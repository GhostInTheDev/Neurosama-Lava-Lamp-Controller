# src/scheduler.py
import time
import threading
from datetime import datetime, timedelta
from src.modes import all_modes


class LampScheduler:
    """Schedule lamp actions at specific times"""
    
    def __init__(self, lamp):
        self.lamp = lamp
        self.schedules = []
        self.running = False
        self.thread = None
    
    def schedule_on(self, target_time, color="#FFFFFF", brightness=100):
        """Schedule lamp to turn on at a specific time"""
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
        """Schedule an effect to run at a specific time"""
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
            if target < now:
                target += timedelta(days=1)
            return target
        
        # Format: "YYYY-MM-DD HH:MM"
        elif len(time_str) >= 16:
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        
        # Format: "MM-DD HH:MM" (this year)
        elif len(time_str) == 11:
            return datetime.strptime(f"{now.year}-{time_str}", "%Y-%m-%d %H:%M")
        
        else:
            raise ValueError(f"Invalid time format: {time_str}")
    
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
            
            for schedule in self.schedules[:]:
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
                            
                            if effect in all_modes:
                                all_modes[effect](self.lamp, duration)
                    
                    except Exception as e:
                        print(f"   ❌ Error executing schedule: {e}")
                    
                    self.schedules.remove(schedule)
            
            time.sleep(1)
    
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
    print("  on <time> [color]     - Schedule turn on")
    print("                          Examples:")
    print("                            on 14:30")
    print("                            on 14:30 #FF0000")
    print("                            on 2025-11-10 10:30")
    print("                            on 2025-11-10 10:30 #00FF00")
    print("  off <time>            - Schedule turn off")
    print("  effect <time> <name>  - Schedule effect")
    print("  list                  - Show all schedules")
    print("  clear                 - Clear all schedules")
    print("  start                 - Start scheduler (run in background)")
    print("  stop                  - Stop scheduler")
    print("  back                  - Return to main menu")
    print("\nTime formats:")
    print("  HH:MM              - Today (or tomorrow if time passed)")
    print("  YYYY-MM-DD HH:MM   - Specific date and time")
    print("  MM-DD HH:MM        - This year")
    print()
    
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
                if len(cmd) == 2:
                    time_str = cmd[1]
                    color = "#FFFFFF"
                elif len(cmd) == 3:
                    if cmd[2].startswith('#'):
                        time_str = cmd[1]
                        color = cmd[2]
                    else:
                        time_str = f"{cmd[1]} {cmd[2]}"
                        color = "#FFFFFF"
                elif len(cmd) == 4:
                    time_str = f"{cmd[1]} {cmd[2]}"
                    color = cmd[3]
                else:
                    print("❌ Invalid format")
                    continue
                scheduler.schedule_on(time_str, color)
            elif cmd[0] == 'off' and len(cmd) >= 2:
                if len(cmd) == 2:
                    time_str = cmd[1]
                else:
                    time_str = f"{cmd[1]} {cmd[2]}"
                scheduler.schedule_off(time_str)
            elif cmd[0] == 'effect' and len(cmd) >= 3:
                if len(cmd) == 3:
                    time_str = cmd[1]
                    effect = cmd[2]
                    duration = 30
                elif len(cmd) == 4:
                    if cmd[3].isdigit():
                        time_str = cmd[1]
                        effect = cmd[2]
                        duration = int(cmd[3])
                    else:
                        time_str = f"{cmd[1]} {cmd[2]}"
                        effect = cmd[3]
                        duration = 30
                elif len(cmd) == 5:
                    time_str = f"{cmd[1]} {cmd[2]}"
                    effect = cmd[3]
                    duration = int(cmd[4])
                else:
                    print("❌ Invalid format")
                    continue
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
                print("❌ Unknown command")
        
        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return scheduler