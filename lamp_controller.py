#!/usr/bin/env python3
"""
===============================================
TUYA LAMP COLOR CONTROLLER
Send colors directly to the Neuro Lava Lamp
===============================================
"""

import tinytuya
import colorsys
import time
import sys
from datetime import datetime, timedelta
import threading

# ===============================================
# DEVICE CREDENTIALS
# ===============================================
DEVICE_ID = "device_id_from_logs"
LOCAL_KEY = "NDzeP/yOu?>o:8(2"
DEVICE_IP = "your-lamp-ip-here"
DEVICE_VERSION = 3.5

# ===============================================
# Color Conversion Functions
# ===============================================
def hex_to_hsv(hex_color):
    """Convert #RRGGBB to HSV (h: 0-360, s: 0-1000, v: 0-1000)"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    return {
        'h': int(h * 360),
        's': int(s * 1000),
        'v': int(v * 1000)
    }

def hsv_to_tuya(h, s, v):
    """Convert HSV to Tuya color data string
    h: 0-360 degrees
    s: 0-1000
    v: 0-1000
    Returns: 12-char hex string like '008503e803e8'
    """
    return f"{h:04x}{s:04x}{v:04x}"

def rgb_to_tuya(r, g, b):
    """Convert RGB (0-255) to Tuya color data"""
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h_tuya = int(h * 360)
    s_tuya = int(s * 1000)
    v_tuya = int(v * 1000)
    return hsv_to_tuya(h_tuya, s_tuya, v_tuya)

# ===============================================
# Device Control Class
# ===============================================
class LavaLampController:
    def __init__(self):
        print("🔌 Connecting to Neuro Lava Lamp...")
        self.device = tinytuya.Device(
            dev_id=DEVICE_ID,
            address=DEVICE_IP,
            local_key=LOCAL_KEY,
            version=DEVICE_VERSION
        )
        self.device.set_socketTimeout(5)
        
        # Test connection
        status = self.device.status()
        if 'Error' in status:
            raise Exception(f"Connection failed: {status['Error']}")
        print("✅ Connected!\n")
    
    def turn_on(self):
        """Turn lamp on"""
        print("💡 Turning lamp ON...")
        self.device.set_value(20, True)
        time.sleep(0.3)
    
    def turn_off(self):
        """Turn lamp off"""
        print("💡 Turning lamp OFF...")
        self.device.set_value(20, False)
        time.sleep(0.3)
    
    def set_mode(self, mode='colour'):
        """Set work mode: 'white', 'colour', 'scene', 'music'"""
        print(f"🎭 Setting mode to: {mode}")
        self.device.set_value(21, mode)
        time.sleep(0.3)
    
    def set_color_hex(self, hex_color, brightness=100):
        """Set color using hex (#RRGGBB)"""
        hsv = hex_to_hsv(hex_color)
        # Adjust brightness
        hsv['v'] = int((brightness / 100) * 1000)
        self.set_color_hsv(hsv['h'], hsv['s'], hsv['v'])
    
    def set_color_rgb(self, r, g, b, brightness=100):
        """Set color using RGB (0-255)"""
        color_data = rgb_to_tuya(r, g, b)
        # Adjust brightness
        v = int((brightness / 100) * 1000)
        h, s = int(color_data[:4], 16), int(color_data[4:8], 16)
        color_data = hsv_to_tuya(h, s, v)
        
        print(f"🎨 Setting color: RGB({r}, {g}, {b}) @ {brightness}%")
        self.device.set_value(21, 'colour')
        time.sleep(0.1)
        self.device.set_value(24, color_data)
        time.sleep(0.3)
    
    def set_color_hsv(self, h, s, v):
        """Set color using HSV (h: 0-360, s: 0-1000, v: 0-1000)"""
        color_data = hsv_to_tuya(h, s, v)
        hex_color = self._hsv_to_hex_display(h, s, v)
        print(f"🎨 Setting color: HSV({h}°, {s/10}%, {v/10}%) = {hex_color}")
        
        self.device.set_value(21, 'colour')
        time.sleep(0.1)
        self.device.set_value(24, color_data)
        time.sleep(0.3)
    
    def _hsv_to_hex_display(self, h, s, v):
        """Convert Tuya HSV to hex for display"""
        r, g, b = colorsys.hsv_to_rgb(h/360, s/1000, v/1000)
        return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"
    
    def get_status(self):
        """Get current lamp status"""
        return self.device.status()

# ===============================================
# Demo Functions
# ===============================================
def demo_basic_colors(lamp):
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

def demo_rainbow(lamp):
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
    import random
    
    print("\n" + "="*60)
    print("🎲 DEMO: Random Rainbow")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        # Random hue (full spectrum)
        h = random.randint(0, 360)
        # Keep saturation and value high for vibrant colors
        s = random.randint(800, 1000)
        v = random.randint(800, 1000)
        
        lamp.set_color_hsv(h, s, v)
        time.sleep(interval)

def demo_party_mode(lamp, duration=30):
    """Demo: Super fast random flashing (party mode)"""
    import random
    
    print("\n" + "="*60)
    print("🎉 DEMO: Party Mode (Fast Random Flash)")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        h = random.randint(0, 360)
        s = 1000  # Full saturation
        v = 1000  # Full brightness
        lamp.set_color_hsv(h, s, v)
        time.sleep(random.uniform(0.05, 0.2))  # Fast random timing

def demo_pastel_mode(lamp, duration=30, interval=2.0):
    """Demo: Soft pastel colors"""
    import random
    
    print("\n" + "="*60)
    print("🌸 DEMO: Pastel Mode (Soft Colors)")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        h = random.randint(0, 360)
        s = random.randint(200, 500)  # Low saturation for pastel
        v = random.randint(700, 1000)  # High brightness
        lamp.set_color_hsv(h, s, v)
        time.sleep(interval)

def demo_fire_effect(lamp, duration=30):
    """Demo: Fire effect (reds, oranges, yellows)"""
    import random
    
    print("\n" + "="*60)
    print("🔥 DEMO: Fire Effect")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        # Fire colors: red (0°), orange (30°), yellow (60°)
        h = random.randint(0, 60)
        s = random.randint(800, 1000)
        v = random.randint(600, 1000)  # Flickering brightness
        lamp.set_color_hsv(h, s, v)
        time.sleep(random.uniform(0.1, 0.3))  # Flickering speed

def demo_ocean_effect(lamp, duration=30):
    """Demo: Ocean effect (blues and greens)"""
    import random
    
    print("\n" + "="*60)
    print("🌊 DEMO: Ocean Effect")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        # Ocean colors: cyan (180°), blue (240°), teal/green (150-200°)
        h = random.randint(150, 240)
        s = random.randint(600, 1000)
        v = random.randint(500, 900)  # Gentle waves
        lamp.set_color_hsv(h, s, v)
        time.sleep(random.uniform(0.5, 2.0))  # Slow, wave-like transitions

def demo_sunset_mode(lamp, duration=30):
    """Demo: Sunset colors (purples, pinks, oranges)"""
    import random
    
    print("\n" + "="*60)
    print("🌅 DEMO: Sunset Mode")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        # Sunset colors: purple (270-300°), pink (320-340°), orange (10-40°)
        color_ranges = [(270, 300), (320, 340), (10, 40)]
        h_range = random.choice(color_ranges)
        h = random.randint(h_range[0], h_range[1])
        s = random.randint(700, 1000)
        v = random.randint(600, 900)
        lamp.set_color_hsv(h, s, v)
        time.sleep(random.uniform(1.0, 3.0))

def demo_police_lights(lamp, duration=30):
    """Demo: Police siren (red/blue alternating)"""
    print("\n" + "="*60)
    print("🚨 DEMO: Police Lights")
    print("="*60 + "\n")
    
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        # Red
        lamp.set_color_hsv(0, 1000, 1000)
        time.sleep(0.3)
        # Blue
        lamp.set_color_hsv(240, 1000, 1000)
        time.sleep(0.3)

# ===============================================
# Scheduling Functions
# ===============================================
class LampScheduler:
    """Schedule lamp actions at specific times"""
    
    def __init__(self, lamp):
        self.lamp = lamp
        self.schedules = []
        self.running = False
        self.thread = None
    
    def schedule_on(self, target_time, color="#FFFFFF", brightness=100):
        """Schedule lamp to turn on at a specific time
        
        Args:
            target_time: datetime object or string "HH:MM" or "YYYY-MM-DD HH:MM"
            color: Hex color string (default white)
            brightness: 0-100 (default 100)
        """
        if isinstance(target_time, str):
            target_time = self._parse_time_string(target_time)
        
        self.schedules.append({
            'time': target_time,
            'action': 'on',
            'color': color,
            'brightness': brightness
        })
        print(f"✅ Scheduled: Turn ON at {target_time.strftime('%Y-%m-%d %H:%M:%S')} with color {color}")
    
    def schedule_off(self, target_time):
        """Schedule lamp to turn off at a specific time"""
        if isinstance(target_time, str):
            target_time = self._parse_time_string(target_time)
        
        self.schedules.append({
            'time': target_time,
            'action': 'off'
        })
        print(f"✅ Scheduled: Turn OFF at {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def schedule_effect(self, target_time, effect_name, duration=30):
        """Schedule an effect to run at a specific time
        
        Args:
            target_time: datetime object or string
            effect_name: 'rainbow', 'party', 'fire', 'ocean', etc.
            duration: How long to run the effect (seconds)
        """
        if isinstance(target_time, str):
            target_time = self._parse_time_string(target_time)
        
        self.schedules.append({
            'time': target_time,
            'action': 'effect',
            'effect': effect_name,
            'duration': duration
        })
        print(f"✅ Scheduled: {effect_name} effect at {target_time.strftime('%Y-%m-%d %H:%M:%S')} for {duration}s")
    
    def _parse_time_string(self, time_str):
        """Parse time string to datetime object"""
        now = datetime.now()
        
        # Format: "HH:MM" (today)
        if len(time_str) == 5 and ':' in time_str:
            hour, minute = map(int, time_str.split(':'))
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # If time already passed today, schedule for tomorrow
            if target < now:
                target += timedelta(days=1)
            return target
        
        # Format: "YYYY-MM-DD HH:MM"
        elif len(time_str) == 16:
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        
        # Format: "MM-DD HH:MM" (this year)
        elif len(time_str) == 11:
            return datetime.strptime(f"{now.year}-{time_str}", "%Y-%m-%d %H:%M")
        
        else:
            raise ValueError(f"Invalid time format: {time_str}. Use 'HH:MM' or 'YYYY-MM-DD HH:MM'")
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            print("⚠️  Scheduler already running!")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("🕐 Scheduler started!")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("⏹️  Scheduler stopped!")
    
    def _run_scheduler(self):
        """Background thread that checks schedules"""
        while self.running:
            now = datetime.now()
            
            for schedule in self.schedules[:]:  # Copy list to allow removal
                if now >= schedule['time']:
                    print(f"\n⏰ Executing scheduled action at {now.strftime('%H:%M:%S')}")
                    
                    try:
                        if schedule['action'] == 'on':
                            self.lamp.turn_on()
                            self.lamp.set_color_hex(schedule['color'], schedule['brightness'])
                            print(f"   ✅ Lamp turned ON with color {schedule['color']}")
                        
                        elif schedule['action'] == 'off':
                            self.lamp.turn_off()
                            print(f"   ✅ Lamp turned OFF")
                        
                        elif schedule['action'] == 'effect':
                            effect = schedule['effect']
                            duration = schedule['duration']
                            print(f"   ✅ Running {effect} effect for {duration}s")
                            
                            # Run effect based on name
                            if effect == 'rainbow':
                                demo_rainbow(self.lamp)
                            elif effect == 'random':
                                demo_random_rainbow(self.lamp, duration)
                            elif effect == 'party':
                                demo_party_mode(self.lamp, duration)
                            elif effect == 'fire':
                                demo_fire_effect(self.lamp, duration)
                            elif effect == 'ocean':
                                demo_ocean_effect(self.lamp, duration)
                            elif effect == 'sunset':
                                demo_sunset_mode(self.lamp, duration)
                            elif effect == 'police':
                                demo_police_lights(self.lamp, duration)
                            elif effect == 'pastel':
                                demo_pastel_mode(self.lamp, duration)
                    
                    except Exception as e:
                        print(f"   ❌ Error executing schedule: {e}")
                    
                    # Remove executed schedule
                    self.schedules.remove(schedule)
            
            time.sleep(1)  # Check every second
    
    def list_schedules(self):
        """Show all scheduled actions"""
        if not self.schedules:
            print("📋 No schedules set")
            return
        
        print("\n📋 Scheduled Actions:")
        print("="*60)
        for i, schedule in enumerate(sorted(self.schedules, key=lambda x: x['time']), 1):
            time_str = schedule['time'].strftime('%Y-%m-%d %H:%M:%S')
            if schedule['action'] == 'on':
                print(f"{i}. {time_str} - Turn ON ({schedule['color']} @ {schedule['brightness']}%)")
            elif schedule['action'] == 'off':
                print(f"{i}. {time_str} - Turn OFF")
            elif schedule['action'] == 'effect':
                print(f"{i}. {time_str} - {schedule['effect'].upper()} effect ({schedule['duration']}s)")
        print("="*60 + "\n")
    
    def clear_schedules(self):
        """Clear all schedules"""
        self.schedules.clear()
        print("🗑️  All schedules cleared!")

def schedule_mode(lamp):
    """Interactive scheduling mode"""
    scheduler = LampScheduler(lamp)
    
    print("\n" + "="*60)
    print("🕐 SCHEDULING MODE")
    print("="*60)
    print("\nCommands:")
    print("  on <time> <color>     - Schedule turn on (e.g., on 14:30 #FF0000)")
    print("  off <time>            - Schedule turn off (e.g., off 22:00)")
    print("  effect <time> <name>  - Schedule effect (e.g., effect 18:00 fire)")
    print("  list                  - Show all schedules")
    print("  clear                 - Clear all schedules")
    print("  start                 - Start scheduler (run in background)")
    print("  stop                  - Stop scheduler")
    print("  back                  - Return to main menu")
    print("\nTime formats: 'HH:MM' or 'YYYY-MM-DD HH:MM'")
    print("Available effects: rainbow, random, party, fire, ocean, sunset, police, pastel\n")
    
    while True:
        try:
            cmd = input("schedule> ").strip().split()
            if not cmd:
                continue
            
            if cmd[0] == 'back':
                if scheduler.running:
                    print("⚠️  Scheduler is still running in background!")
                break
            elif cmd[0] == 'on' and len(cmd) >= 2:
                time_str = cmd[1]
                color = cmd[2] if len(cmd) > 2 else "#FFFFFF"
                scheduler.schedule_on(time_str, color)
            elif cmd[0] == 'off' and len(cmd) >= 2:
                time_str = cmd[1]
                scheduler.schedule_off(time_str)
            elif cmd[0] == 'effect' and len(cmd) >= 3:
                time_str = cmd[1]
                effect = cmd[2]
                duration = int(cmd[3]) if len(cmd) > 3 else 30
                scheduler.schedule_effect(time_str, effect, duration)
            elif cmd[0] == 'list':
                scheduler.list_schedules()
            elif cmd[0] == 'clear':
                scheduler.clear_schedules()
            elif cmd[0] == 'start':
                scheduler.start()
            elif cmd[0] == 'stop':
                scheduler.stop()
            else:
                print("❌ Unknown command or wrong arguments")
        
        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return scheduler

def demo_breathing(lamp, color="#FF0000", cycles=3):
    """Demo: Breathing effect"""
    print("\n" + "="*60)
    print("💨 DEMO: Breathing Effect")
    print("="*60 + "\n")
    
    lamp.turn_on()
    hsv = hex_to_hsv(color)
    
    for _ in range(cycles):
        # Fade in
        for v in range(100, 1001, 50):
            lamp.set_color_hsv(hsv['h'], hsv['s'], v)
            time.sleep(0.05)
        # Fade out
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

# ===============================================
# Interactive Mode
# ===============================================
def interactive_mode(lamp):
    """Interactive command-line control"""
    print("\n" + "="*60)
    print("🎮 INTERACTIVE MODE")
    print("="*60)
    print("\nCommands:")
    print("  hex <color>        - Set color by hex (e.g., hex #FF0000)")
    print("  rgb <r> <g> <b>    - Set color by RGB (e.g., rgb 255 0 0)")
    print("  hsv <h> <s> <v>    - Set color by HSV (e.g., hsv 0 1000 1000)")
    print("  on                 - Turn lamp on")
    print("  off                - Turn lamp off")
    print("  status             - Show current status")
    print("  demo               - Run color demos")
    print("  schedule           - Enter scheduling mode")
    print("  quit               - Exit")
    print()
    
    while True:
        try:
            cmd = input("lamp> ").strip().lower().split()
            if not cmd:
                continue
            
            if cmd[0] == 'quit' or cmd[0] == 'exit':
                break
            elif cmd[0] == 'on':
                lamp.turn_on()
            elif cmd[0] == 'off':
                lamp.turn_off()
            elif cmd[0] == 'hex' and len(cmd) == 2:
                lamp.set_color_hex(cmd[1])
            elif cmd[0] == 'rgb' and len(cmd) == 4:
                lamp.set_color_rgb(int(cmd[1]), int(cmd[2]), int(cmd[3]))
            elif cmd[0] == 'hsv' and len(cmd) == 4:
                lamp.set_color_hsv(int(cmd[1]), int(cmd[2]), int(cmd[3]))
            elif cmd[0] == 'status':
                status = lamp.get_status()
                print(f"\n{status}\n")
            elif cmd[0] == 'schedule':
                schedule_mode(lamp)
            elif cmd[0] == 'demo':
                print("\nWhich demo?")
                print("  1. Basic colors")
                print("  2. Rainbow (smooth)")
                print("  3. Random rainbow")
                print("  4. Breathing")
                print("  5. Strobe")
                print("  6. Party mode 🎉")
                print("  7. Pastel mode 🌸")
                print("  8. Fire effect 🔥")
                print("  9. Ocean effect 🌊")
                print("  10. Sunset mode 🌅")
                print("  11. Police lights 🚨")
                choice = input("Choice (1-11): ").strip()
                if choice == '1':
                    demo_basic_colors(lamp)
                elif choice == '2':
                    demo_rainbow(lamp)
                elif choice == '3':
                    demo_random_rainbow(lamp)
                elif choice == '4':
                    demo_breathing(lamp)
                elif choice == '5':
                    demo_strobe(lamp)
                elif choice == '6':
                    demo_party_mode(lamp)
                elif choice == '7':
                    demo_pastel_mode(lamp)
                elif choice == '8':
                    demo_fire_effect(lamp)
                elif choice == '9':
                    demo_ocean_effect(lamp)
                elif choice == '10':
                    demo_sunset_mode(lamp)
                elif choice == '11':
                    demo_police_lights(lamp)
            else:
                print("❌ Unknown command or wrong arguments")
        
        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

# ===============================================
# Main
# ===============================================
def main():
    print("="*60)
    print("🔮 NEURO LAVA LAMP CONTROLLER")
    print("="*60 + "\n")
    
    try:
        lamp = LavaLampController()
        
        # Check command-line arguments
        if len(sys.argv) > 1:
            cmd = sys.argv[1].lower()
            
            if cmd == 'demo':
                demo_basic_colors(lamp)
                demo_rainbow(lamp)
                demo_random_rainbow(lamp, duration=10)
            elif cmd == 'rainbow':
                demo_rainbow(lamp)
            elif cmd == 'random':
                demo_random_rainbow(lamp)
            elif cmd == 'party':
                demo_party_mode(lamp)
            elif cmd == 'pastel':
                demo_pastel_mode(lamp)
            elif cmd == 'fire':
                demo_fire_effect(lamp)
            elif cmd == 'ocean':
                demo_ocean_effect(lamp)
            elif cmd == 'sunset':
                demo_sunset_mode(lamp)
            elif cmd == 'police':
                demo_police_lights(lamp)
            elif cmd == 'breathing':
                demo_breathing(lamp)
            elif cmd == 'strobe':
                demo_strobe(lamp)
            elif cmd.startswith('#'):
                lamp.turn_on()
                lamp.set_color_hex(cmd)
            else:
                print(f"❌ Unknown command: {cmd}")
                print("\nUsage:")
                print("  python lamp_controller.py              # Interactive mode")
                print("  python lamp_controller.py demo         # Run all demos")
                print("  python lamp_controller.py rainbow      # Rainbow cycle")
                print("  python lamp_controller.py random       # Random colors")
                print("  python lamp_controller.py party        # Party mode 🎉")
                print("  python lamp_controller.py pastel       # Pastel colors 🌸")
                print("  python lamp_controller.py fire         # Fire effect 🔥")
                print("  python lamp_controller.py ocean        # Ocean waves 🌊")
                print("  python lamp_controller.py sunset       # Sunset colors 🌅")
                print("  python lamp_controller.py police       # Police lights 🚨")
                print("  python lamp_controller.py breathing    # Breathing effect")
                print("  python lamp_controller.py strobe       # Strobe effect")
                print("  python lamp_controller.py #FF0000      # Set specific color")
        else:
            # Interactive mode
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
