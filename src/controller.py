import time
import tinytuya
from src.utils import hex_to_hsv, hsv_to_tuya, rgb_to_tuya_hsv, InvalidHexError, _hsv_to_hex_display

# --- Tuya Data Point (DP) IDs (Based on your working script: 20=switch, 21=mode) ---
DP_ID_SWITCH = 20        # Boolean: True (on), False (off)
DP_ID_MODE = 21          # String: 'colour', 'white', 'scene', 'music'
DP_ID_COLOR = 24        # String: HSB/HSV color data string (e.g., '008503e803e8')
# ---------------------------------


class LavaLampController:
    """
    Controls the physical lava lamp, communicating with a Tuya-compatible device.
    Implements all color setting and status retrieval methods required by CLI/GUI.
    """
    
    def __init__(self, device_id: str, local_key: str, device_ip: str, version: float):
        """Initializes the Tuya device object and attempts connection."""
        print(f"🔌 Connecting to Tuya device at {device_ip}...")
        
        self._device = tinytuya.Device(
            dev_id=device_id,
            address=device_ip,
            local_key=local_key,
            version=version
        )
        self._device.set_socketTimeout(5) # Set timeout from your working script
        self._is_connected = False
        self._last_status = {}
        
        # Disable Tuya debug logs unless needed
        tinytuya.set_debug(False)
        
        try:
            # Check status to ensure the connection is live and get initial state
            self._last_status = self._device.status()
            if self._last_status is None:
                 raise ConnectionError("Failed to get initial status from device.")
            
            self._is_connected = True
            is_on = self._last_status.get('dps', {}).get(DP_ID_SWITCH)
            print(f"✅ Connection established. Lamp is currently {'ON' if is_on else 'OFF'}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not connect to Tuya device. Running in simulation mode. Error: {e}")
            self._device = None
            # Initialize simulation status to provide default values
            self._last_status = {
                DP_ID_SWITCH: False,
                DP_ID_MODE: 'colour',
                DP_ID_COLOR: '000003e803e8' # Default white 
            } 

        
    def _set_dp_value(self, dp_id: int, value):
        """Helper to send a command to the device."""
        if self._device is None:
            # Simulation mode: update internal status for reporting
            self._last_status.setdefault('dps', {})[dp_id] = value
            return 
        
        try:
            self._device.set_value(dp_id, value, nowait=True)
            time.sleep(0.3) # Wait required by your working script for stability
        except Exception as e:
            print(f"❌ Failed to send DP {dp_id} command: {e}")


    def turn_on(self):
        """Turns the lamp on and ensures it's in 'colour' mode."""
        self._set_dp_value(DP_ID_SWITCH, True)
        self._set_dp_value(DP_ID_MODE, 'colour')
        print("💡 Lamp turned ON")


    def turn_off(self):
        """Turns the lamp off."""
        self._set_dp_value(DP_ID_SWITCH, False)
        print("🛑 Lamp turned OFF")

    
    def set_color_hex(self, hex_color: str, brightness: int = 100):
        """Sets color using HEX code (e.g., #FF0000)."""
        try:
            hsv = hex_to_hsv(hex_color)
            
            # Apply external brightness control (0-100) to V component
            v_scaled = int((brightness / 100) * 1000)
            v_tuya = max(1, min(1000, v_scaled)) 
            
            self.set_color_hsv(hsv['h'], hsv['s'], v_tuya)
            print(f"✨ Set color (HEX) to {hex_color} @ {brightness}%")
            
        except InvalidHexError as e:
            print(f"❌ Error setting color: {e}")


    def set_color_rgb(self, r: int, g: int, b: int, brightness: int = 100):
        """Sets color using RGB values (0-255)."""
        try:
            # Convert RGB (0-255) to Tuya HSB/HSV components
            h, s, v_max = rgb_to_tuya_hsv(r, g, b)
            
            # Apply brightness scale
            v_scaled = int((brightness / 100) * 1000)
            v_tuya = max(1, min(1000, v_scaled))
            
            self.set_color_hsv(h, s, v_tuya)
            print(f"✨ Set color (RGB) to R:{r} G:{g} B:{b} @ {brightness}%")
            
        except Exception as e:
            print(f"❌ Failed to process RGB command: {e}")


    def set_color_hsv(self, h: int, s: int, v: int):
        """
        Sets color using Tuya-native HSB/HSV values.
        h: 0-360, s: 0-1000, v: 0-1000 (V represents absolute brightness/value)
        """
        try:
            # Format the HSB string (e.g., '008503e803e8') and send
            tuya_color_string = hsv_to_tuya(h, s, v)
            
            # Ensure mode is 'colour' before sending color data
            self._set_dp_value(DP_ID_MODE, 'colour')
            
            # Send the color data on DP 24
            self._set_dp_value(DP_ID_COLOR, tuya_color_string)
            
            hex_color_display = _hsv_to_hex_display(h, s, v)
            print(f"🎨 Set color (HSV) to H:{h} S:{s} V:{v} ({hex_color_display})")
            
        except Exception as e:
            print(f"❌ Failed to send HSV command: {e}")


    def get_status(self) -> str:
        """
        Fetches and formats the current lamp status for display in the CLI.
        """
        if self._device is None:
            status_text = "Status: OFFLINE (Running in simulation mode)\n"
            status_text += f"Last Known State (DPS): {self._last_status.get('dps', {})}"
            return status_text

        try:
            # Refresh status from device
            current_status = self._device.status()
            if not current_status:
                return "Status: Error retrieving status (Device Unreachable)."
            
            dps_raw = current_status.get('dps', {})
            
            # CRITICAL FIX: Convert raw DP keys (which are often strings like '20') to integers
            dps = {int(k): v for k, v in dps_raw.items() if isinstance(k, str) and k.isdigit()}
            self._last_status = dps # Store the cleaned, integer-keyed dictionary
            
            is_on = dps.get(DP_ID_SWITCH, False)
            mode = dps.get(DP_ID_MODE, 'unknown')
            color_str = dps.get(DP_ID_COLOR, 'N/A')
            
            # Decode the HSB string if available (format is hex hhhhssssvvvv)
            h, s, v = "N/A", "N/A", "N/A"
            hex_display = "N/A"
            if len(color_str) == 12:
                try:
                    # Parse the 4-char hex strings
                    h = int(color_str[0:4], 16)
                    s = int(color_str[4:8], 16)
                    v = int(color_str[8:12], 16)
                    hex_display = _hsv_to_hex_display(h, s, v)
                except ValueError:
                    pass
            
            output = f"Status: {'ON' if is_on else 'OFF'}\n"
            output += f"Mode: {mode.upper()}\n"
            output += f"Color (HSV/Tuya): H={h}, S={s}, V={v} (V=Brightness)\n"
            output += f"Raw DPS: {dps}"
            
            return output
            
        except Exception as e:
            return f"Status: Error fetching device data. {e}"