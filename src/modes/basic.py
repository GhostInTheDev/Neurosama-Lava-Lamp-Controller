# src/modes/basic.py
import time


def demo_basic_colors(lamp, duration=None):
    """Demo: Cycle through basic colors"""
    print("\n" + "="*60)
    print("🌈 DEMO: Basic Colors")
    print("="*60 + "\n")
    
    colors = [
        ("#FF0000", "Red"),
        ("#00FF00", "Green"),
        ("#0000FF", "Blue"),
        ("#FFFF00", "Yellow"),
        ("#FF00FF", "Magenta"),
        ("#00FFFF", "Cyan"),
        ("#FFFFFF", "White"),
    ]
    
    lamp.turn_on()
    for hex_color, name in colors:
        print(f"→ {name}")
        lamp.set_color_hex(hex_color, brightness=100)
        time.sleep(1.5)