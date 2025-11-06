# src/modes/rainbow.py
import time
import random


def demo_rainbow(lamp, duration=None):
    """Demo: Smooth rainbow transition"""
    print("\n" + "="*60)
    print("🌈 DEMO: Rainbow Cycle (Smooth)")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    for h in range(0, 360, 5):
        lamp.set_color_hsv(h, 1000, 1000)
        time.sleep(0.1)


def demo_random_rainbow(lamp, duration=30, interval=1.0):
    """Demo: Random vibrant colors"""
    print("\n" + "="*60)
    print("🎲 DEMO: Random Rainbow")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        h = random.randint(0, 360)
        s = random.randint(800, 1000)
        v = random.randint(800, 1000)
        lamp.set_color_hsv(h, s, v)
        time.sleep(interval)