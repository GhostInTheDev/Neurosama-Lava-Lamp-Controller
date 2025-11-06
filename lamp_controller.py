#!/usr/bin/env python3
"""
===============================================
NEURO LAVA LAMP CONTROLLER - Main Entry Point
===============================================
"""

import sys
import argparse
from src.controller import LavaLampController
from src.cli import interactive_mode
from src.gui import start_web_interface
from src.config import DEVICE_ID, LOCAL_KEY, DEVICE_IP, DEVICE_VERSION # IMPORTED credentials from config.py


def main():
    parser = argparse.ArgumentParser(
        description="Control your Neuro Lava Lamp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lamp_controller.py                     # Interactive CLI mode
  python lamp_controller.py --gui               # Web interface mode
  python lamp_controller.py --port 8080         # Web interface on custom port
  python lamp_controller.py rainbow             # Run rainbow demo
  python lamp_controller.py #FF0000             # Set specific color
        """
    )
    
    parser.add_argument('--gui', action='store_true',
                        help='Start web interface instead of CLI')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port for web interface (default: 5000)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host for web interface (default: 127.0.0.1)')
    parser.add_argument('command', nargs='?', default=None,
                        help='Quick command: rainbow, party, fire, ocean, sunset, police, pastel, breathing, strobe, demo, or #RRGGBB')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🔮 NEURO LAVA LAMP CONTROLLER")
    print("="*60 + "\n")
    
    try:
        # Initialize lamp controller using imported credentials
        lamp = LavaLampController(
            device_id=DEVICE_ID,
            local_key=LOCAL_KEY,
            device_ip=DEVICE_IP,
            version=DEVICE_VERSION
        )
        
        # Start web interface mode
        if args.gui:
            print(f"🌐 Starting web interface on http://{args.host}:{args.port}")
            start_web_interface(lamp, host=args.host, port=args.port)
            return
        
        # Quick command mode
        if args.command:
            from src.modes import all_modes
            
            cmd = args.command.lower()
            
            if cmd == 'demo':
                # Run all demos
                for mode_name in ['basic_colors', 'rainbow', 'random_rainbow']:
                    if mode_name in all_modes:
                        all_modes[mode_name](lamp, duration=10)
            
            elif cmd in all_modes:
                # Run specific mode
                all_modes[cmd](lamp)
            
            elif args.command.startswith('#'):
                # Set specific color
                lamp.turn_on()
                lamp.set_color_hex(args.command)
            
            else:
                print(f"❌ Unknown command: {cmd}")
                print("\nAvailable commands:")
                for mode_name in all_modes.keys():
                    print(f"  - {mode_name}")
                return
        
        else:
            # Interactive CLI mode
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