# src/gui.py
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
from src.modes import all_modes


app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# Global lamp controller instance
lamp_controller = None


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get lamp status"""
    try:
        status = lamp_controller.get_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/power', methods=['POST'])
def set_power():
    """Turn lamp on/off"""
    try:
        data = request.json
        if data.get('state') == 'on':
            lamp_controller.turn_on()
        else:
            lamp_controller.turn_off()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/color', methods=['POST'])
def set_color():
    """Set lamp color"""
    try:
        data = request.json
        color_type = data.get('type', 'hex')
        
        if color_type == 'hex':
            lamp_controller.set_color_hex(
                data['value'],
                brightness=data.get('brightness', 100)
            )
        elif color_type == 'rgb':
            rgb = data['value']
            lamp_controller.set_color_rgb(
                rgb['r'], rgb['g'], rgb['b'],
                brightness=data.get('brightness', 100)
            )
        elif color_type == 'hsv':
            hsv = data['value']
            lamp_controller.set_color_hsv(
                hsv['h'], hsv['s'], hsv['v']
            )
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/effect', methods=['POST'])
def run_effect():
    """Run an effect mode"""
    try:
        data = request.json
        effect_name = data.get('name')
        duration = data.get('duration', 30)
        
        if effect_name not in all_modes:
            return jsonify({'success': False, 'error': 'Unknown effect'}), 400
        
        # Run effect in background thread so API returns immediately
        def run():
            all_modes[effect_name](lamp_controller, duration=duration)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/effects')
def list_effects():
    """List all available effects"""
    return jsonify({
        'success': True,
        'effects': list(all_modes.keys())
    })


def start_web_interface(lamp, host='127.0.0.1', port=5000):
    """Start the Flask web interface"""
    global lamp_controller
    lamp_controller = lamp
    
    print(f"\n🌐 Web interface starting...")
    print(f"   URL: http://{host}:{port}")
    print("   Press Ctrl+C to stop\n")
    
    app.run(host=host, port=port, debug=False)