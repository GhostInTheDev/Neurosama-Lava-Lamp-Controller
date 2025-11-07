import time
import tinytuya
from src.utils import hex_to_hsv, hsv_to_tuya, rgb_to_tuya_hsv, InvalidHexError, _hsv_to_hex_display

# --- Tuya Data Point (DP) IDs (Based on your working script: 20=switch, 21=mode) ---
DP_ID_SWITCH = 20        # Boolean: True (on), False (off)
DP_ID_MODE = 21          # String: 'colour', 'white', 'scene', 'music'
DP_ID_COLOR = 24         # String: HSB/HSV color data string (e.g., '008503e803e8')
DP_ID_SCENE = 25         # String: Scene data
DP_ID_MUSIC_TOGGLE = 27  # NEW: Hypothesized toggle for Music/Sync mode activation
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
        self._device.set_socketTimeout(5)
        self._is_connected = False
        self._last_status = {}
        
        tinytuya.set_debug(False)
        
        try:
            self._last_status = self._device.status()
            if self._last_status is None:
                 raise ConnectionError("Failed to get initial status from device.")
            
            self._is_connected = True
            is_on = self._last_status.get('dps', {}).get(str(DP_ID_SWITCH))
            print(f"✅ Connection established. Lamp is currently {'ON' if is_on else 'OFF'}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not connect to Tuya device. Running in simulation mode. Error: {e}")
            self._device = None
            self._last_status = {'dps': {str(DP_ID_SWITCH): False, str(DP_ID_MODE): 'colour', str(DP_ID_COLOR): '000003e803e8'}} 

        
    def _set_dp_value(self, dp_id: int, value):
        """Helper to send a command to the device."""
        if self._device is None:
            self._last_status.setdefault('dps', {})[str(dp_id)] = value
            return 
        
        try:
            self._device.set_value(dp_id, value, nowait=True)
            time.sleep(0.3)
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

    
    def set_mode(self, mode: str):
        """Sets the work mode (DPS 21)."""
        valid_modes = ['colour', 'white', 'scene', 'music']
        if mode not in valid_modes:
            print(f"❌ Invalid mode '{mode}'. Must be one of: {', '.join(valid_modes)}.")
            return

        self._set_dp_value(DP_ID_MODE, mode)
        print(f"🎭 Lamp mode set to {mode.upper()}")
    
    
    def set_music_toggle(self, state: bool):
        """NEW: Toggles the music/sync start flag (DPS 27)."""
        self._set_dp_value(DP_ID_MUSIC_TOGGLE, state)
        print(f"⏯️  Sent DPS {DP_ID_MUSIC_TOGGLE} (Music Toggle): {state}")


    def set_scene_raw(self, scene_hex: str):
        """Sends raw scene data string to DPS 25."""
        self._set_dp_value(DP_ID_SCENE, scene_hex)
        print(f"🖼️ Raw scene data sent to DPS {DP_ID_SCENE}.")

    # (Other methods like set_color_hex, get_status, etc., are omitted for brevity but remain unchanged)

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
            self.set_mode('colour') # Use the new method
            
            # Send the color data on DP 24
            self._set_dp_value(DP_ID_COLOR, tuya_color_string)
            
            hex_color_display = _hsv_to_hex_display(h, s, v)
            print(f"🎨 Set color (HSV) to H:{h} S:{s} V:{v} ({hex_color_display})")
            
        except Exception as e:
            print(f"❌ Failed to send HSV command: {e}")


    def get_status(self) -> dict:
        """
        Fetches and returns the current lamp status as a dictionary.
        NOTE: Returns the raw DPS dictionary for deep analysis.
        """
        if self._device is None:
            # Return simulation status
            return self._last_status.get('dps', {})
        
        try:
            # Refresh status from device
            current_status = self._device.status()
            if not current_status:
                return {}
            
            dps_raw = current_status.get('dps', {})
            
            # Store the raw dictionary
            self._last_status = dps_raw 
            
            return dps_raw
            
        except Exception:
            return {}