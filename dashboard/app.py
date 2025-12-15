# LLM Prompt:
# "Create a Flask web application for DriveGuard that:
# - Serves as the main web interface for the project
# - Connects to Shiftr.io MQTT broker to receive real-time data
# - Displays live driving metrics (speed, acceleration, GPS coordinates)
# - Shows current safety score with color-coded status (green >80, yellow 60-80, red <60)
# - Implements WebSocket or Server-Sent Events for real-time updates
# - Has a clean, modern dashboard layout
# - Displays historical data trends with charts
# - Shows system status (MQTT connection, last update time)
# - Uses Bootstrap or similar framework for responsive design
# - Runs on port 5000 for local development"

"""
DriveGuard Dashboard - Flask Backend
Reads Telegraf output and serves data to the web interface.
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import os
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# Get data file path from environment or use default
DATA_FILE = Path(os.environ.get("DRIVEGUARD_DATA_FILE", "../data/live_data.out"))
HISTORY_DIR = Path(os.environ.get("DRIVEGUARD_HISTORY_DIR", "../data/history"))

# Configurable thresholds
config = {
    "speed_danger": 120.0,
    "accel_harsh": 0.5
}


def parse_telegraf_file(filepath):
    """Parse the Telegraf output file and extract DriveGuard data."""
    batch_data = []
    alerts_speed = []
    alerts_harsh = []
    status_msgs = []
    
    filepath = Path(filepath)
    if not filepath.exists():
        return batch_data, alerts_speed, alerts_harsh, status_msgs
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse batch_data lines
                if 'batch_data' in line:
                    try:
                        parts = line.split(' ')
                        if len(parts) >= 2:
                            fields_part = parts[1]
                            fields = {}
                            for field in fields_part.split(','):
                                if '=' in field:
                                    key, val = field.split('=', 1)
                                    try:
                                        fields[key] = float(val)
                                    except:
                                        fields[key] = val
                            
                            if fields:
                                batch_data.append({
                                    'timestamp': fields.get('ts', 0),
                                    'speed': fields.get('spd', 0),
                                    'lat': fields.get('lat', 0),
                                    'lon': fields.get('lon', 0),
                                    'acc': fields.get('acc', 0),
                                    'score': fields.get('scr', 100),
                                    'gps_valid': fields.get('gps', 0)
                                })
                    except:
                        continue
                
                # Parse speed alerts
                elif 'alert_speed' in line:
                    try:
                        parts = line.split(' ')
                        if len(parts) >= 2:
                            fields_part = parts[1]
                            fields = {}
                            for field in fields_part.split(','):
                                if '=' in field:
                                    key, val = field.split('=', 1)
                                    try:
                                        fields[key] = float(val)
                                    except:
                                        fields[key] = val
                            
                            if fields:
                                alerts_speed.append({
                                    'timestamp': fields.get('ts', 0),
                                    'speed': fields.get('spd', 0),
                                    'limit': fields.get('lim', 120),
                                    'score': fields.get('scr', 0),
                                    'lat': fields.get('lat', 0),
                                    'lon': fields.get('lon', 0)
                                })
                    except:
                        continue
                
                # Parse harsh driving alerts
                elif 'alert_harsh' in line:
                    try:
                        parts = line.split(' ')
                        if len(parts) >= 2:
                            fields_part = parts[1]
                            fields = {}
                            for field in fields_part.split(','):
                                if '=' in field:
                                    key, val = field.split('=', 1)
                                    try:
                                        fields[key] = float(val)
                                    except:
                                        fields[key] = val
                            
                            if fields:
                                alerts_harsh.append({
                                    'timestamp': fields.get('ts', 0),
                                    'acceleration': fields.get('acc', 0),
                                    'threshold': fields.get('thr', 0.5),
                                    'score': fields.get('scr', 0)
                                })
                    except:
                        continue
                
                # Parse status messages
                elif 'status' in line:
                    try:
                        parts = line.split(' ')
                        if len(parts) >= 2:
                            fields_part = parts[1]
                            fields = {}
                            for field in fields_part.split(','):
                                if '=' in field:
                                    key, val = field.split('=', 1)
                                    fields[key] = val
                            if fields:
                                status_msgs.append(fields)
                    except:
                        continue
    
    except Exception as e:
        print(f"Error reading file: {e}")
    
    return batch_data, alerts_speed, alerts_harsh, status_msgs


@app.route('/')
def index():
    """Serve the dashboard HTML."""
    return render_template('dashboard.html')


@app.route('/api/data')
def get_data():
    """Get all parsed data for the dashboard."""
    batch_data, alerts_speed, alerts_harsh, status_msgs = parse_telegraf_file(DATA_FILE)
    
    # Calculate statistics
    total_readings = len(batch_data)
    total_alerts = len(alerts_speed) + len(alerts_harsh)
    
    if batch_data:
        current_score = batch_data[-1].get('score', 100)
        max_speed = max(d.get('speed', 0) for d in batch_data)
        avg_speed = sum(d.get('speed', 0) for d in batch_data) / total_readings
        max_accel = max(d.get('acc', 0) for d in batch_data)
    else:
        current_score = 100
        max_speed = 0
        avg_speed = 0
        max_accel = 0
    
    return jsonify({
        'batch_data': batch_data[-500:],
        'alerts_speed': alerts_speed,
        'alerts_harsh': alerts_harsh,
        'status': status_msgs,
        'stats': {
            'total_readings': total_readings,
            'total_alerts': total_alerts,
            'current_score': current_score,
            'max_speed': max_speed,
            'avg_speed': avg_speed,
            'max_accel': max_accel,
            'speed_alerts': len(alerts_speed),
            'harsh_alerts': len(alerts_harsh)
        },
        'config': config,
        'last_update': datetime.now().isoformat()
    })


@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update configuration."""
    global config
    
    if request.method == 'POST':
        data = request.json
        if 'speed_danger' in data:
            config['speed_danger'] = float(data['speed_danger'])
        if 'accel_harsh' in data:
            config['accel_harsh'] = float(data['accel_harsh'])
        return jsonify({'status': 'success', 'config': config})
    
    return jsonify(config)


@app.route('/api/history')
def get_history():
    """Get list of historical sessions."""
    sessions = []
    if HISTORY_DIR.exists():
        for f in sorted(HISTORY_DIR.glob("session_*.out"), reverse=True):
            stat = f.stat()
            sessions.append({
                'filename': f.name,
                'date': f.stem.replace('session_', ''),
                'size': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 1)
            })
    return jsonify({'sessions': sessions})


@app.route('/api/history/<filename>')
def get_history_data(filename):
    """Get data from a historical session."""
    filepath = HISTORY_DIR / filename
    if not filepath.exists() or not filename.startswith('session_'):
        return jsonify({'error': 'File not found'}), 404
    
    batch_data, alerts_speed, alerts_harsh, _ = parse_telegraf_file(filepath)
    
    total_readings = len(batch_data)
    if batch_data:
        current_score = batch_data[-1].get('score', 100)
        max_speed = max(d.get('speed', 0) for d in batch_data)
        avg_speed = sum(d.get('speed', 0) for d in batch_data) / total_readings
    else:
        current_score = 100
        max_speed = 0
        avg_speed = 0
    
    return jsonify({
        'batch_data': batch_data,
        'alerts_speed': alerts_speed,
        'alerts_harsh': alerts_harsh,
        'stats': {
            'total_readings': total_readings,
            'total_alerts': len(alerts_speed) + len(alerts_harsh),
            'current_score': current_score,
            'max_speed': max_speed,
            'avg_speed': avg_speed
        }
    })


if __name__ == '__main__':
    print("=" * 50)
    print("  DriveGuard Dashboard")
    print("=" * 50)
    print(f"  Data file: {DATA_FILE}")
    print(f"  History: {HISTORY_DIR}")
    print()
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
