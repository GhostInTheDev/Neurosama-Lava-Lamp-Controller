import time
import threading
from datetime import datetime, timedelta
from src.modes import all_modes
import json
import os

# Define the file path for persistent schedules
SCHEDULE_FILE = 'schedules.json'

class LampScheduler:
    """Schedule lamp actions at specific times"""
    
    def __init__(self, lamp):
        self.lamp = lamp
        self.schedules = []
        self.running = False
        self.thread = None
        self._load_schedules() # Load schedules on startup
    
    # --- Persistence Methods ---
    
    def _load_schedules(self):
        """Loads schedules from the JSON file."""
        if os.path.exists(SCHEDULE_FILE):
            try:
                with open(SCHEDULE_FILE, 'r') as f:
                    data = json.load(f)
                    self.schedules = []
                    for item in data:
                        # Convert ISO string back to datetime object
                        item['time'] = datetime.fromisoformat(item['time'])
                        self.schedules.append(item)
                print(f"✅ Loaded {len(self.schedules)} schedules.")
            except Exception as e:
                print(f"⚠️ Failed to load schedules: {e}")
    
    def _save_schedules(self):
        """Saves current schedules to the JSON file."""
        try:
            # Convert datetime objects to ISO format strings for JSON serialization
            data = [
                {k: v.isoformat() if isinstance(v, datetime) else v for k, v in schedule.items()}
                for schedule in self.schedules
            ]
            with open(SCHEDULE_FILE, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"❌ Failed to save schedules: {e}")
    
    # --- Scheduling Methods ---
    
    def schedule_on(self, target_time, color="#FFFFFF", brightness=100):
        """Schedule lamp to turn on at a specific time"""
        if isinstance(target_time, str):
            target_time = self._parse_time_string(target_time)
        
        schedule = {
            'time': target_time,
            'action': 'on',
            'color': color,
            'brightness': brightness
        }
        self.schedules.append(schedule)
        self._save_schedules()
        print(f"✅ Scheduled: Turn ON at {target_time.strftime('%Y-%m-%d %H:%M:%S')} with color {color}")
        return schedule
    
    def schedule_off(self, target_time):
        """Schedule lamp to turn off at a specific time"""
        if isinstance(target_time, str):
            target_time = self._parse_time_string(target_time)
        
        schedule = {
            'time': target_time,
            'action': 'off'
        }
        self.schedules.append(schedule)
        self._save_schedules()
        print(f"✅ Scheduled: Turn OFF at {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return schedule

    def schedule_sync(self, target_time):
        """Schedule the 'sync' effect to run at a specific time"""
        if isinstance(target_time, str):
            target_time = self._parse_time_string(target_time)
        
        schedule = {
            'time': target_time,
            'action': 'effect',
            'effect': 'sync', # Fixed effect name
        }
        self.schedules.append(schedule)
        self._save_schedules()
        print(f"✅ Scheduled: Stream SYNC at {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return schedule
    
    def schedule_effect(self, target_time, effect_name, duration=30):
        """Schedule an effect (non-sync) to run at a specific time"""
        if effect_name == 'sync':
             return self.schedule_sync(target_time, duration)

        if isinstance(target_time, str):
            target_time = self._parse_time_string(target_time)
        
        schedule = {
            'time': target_time,
            'action': 'effect',
            'effect': effect_name,
            'duration': duration
        }
        self.schedules.append(schedule)
        self._save_schedules()
        print(f"✅ Scheduled: {effect_name} effect at {target_time.strftime('%Y-%m-%d %H:%M:%S')} for {duration}s")
        return schedule
    
    def remove_schedule(self, index):
        """Remove a schedule by 1-based index (for CLI)"""
        try:
            # Sort schedules by time to ensure the index matches the CLI/UI list order
            sorted_schedules = sorted(self.schedules, key=lambda x: x['time'])
            
            # Get the schedule object using the 1-based index
            schedule_to_remove = sorted_schedules[index - 1]
            
            # Find and remove the original object from the unsorted list
            self.schedules.remove(schedule_to_remove)
            self._save_schedules()
            print(f"🗑️ Removed schedule at {schedule_to_remove['time'].strftime('%H:%M')} ({schedule_to_remove['action']})")
            return True
            
        except IndexError:
            print(f"❌ Schedule index {index} not found.")
            return False
        except Exception as e:
            print(f"❌ Error removing schedule: {e}")
            return False


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
    
    # --- Thread Management ---

    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            print("⚠️  Scheduler already running!")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("🕐 Scheduler started! Checking every 1s.")
    
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
            
            # Sort schedules to handle execution order correctly
            sorted_schedules = sorted(self.schedules, key=lambda x: x['time'])

            for schedule in sorted_schedules[:]:
                # Check for time match (use a small window around the minute for robustness)
                if now >= schedule['time'] and now < schedule['time'] + timedelta(seconds=60): 
                    print(f"\n⏰ Executing scheduled action at {now.strftime('%H:%M:%S')}")
                    
                    # Assume we should remove the schedule unless it is an indefinite effect
                    remove_schedule = True
                    
                    try:
                        # 1. Guarantee lamp is ON before any action (except off)
                        if schedule['action'] != 'off':
                             self.lamp.turn_on()
                             time.sleep(0.1) 

                        # 2. Execute Action
                        if schedule['action'] == 'on':
                            self.lamp.set_color_hex(schedule['color'], schedule['brightness'])
                            print(f"   ✅ Lamp turned ON with color {schedule['color']}")
                        
                        elif schedule['action'] == 'off':
                            self.lamp.turn_off()
                            print(f"   ✅ Lamp turned OFF")
                        
                        elif schedule['action'] == 'effect':
                            effect = schedule['effect']
                            # Use .get() to safely check for duration, defaulting to a non-zero value if missing
                            duration = schedule.get('duration') 
                            
                            if effect in all_modes:
                                
                                # --- NEW LOGIC FOR INDEFINITE SYNC ---
                                # If the action is sync AND duration is None/0 (meaning indefinitely scheduled)
                                if effect == 'sync' and not duration:
                                    # Execute the ON sequence for Stream Sync (duration=None runs indefinitely)
                                    all_modes[effect](self.lamp)
                                    print(f"   ✅ Running {effect.upper()} effect INDEFINITELY.")
                                    # Schedule should still be removed after execution - it's a one-time trigger
                                    remove_schedule = True
                                
                                else:
                                    # Execute standard timed effect (including timed sync from CLI)
                                    all_modes[effect](self.lamp, duration)
                                    print(f"   ✅ Running {effect.upper()} effect for {duration}s")
                            else:
                                print(f"   ❌ Error: Effect '{effect}' not found in modes.")
                    
                    except Exception as e:
                        print(f"   ❌ Error executing schedule: {e}")
                    
                    # 3. Remove completed schedule
                    if remove_schedule:
                        self.schedules.remove(schedule)
                        self._save_schedules()
            
            time.sleep(1)
    
    # --- UI/CLI Display Methods ---

    def list_schedules(self):
        """Show all scheduled actions (formatted for CLI)"""
        if not self.schedules:
            return "\n📋 No schedules set"
        
        output = ["\n📋 Scheduled Actions:", "="*60]
        
        sorted_schedules = sorted(self.schedules, key=lambda x: x['time'])
        
        for i, schedule in enumerate(sorted_schedules, 1):
            time_str = schedule['time'].strftime('%Y-%m-%d %H:%M:%S')
            action = schedule['action']
            
            if action == 'on':
                details = f"Turn ON ({schedule['color']} @ {schedule['brightness']}%)"
            elif action == 'off':
                details = "Turn OFF"
            elif action == 'effect':
                details = f"{schedule['effect'].upper()} effect ({schedule['duration']}s)"
            else:
                details = "Unknown Action"
                
            output.append(f"{i}. {time_str} - {details}")
        
        output.append("="*60 + "\n")
        return "\n".join(output)
    
    def clear_schedules(self):
        """Clear all schedules"""
        self.schedules.clear()
        self._save_schedules()
        print("🗑️  All schedules cleared!")

    def get_raw_schedules(self):
        """Returns the raw list of schedules for GUI serialization."""
        # Must serialize datetime objects to ISO strings
        sorted_schedules = sorted(self.schedules, key=lambda x: x['time'])
        return [
            {k: v.isoformat() if isinstance(v, datetime) else v for k, v in schedule.items()}
            for schedule in sorted_schedules
        ]


def schedule_mode(lamp):
    """Interactive scheduling mode (CLI)"""
    # Note: In the final app, this function would likely receive the scheduler instance.
    scheduler = LampScheduler(lamp)
    
    if not scheduler.running:
        print("⚠️  Scheduler is not running. Use 'start' to activate.")

    print("\n" + "="*60)
    print("🕐 SCHEDULING MODE")
    print("="*60)
    print("\nCommands:")
    print("  on <time> [color]     - Schedule turn on")
    print("  off <time>            - Schedule turn off")
    print("  sync <time> - Schedule Stream Sync (turns ON lamp)")
    print("  effect <time> <name>  - Schedule other effect")
    print("  list                  - Show all schedules")
    print("  remove <index>        - Remove schedule by index (1-based)")
    print("  clear                 - Clear all schedules")
    print("  start                 - Start scheduler (run in background)")
    print("  stop                  - Stop scheduler")
    print("  back                  - Return to main menu")
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
            
            # --- Command Parsing (Simplified for CLI) ---
            
            elif cmd[0] == 'on':
                if len(cmd) < 2:
                    print("❌ Invalid format. Requires time.")
                    continue
                time_str = cmd[1] if len(cmd) == 2 else f"{cmd[1]} {cmd[2]}"
                color = cmd[-1] if cmd[-1].startswith('#') else "#FFFFFF"
                scheduler.schedule_on(time_str, color)
            
            elif cmd[0] == 'off':
                if len(cmd) < 2:
                    print("❌ Invalid format. Requires time.")
                    continue
                time_str = cmd[1] if len(cmd) == 2 else f"{cmd[1]} {cmd[2]}"
                scheduler.schedule_off(time_str)

            elif cmd[0] == 'sync': 
                if len(cmd) < 2:
                    print("❌ Invalid format. Requires time.")
                    continue
                time_str = cmd[1] if len(cmd) == 2 else f"{cmd[1]} {cmd[2]}"
                duration = int(cmd[-1]) if len(cmd) > 2 and cmd[-1].isdigit() else 3600
                scheduler.schedule_sync(time_str)
            
            elif cmd[0] == 'effect':
                if len(cmd) < 3:
                    print("❌ Invalid format. Requires time and effect name.")
                    continue
                time_str = cmd[1] if len(cmd) == 3 else f"{cmd[1]} {cmd[2]}"
                effect = cmd[-2] if cmd[-1].isdigit() else cmd[-1]
                duration = int(cmd[-1]) if cmd[-1].isdigit() else 30
                
                if effect not in all_modes:
                    print(f"❌ Effect '{effect}' not recognized.")
                    continue
                
                scheduler.schedule_effect(time_str, effect, duration)
                
            elif cmd[0] == 'list':
                print(scheduler.list_schedules())

            elif cmd[0] == 'remove' and len(cmd) == 2:
                 try:
                     index = int(cmd[1])
                     scheduler.remove_schedule(index)
                 except ValueError:
                     print("❌ Invalid index. Please enter a number.")
            
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