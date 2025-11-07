# src/cli.py
from src.modes import all_modes
from src.scheduler import schedule_mode, LampScheduler # Import necessary scheduler functions

# Global instance of the scheduler (needs to be initialized in main.py)
# We will assume a global scheduler instance is managed by the main script for persistence.
# For simplicity, we define a placeholder scheduler instance here.
SCHEDULER = None 

def interactive_mode(lamp):
    """Interactive command-line control"""
    
    # Initialize scheduler if it hasn't been done globally
    global SCHEDULER
    if SCHEDULER is None:
        SCHEDULER = LampScheduler(lamp)
        # Note: In a production app, the scheduler should be started once in main.py

    print("\n" + "="*60)
    print("🎮 INTERACTIVE MODE")
    print("="*60)
    print("\nCommands:")
    print("  hex <color>        - Set color by hex (e.g., hex #FF0000)")
    print("  rgb <r> <g> <b>    - Set color by RGB (e.g., rgb 255 0 0)")
    print("  hsv <h> <s> <v>    - Set color by HSV (e.g., hsv 0 1000 1000)")
    print("  on                 - Turn lamp on")
    print("  off                - Turn lamp off")
    print("  sync               - Activate Stream Sync Mode 🎧")
    print("  status             - Show current status")
    print("  schedule           - Enter scheduling mode")
    print("  list               - Show scheduled commands") # New direct access
    print("  remove <index>     - Remove scheduled command (1-based)") # New direct access
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
            elif cmd[0] == 'sync':
                all_modes['sync'](lamp)
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
                schedule_mode(lamp) # Enters the interactive scheduling menu
            elif cmd[0] == 'list': # Direct list access
                print(SCHEDULER.list_schedules())
            elif cmd[0] == 'remove' and len(cmd) == 2: # Direct remove access
                try:
                    index = int(cmd[1])
                    SCHEDULER.remove_schedule(index)
                except ValueError:
                    print("❌ Invalid index. Please enter a number.")
            else:
                print("❌ Unknown command or wrong arguments")
        
        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}")