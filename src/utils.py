# src/utils.py
import colorsys
import re


class InvalidHexError(Exception):
    """Custom exception for invalid hex codes."""
    pass


def hex_to_hsv(hex_color: str) -> dict:
    """
    Convert #RRGGBB to standard HSV dictionary (h: 0-360, s: 0-1000, v: 0-1000).
    """
    hex_color = hex_color.lstrip('#')
    if not re.fullmatch(r'^[0-9a-fA-F]{6}$', hex_color):
        raise InvalidHexError(f"Invalid hex color format: {hex_color}")
        
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    
    return {
        'h': int(h * 360),
        's': int(s * 1000),
        'v': int(v * 1000)
    }

def hsv_to_tuya(h: int, s: int, v: int) -> str:
    """
    Convert HSV (h: 0-360, s: 0-1000, v: 0-1000) to Tuya color data string.
    Format: hhhhssssvvvv (4-char hex for each component).
    """
    return f"{h:04x}{s:04x}{v:04x}"

def rgb_to_tuya_hsv(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Convert RGB (0-255) to Tuya HSV components (0-360, 0-1000, 0-1000)."""
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h_tuya = int(h * 360)
    s_tuya = int(s * 1000)
    v_tuya = int(v * 1000)
    return h_tuya, s_tuya, v_tuya
    
def _hsv_to_hex_display(h: int, s: int, v: int) -> str:
    """Helper to convert Tuya HSV back to hex for display/status reporting."""
    r, g, b = colorsys.hsv_to_rgb(h/360, s/1000, v/1000)
    return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"