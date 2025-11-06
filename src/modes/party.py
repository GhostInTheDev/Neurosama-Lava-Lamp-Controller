# src/modes/party.py
import time
import random


def demo_party_mode(lamp, duration=30):
    """Demo: Super fast random flashing (party mode)"""
    print("\n" + "="*60)
    print("🎉 DEMO: Party Mode (Fast Random Flash)")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        h = random.randint(0, 360)
        s = 1000
        v = 1000
        lamp.set_color_hsv(h, s, v)
        time.sleep(random.uniform(0.05, 0.2))