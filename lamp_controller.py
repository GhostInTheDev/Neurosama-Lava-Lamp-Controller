#!/usr.bin/env python3
"""
===============================================
NEURO LAVA LAMP CONTROLLER - Main Entry Point
===============================================
"""

import sys
import argparse
import struct
import time # Import struct and time for quick commands
from src.controller import LavaLampController
from src.cli import interactive_mode
from src.gui import start_web_interface
from src.config import DEVICE_ID, LOCAL_KEY, DEVICE_IP, DEVICE_VERSION # IMPORTED credentials from config.py

# --- Helper function used for building the scene string ---
def _build_music_scene_string(colors, duration=60):
    """
    Builds the definitive cycling scene string based on the captured music mode format:
    [ID=00][Count][Mode=01][Pad=00][Duration (2-byte)][Color Data (6 bytes each)]
    """
    scene = bytearray()
    
    scene.append(0x00)  # ID/Version
    scene.append(len(colors))  # Color count (e.g., 0x02 for 2 colors)
    scene.append(0x01)  # Mode: 0x01 is the magic byte for JUMP/MUSIC cycling!
    scene.append(0x00)  # Padding/Flags
    
    # Duration (in 0.1s units)
    duration_units = min(duration * 10, 65535)
    scene.extend(struct.pack('>H', duration_units))
    
    # Colors (HSV, 2 bytes each, Big Endian)
    for h, s, v in colors:
        scene.extend(struct.pack('>H', h))
        scene.extend(struct.pack('>H', s))
        scene.extend(struct.pack('>H', v))
    
    return scene.hex()

def _sync_stream_quick_command(lamp):
    """Activates the single-command 'Sync to Stream' mode for CLI/Quick use."""
    
    colors = [(0, 1000, 1000)] # Use a single color for the minimal payload
    scene_hex = _build_music_scene_string(colors)

    try:
        lamp.set_mode('music') 
        time.sleep(0.5)
        lamp.set_scene_raw(scene_hex)
        time.sleep(0.5)
        lamp.set_music_toggle(True)
        print("✅ Stream Sync activated.")
    except Exception as e:
        print(f"❌ Failed to activate sync: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Control your Neuro Lava Lamp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                              # Interactive CLI mode
  python main.py --gui                        # Web interface mode (accessible via network)
  python main.py --port 8080                  # Web interface on custom port
  python main.py sync                         # Activate Stream Sync mode
  python main.py #FF0000                      # Set specific color
        """
    )
    
    parser.add_argument('--gui', action='store_true',
                        help='Start web interface instead of CLI')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port for web interface (default: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', # <-- CRITICAL CHANGE: Listen on all interfaces
                        help='Host for web interface (default: 0.0.0.0)')
    parser.add_argument('command', nargs='?', default=None,
                        help='Quick command: sync, rainbow, party, etc., or #RRGGBB')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🔮 NEURO LAVA LAMP CONTROLLER")
    print("="*60 + "\n")
    
    try:
        # Initialize lamp controller using imported credentials
        lamp = LavaLampController(
            device_id=DEVICE_ID,
            local_key=LOCAL_KEY,
            device_ip=DEVICE_IP,
            version=DEVICE_VERSION
        )
        
        # Start web interface mode
        if args.gui:
            print(f"🌐 Starting web interface on http://{args.host}:{args.port}")
            start_web_interface(lamp, host=args.host, port=args.port)
            return
        
        # Quick command mode
        if args.command:
            from src.modes import all_modes
            
            cmd = args.command.lower()
            
            if cmd == 'sync': # Handle the new 'sync' quick command
                _sync_stream_quick_command(lamp)
            
            elif cmd == 'demo':
                # Run all demos
                for mode_name in ['basic_colors', 'rainbow', 'random_rainbow']:
                    if mode_name in all_modes:
                        all_modes[mode_name](lamp, duration=10)
            
            elif cmd in all_modes:
                # Run specific mode
                all_modes[cmd](lamp)
            
            elif args.command.startswith('#'):
                # Set specific color
                lamp.turn_on()
                lamp.set_color_hex(args.command)
            
            else:
                print(f"❌ Unknown command: {cmd}")
                print("\nAvailable commands:")
                for mode_name in all_modes.keys():
                    print(f"  - {mode_name}")
                return
        
        else:
            # Interactive CLI mode
            interactive_mode(lamp)
        
        print("\n✅ Done!")
        
    except KeyboardInterrupt:
        print("\n\n✅ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()