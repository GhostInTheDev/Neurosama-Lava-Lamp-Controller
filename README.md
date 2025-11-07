# 🔮 Neuro-sama Lava Lamp Controller

A comprehensive Python-based controller for Tuya-compatible smart lamps, originally developed for Neuro-sama's lava lamp. This project provides both CLI and web-based interfaces for controlling color, scheduling effects, and monitoring lamp activity.

## ✨ Features

### Core Functionality
- 🎨 **Full Color Control** - Set colors via HEX, RGB, or HSV
- 💡 **Power Management** - Turn lamp on/off programmatically
- 🌐 **Dual Interface** - Choose between terminal CLI or web GUI
- 📊 **Real-time Monitoring** - Intercept and display color changes
- ⏰ **Advanced Scheduling** - Schedule colors and effects for specific dates/times
- 🎭 **Multiple Effect Modes** - Pre-built visual effects ready to use

### Effect Modes
- 🌈 **Rainbow** - Smooth spectrum cycling
- 🎲 **Random Rainbow** - Vibrant random colors
- 🎉 **Party Mode** - Fast random flashing
- 🔥 **Fire Effect** - Flickering reds, oranges, yellows
- 🌊 **Ocean Effect** - Calming blues and greens
- 🌅 **Sunset Mode** - Purples, pinks, and oranges
- 🌸 **Pastel Mode** - Soft, gentle colors
- 💨 **Breathing** - Fade in/out effect
- ⚡ **Strobe** - High-intensity flashing
- 🚨 **Police Lights** - Alternating red and blue

## 📋 Requirements

- Python 3.7+
- Tuya-compatible smart lamp
- Local network access to the lamp
- Device credentials (Device ID, Local Key, IP Address)

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/GhostInTheDev/Neurosama-Lava-Lamp-Controller.git
cd Neurosama-Lava-Lamp-Controller
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure device credentials:**
Edit `lamp_controller.py` and update these values:
```python
DEVICE_ID = "your_device_id_here"
LOCAL_KEY = "your_local_key_here"
DEVICE_IP = "your_lamp_ip_here"
DEVICE_VERSION = 3.5  # Usually 3.5 for newer devices
```

## 🎮 Usage

### Terminal Mode (Default)

**Interactive CLI:**
```bash
python lamp_controller.py
```

Available commands:
- `hex #FF0000` - Set color by hex code
- `rgb 255 0 0` - Set color by RGB values
- `hsv 0 1000 1000` - Set color by HSV values
- `on` / `off` - Power control
- `status` - Show current lamp status
- `demo` - Browse and run effect modes
- `schedule` - Enter scheduling mode
- `quit` - Exit

**Quick Commands:**
```bash
# Run specific effect
python lamp_controller.py rainbow
python lamp_controller.py fire
python lamp_controller.py party

# Set specific color
python lamp_controller.py #FF0000

# Run all demos
python lamp_controller.py demo
```

### Web Interface Mode

**Start web server:**
```bash
python lamp_controller.py --gui
```

Then open your browser to `http://127.0.0.1:5000`

**Custom port/host:**
```bash
python lamp_controller.py --gui --port 8080 --host 0.0.0.0
```

### Scheduling

Schedule lamp actions for specific times:

```bash
python lamp_controller.py
lamp> schedule

# Turn on at 2:30 PM with red color
schedule> on 14:30 #FF0000

# Turn on at specific date/time
schedule> on 2025-12-25 08:00 #00FF00

# Schedule an effect
schedule> effect 18:00 fire 60

# Turn off at 10 PM
schedule> off 22:00

# View all schedules
schedule> list

# Start the scheduler
schedule> start
```

Time formats supported:
- `HH:MM` - Today (or tomorrow if time passed)
- `YYYY-MM-DD HH:MM` - Specific date and time
- `MM-DD HH:MM` - This year

## 🔍 Monitoring & Interception

### Real-time Color Monitoring

Monitor color changes sent to the lamp:

```bash
python color_interceptor.py
```

This will display:
- Power state changes
- Mode switches (manual vs sync)
- Color data in HSV and HEX formats
- Raw Tuya protocol data

### Network Packet Sniffing

Capture Tuya protocol traffic (requires root/admin):

```bash
sudo python tuya_sniffer.py
```

Or target a specific device:
```bash
sudo python tuya_sniffer.py 192.168.1.100
```

## 📁 Project Structure

```
lamp_controller/
├── lamp_controller.py          # Main entry point
├── color_interceptor.py        # Real-time color monitoring
├── tuya_sniffer.py            # Network packet capture tool
├── requirements.txt           # Python dependencies
│
├── src/
│   ├── controller.py          # Core lamp controller
│   ├── cli.py                 # Terminal interface
│   ├── gui.py                 # Web interface (Flask)
│   ├── scheduler.py           # Scheduling system
│   ├── utils.py               # Color conversion utilities
│   │
│   └── modes/                 # Effect modules
│       ├── basic.py
│       ├── rainbow.py
│       ├── party.py
│       ├── nature.py
│       ├── utility.py
│       └── pastel.py
│
├── static/                    # Web assets
│   ├── style.css
│   └── app.js
│
└── templates/
    └── index.html            # Web interface template
```

## 🔧 Advanced Configuration

### Finding Your Device Credentials

**Device ID and Local Key:**
1. Use the Tuya/Smart Life mobile app
2. Check application logs when controlling the device
3. Or use tools like `tuya-cli` to extract credentials

**Device IP:**
```bash
# Scan network for Tuya devices
python tuya_sniffer.py --scan
```

**Protocol Version:**
- Try 3.5 first (newest devices)
- Fallback to 3.3 or 3.1 if needed
- The script auto-detects on connection

### Adding Custom Effects

Create a new file in `src/modes/`:

```python
# src/modes/my_effect.py
import time

def demo_my_effect(lamp, duration=30):
    """My custom effect"""
    lamp.turn_on()
    lamp.set_mode('colour')
    
    start = time.time()
    while time.time() - start < duration:
        # Your effect code here
        lamp.set_color_hex("#FF0000")
        time.sleep(0.5)
```

Register it in `src/modes/__init__.py`:
```python
from .my_effect import demo_my_effect
all_modes['my_effect'] = demo_my_effect
```

## 🛠️ Troubleshooting

### Connection Issues

**"Unexpected Payload from Device":**
- Try different protocol versions (3.5, 3.3, 3.1)
- Verify the local key is correct
- Ensure device is on the same network

**"Connection Failed":**
- Check if device IP is correct
- Verify firewall isn't blocking UDP ports 6666-6668
- Ensure lamp is powered on and connected to WiFi

**"Device Key or Version Error":**
- Double-check your Local Key
- Try protocol version 3.5 instead of 3.3

### Color Monitoring Not Working

**No colors displayed in sync mode:**
- Sync colors may use DPS 27 (music_data) instead of DPS 24
- Check the monitoring script output for all DPS changes
- Verify sync mode is actually enabled on the lamp

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new effect modes
- Improve the web interface
- Fix bugs or add features
- Improve documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for the Neuro-sama community
- Uses the [TinyTuya](https://github.com/jasonacox/tinytuya) library for Tuya device communication
- Inspired by the need for programmatic control of streaming setup lighting

## 📧 Support

For issues, questions, or feature requests, please open an issue on GitHub.

## ⚠️ Disclaimer

This project is for educational and personal use. Always respect device manufacturer warranties and terms of service when modifying or controlling IoT devices. Use at your own risk.