# src/cli.py
from src.modes import all_modes
from src.scheduler import schedule_mode


def interactive_mode(lamp):
    """Interactive command-line control"""
    print("\n" + "="*60)
    print("🎮 INTERACTIVE MODE")
    print("="*60)
    print("\nCommands:")
    print("  hex <color>        - Set color by hex (e.g., hex #FF0000)")
    # ... (other existing commands) ...
    print("  on                 - Turn lamp on")
    print("  off                - Turn lamp off")
    print("  sync               - Activate Music/Stream Sync Mode 🎧") # ADDED
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
            # ... (existing commands) ...
            elif cmd[0] == 'sync': # ADDED LOGIC
                all_modes['sync'](lamp)
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
                # ... (existing demo logic) ...
                print("\nWhich demo?")
                mode_list = list(all_modes.keys())
                for i, mode_name in enumerate(mode_list, 1):
                    print(f"  {i}. {mode_name}")
                choice = input("Choice: ").strip()
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(mode_list):
                        mode_name = mode_list[idx]
                        all_modes[mode_name](lamp)
                    else:
                        print("❌ Invalid choice")
                except ValueError:
                    print("❌ Invalid choice")
            else:
                print("❌ Unknown command or wrong arguments")
        
        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}")