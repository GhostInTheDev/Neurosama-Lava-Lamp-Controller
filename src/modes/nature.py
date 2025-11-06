# src/modes/nature.py
import time
import random


def demo_fire_effect(lamp, duration=30):
    """Demo: Fire effect (reds, oranges, yellows)"""
    print("\n" + "="*60)
    print("🔥 DEMO: Fire Effect")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        h = random.randint(0, 60)
        s = random.randint(800, 1000)
        v = random.randint(600, 1000)
        lamp.set_color_hsv(h, s, v)
        time.sleep(random.uniform(0.1, 0.3))


def demo_ocean_effect(lamp, duration=30):
    """Demo: Ocean effect (blues and greens)"""
    print("\n" + "="*60)
    print("🌊 DEMO: Ocean Effect")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        h = random.randint(150, 240)
        s = random.randint(600, 1000)
        v = random.randint(500, 900)
        lamp.set_color_hsv(h, s, v)
        time.sleep(random.uniform(0.5, 2.0))


def demo_sunset_mode(lamp, duration=30):
    """Demo: Sunset colors (purples, pinks, oranges)"""
    print("\n" + "="*60)
    print("🌅 DEMO: Sunset Mode")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        color_ranges = [(270, 300), (320, 340), (10, 40)]
        h_range = random.choice(color_ranges)
        h = random.randint(h_range[0], h_range[1])
        s = random.randint(700, 1000)
        v = random.randint(600, 900)
        lamp.set_color_hsv(h, s, v)
        time.sleep(random.uniform(1.0, 3.0))