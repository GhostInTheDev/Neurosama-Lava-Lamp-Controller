# src/modes/utility.py
import time


def demo_breathing(lamp, color="#FF0000", cycles=3, duration=None):
    """Demo: Breathing effect"""
    from src.utils import hex_to_hsv
    
    print("\n" + "="*60)
    print("💨 DEMO: Breathing Effect")
    print("="*60 + "\n")
    
    lamp.turn_on()
    hsv = hex_to_hsv(color)
    
    for _ in range(cycles):
        for v in range(100, 1001, 50):
            lamp.set_color_hsv(hsv['h'], hsv['s'], v)
            time.sleep(0.05)
        for v in range(1000, 99, -50):
            lamp.set_color_hsv(hsv['h'], hsv['s'], v)
            time.sleep(0.05)


def demo_strobe(lamp, color="#FFFFFF", duration=5):
    """Demo: Strobe effect"""
    print("\n" + "="*60)
    print("⚡ DEMO: Strobe Effect")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_color_hex(color, brightness=100)
    
    start = time.time()
    while time.time() - start < duration:
        lamp.turn_off()
        time.sleep(0.1)
        lamp.turn_on()
        lamp.set_color_hex(color, brightness=100)
        time.sleep(0.1)


def demo_police_lights(lamp, duration=30):
    """Demo: Police siren (red/blue alternating)"""
    print("\n" + "="*60)
    print("🚨 DEMO: Police Lights")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        lamp.set_color_hsv(0, 1000, 1000)
        time.sleep(0.3)
        lamp.set_color_hsv(240, 1000, 1000)
        time.sleep(0.3)