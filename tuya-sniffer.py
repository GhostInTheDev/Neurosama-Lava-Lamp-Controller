#!/usr/bin/env python3
"""
===============================================
TUYA DEVICE NETWORK SNIFFER (Pentest Tool)
Captures and analyzes Tuya device traffic
===============================================
"""

import socket
import struct
import json
import binascii
from datetime import datetime
from scapy.all import sniff, UDP, IP, Raw
from Crypto.Cipher import AES
import hashlib

# ===============================================
# CONFIGURATION
# ===============================================
TARGET_IP = None  # Set to lamp's IP if known, or None to capture all
TUYA_PORTS = [6666, 6667, 6668]
INTERFACE = None  # None = all interfaces, or specify like "eth0", "wlan0"

# Known Tuya protocol constants
TUYA_PROTOCOL_VERSION = b'3.3'
TUYA_MESSAGE_TYPES = {
    0x00: "UDP_NEW",
    0x01: "AP_CONFIG",
    0x02: "ACTIVE",
    0x03: "BIND",
    0x04: "RENAME_GW",
    0x05: "RENAME_DEVICE",
    0x06: "UNBIND",
    0x07: "CONTROL",
    0x08: "STATUS",
    0x09: "HEART_BEAT",
    0x0a: "DP_QUERY",
    0x0d: "QUERY_WIFI",
    0x0e: "TOKEN_BIND",
    0x0f: "CONTROL_NEW",
    0x10: "ENABLE_WIFI",
    0x12: "DP_QUERY_NEW",
    0x13: "SCENE_EXECUTE",
    0x14: "UDP_NEW_V2",
}

# ===============================================
# TUYA PROTOCOL PARSER
# ===============================================
class TuyaParser:
    @staticmethod
    def parse_packet(data):
        """Parse Tuya packet structure"""
        if len(data) < 24:
            return None
        
        try:
            # Tuya packet structure:
            # 0000000: prefix (4 bytes) - usually 0x000055AA
            # 0000004: sequence_nr (4 bytes)
            # 0000008: command (4 bytes)
            # 000000c: length (4 bytes)
            # 0000010: return_code (4 bytes)
            # 0000014: data (variable)
            # .......: crc (4 bytes)
            # .......: suffix (4 bytes) - usually 0x0000AA55
            
            prefix = struct.unpack(">I", data[0:4])[0]
            if prefix != 0x000055AA:
                return None
            
            seq_nr = struct.unpack(">I", data[4:8])[0]
            cmd = struct.unpack(">I", data[8:12])[0]
            length = struct.unpack(">I", data[12:16])[0]
            
            result = {
                "prefix": hex(prefix),
                "sequence": seq_nr,
                "command": cmd,
                "command_name": TUYA_MESSAGE_TYPES.get(cmd, f"UNKNOWN_{hex(cmd)}"),
                "length": length,
                "raw": binascii.hexlify(data).decode()
            }
            
            if length > 0 and len(data) >= 16 + length:
                payload = data[16:16+length]
                result["payload_hex"] = binascii.hexlify(payload).decode()
                
                # Try to parse as JSON (if unencrypted)
                try:
                    payload_str = payload.decode('utf-8', errors='ignore')
                    if payload_str.startswith('{'):
                        result["payload_json"] = json.loads(payload_str)
                except:
                    pass
                
                # Check for encrypted data (starts with version)
                if payload.startswith(b'3.'):
                    result["encrypted"] = True
                    result["version"] = payload[:3].decode()
            
            return result
            
        except Exception as e:
            return {"error": str(e), "raw": binascii.hexlify(data).decode()}

    @staticmethod
    def try_decrypt(encrypted_data, local_key):
        """Attempt to decrypt Tuya payload with a local key"""
        if not local_key:
            return None
        
        try:
            # Tuya encryption: AES-128-ECB with MD5 hash of local key
            key = local_key.encode() if isinstance(local_key, str) else local_key
            cipher = AES.new(hashlib.md5(key).digest(), AES.MODE_ECB)
            
            # Remove version prefix if present
            if encrypted_data.startswith(b'3.'):
                encrypted_data = encrypted_data[3:]
            
            decrypted = cipher.decrypt(encrypted_data)
            # Remove PKCS7 padding
            padding_len = decrypted[-1]
            decrypted = decrypted[:-padding_len]
            
            return json.loads(decrypted.decode())
        except Exception as e:
            return None

# ===============================================
# PACKET SNIFFER
# ===============================================
class TuyaSniffer:
    def __init__(self):
        self.parser = TuyaParser()
        self.packet_count = 0
        self.devices_seen = set()
        
    def packet_callback(self, packet):
        """Process each captured packet"""
        if not packet.haslayer(UDP):
            return
        
        udp_layer = packet[UDP]
        ip_layer = packet[IP]
        
        # Filter for Tuya ports
        if udp_layer.dport not in TUYA_PORTS and udp_layer.sport not in TUYA_PORTS:
            return
        
        # Filter for target IP if specified
        if TARGET_IP and ip_layer.src != TARGET_IP and ip_layer.dst != TARGET_IP:
            return
        
        self.packet_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Track devices
        device_ip = ip_layer.src if udp_layer.sport in TUYA_PORTS else ip_layer.dst
        self.devices_seen.add(device_ip)
        
        print(f"\n{'='*60}")
        print(f"[{timestamp}] PACKET #{self.packet_count}")
        print(f"{'='*60}")
        print(f"Source:      {ip_layer.src}:{udp_layer.sport}")
        print(f"Destination: {ip_layer.dst}:{udp_layer.dport}")
        print(f"Length:      {len(udp_layer.payload)} bytes")
        
        # Parse Tuya protocol
        if packet.haslayer(Raw):
            payload = bytes(packet[Raw].load)
            parsed = self.parser.parse_packet(payload)
            
            if parsed:
                print(f"\n--- TUYA PROTOCOL ---")
                print(f"Command:     {parsed.get('command_name', 'UNKNOWN')} ({parsed.get('command', '?')})")
                print(f"Sequence:    {parsed.get('sequence', '?')}")
                
                if "payload_json" in parsed:
                    print(f"\n--- DECRYPTED PAYLOAD ---")
                    print(json.dumps(parsed["payload_json"], indent=2))
                    
                    # Check for color data
                    if "dps" in parsed["payload_json"]:
                        dps = parsed["payload_json"]["dps"]
                        if "24" in dps:
                            print(f"\n🎨 COLOR DATA DETECTED: {dps['24']}")
                        if "21" in dps:
                            print(f"   Mode: {dps['21']}")
                
                elif "payload_hex" in parsed:
                    print(f"\n--- ENCRYPTED/RAW PAYLOAD ---")
                    print(f"Hex: {parsed['payload_hex'][:100]}{'...' if len(parsed['payload_hex']) > 100 else ''}")
                    
                    if parsed.get("encrypted"):
                        print(f"⚠️  ENCRYPTED (version {parsed.get('version')})")
                        print(f"💡 Need local key to decrypt")
                
                # Print full raw packet for analysis
                print(f"\n--- RAW PACKET (first 200 bytes) ---")
                print(f"{parsed.get('raw', '')[:400]}")
            else:
                # Not a Tuya packet, just show raw data
                print(f"\n--- RAW UDP DATA ---")
                print(f"{binascii.hexlify(payload)[:200].decode()}")
    
    def start(self):
        """Start sniffing"""
        filter_str = f"udp and (port {' or port '.join(map(str, TUYA_PORTS))})"
        if TARGET_IP:
            filter_str += f" and host {TARGET_IP}"
        
        print("="*60)
        print("🔍 TUYA DEVICE NETWORK SNIFFER")
        print("="*60)
        print(f"Target IP:    {TARGET_IP or 'ALL (will capture all Tuya traffic)'}")
        print(f"Monitoring:   UDP ports {TUYA_PORTS}")
        print(f"Interface:    {INTERFACE or 'ALL'}")
        print(f"Filter:       {filter_str}")
        print("\n⚡ Starting capture... (Press Ctrl+C to stop)\n")
        
        try:
            sniff(
                filter=filter_str,
                prn=self.packet_callback,
                store=0,
                iface=INTERFACE
            )
        except PermissionError:
            print("\n❌ ERROR: Need root/admin privileges to capture packets!")
            print("   Run with: sudo python3 tuya_sniffer.py")
        except KeyboardInterrupt:
            print("\n\n" + "="*60)
            print("📊 CAPTURE SUMMARY")
            print("="*60)
            print(f"Total packets: {self.packet_count}")
            print(f"Devices seen:  {len(self.devices_seen)}")
            for ip in self.devices_seen:
                print(f"  - {ip}")
            print("\n✅ Capture stopped.")

# ===============================================
# ADDITIONAL TOOLS
# ===============================================
def find_tuya_devices():
    """Scan local network for Tuya devices"""
    print("🔎 Scanning for Tuya devices on local network...")
    print("   (This uses ARP + UDP broadcast)")
    
    # Send UDP broadcast to Tuya discovery port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    # Tuya discovery packet
    discovery = b'\x00\x00\x55\xaa\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xaa\x55'
    
    try:
        sock.sendto(discovery, ('255.255.255.255', 6666))
        sock.sendto(discovery, ('255.255.255.255', 6667))
        sock.settimeout(3)
        
        devices = []
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                devices.append(addr[0])
                print(f"   Found: {addr[0]}")
        except socket.timeout:
            pass
        
        if devices:
            print(f"\n✅ Found {len(devices)} potential Tuya device(s)")
            return devices
        else:
            print("\n⚠️  No Tuya devices responded to broadcast")
            return []
    except Exception as e:
        print(f"❌ Error during scan: {e}")
        return []
    finally:
        sock.close()

# ===============================================
# MAIN
# ===============================================
if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("  TUYA PENTEST TOOL - Network Traffic Analyzer")
    print("="*60 + "\n")
    
    # Optional: Scan for devices first
    if "--scan" in sys.argv:
        devices = find_tuya_devices()
        if devices and len(devices) == 1:
            TARGET_IP = devices[0]
            print(f"\n→ Will monitor traffic from: {TARGET_IP}")
        input("\nPress Enter to start sniffing...")
    
    # Check for target IP argument
    if len(sys.argv) > 1 and sys.argv[1] not in ["--scan"]:
        TARGET_IP = sys.argv[1]
    
    # Start sniffer
    sniffer = TuyaSniffer()
    sniffer.start()
