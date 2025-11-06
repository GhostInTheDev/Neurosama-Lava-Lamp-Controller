# src/modes/pastel.py
import time
import random


def demo_pastel_mode(lamp, duration=30, interval=2.0):
    """Demo: Soft pastel colors"""
    print("\n" + "="*60)
    print("🌸 DEMO: Pastel Mode (Soft Colors)")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        h = random.randint(0, 360)
        s = random.randint(200, 500)
        v = random.randint(700, 1000)
        lamp.set_color_hsv(h, s, v)
        time.sleep(interval)