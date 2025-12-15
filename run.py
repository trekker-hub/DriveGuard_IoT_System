# Prompt:
# "Create a Flask web dashboard for DriveGuard that:
# - Subscribes to MQTT topics from Shiftr.io
# - Displays real-time driving data (speed, acceleration, location)
# - Shows safety score with color coding (green/yellow/red)
# - Creates graphs for speed and acceleration over time
# - Shows GPS coordinates on an embedded map"
# - Updates in real-time as new data arrives
# - Uses the configuration from config.py
# - Has a clean, professional interface
# - Runs on localhost:5000"


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     DRIVEGUARD - MAIN LAUNCHER                               ║
║                     Run this file to start everything                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python run.py              - Start Telegraf + Dashboard
    python run.py --update     - Update Arduino code with config settings
    python run.py --dashboard  - Start only the dashboard
    python run.py --help       - Show help
"""

import os
import sys
import subprocess
import shutil
import webbrowser
import time
import signal
from datetime import datetime
from pathlib import Path

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent.resolve()
ARDUINO_DIR = BASE_DIR / "arduino" / "DriveGuard_Shiftr_Production"
ARDUINO_FILE = ARDUINO_DIR / "DriveGuard_Shiftr_Production.ino"
TELEGRAF_DIR = BASE_DIR / "telegraf"
TELEGRAF_CONF = TELEGRAF_DIR / "telegraf_driveguard.conf"
DATA_DIR = BASE_DIR / "data"
HISTORY_DIR = DATA_DIR / "history"
LIVE_DATA_FILE = DATA_DIR / "live_data.out"
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Import config
sys.path.insert(0, str(BASE_DIR))
try:
    import config
except ImportError:
    print("ERROR: config.py not found!")
    print("Make sure config.py exists in the same folder as run.py")
    sys.exit(1)


def print_banner():
    """Print the startup banner."""
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║     ██████╗ ██████╗ ██╗██╗   ██╗███████╗ ██████╗ ██╗   ██╗       ║")
    print("║     ██╔══██╗██╔══██╗██║██║   ██║██╔════╝██╔════╝ ██║   ██║       ║")
    print("║     ██║  ██║██████╔╝██║██║   ██║█████╗  ██║  ███╗██║   ██║       ║")
    print("║     ██║  ██║██╔══██╗██║╚██╗ ██╔╝██╔══╝  ██║   ██║██║   ██║       ║")
    print("║     ██████╔╝██║  ██║██║ ╚████╔╝ ███████╗╚██████╔╝╚██████╔╝       ║")
    print("║     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝ ╚═════╝  ╚═════╝        ║")
    print("║                                                                  ║")
    print("║              IoT Driver Safety Monitoring System                 ║")
    print("║                      ECE508 Fall 2025                            ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()


def print_config():
    """Print current configuration."""
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│                    CURRENT CONFIGURATION                        │")
    print("├─────────────────────────────────────────────────────────────────┤")
    print(f"│  WiFi SSID:        {config.WIFI_SSID:<43} │")
    print(f"│  G-Number:         {config.G_NUMBER:<43} │")
    print(f"│  Speed Limit:      {config.SPEED_DANGER:<43} km/h │")
    print(f"│  Accel Threshold:  {config.ACCEL_HARSH:<43} g │")
    print(f"│  Dashboard Port:   {config.DASHBOARD_PORT:<43} │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print()


def update_arduino_code():
    """Update Arduino .ino file with config settings."""
    print("[1/3] Updating Arduino code with your settings...")
    
    if not ARDUINO_FILE.exists():
        print(f"  ERROR: Arduino file not found at {ARDUINO_FILE}")
        return False
    
    # Read current Arduino code
    with open(ARDUINO_FILE, 'r') as f:
        code = f.read()
    
    # Replace WiFi credentials
    import re
    
    # Update SSID
    code = re.sub(
        r'const char\* ssid = "[^"]*";',
        f'const char* ssid = "{config.WIFI_SSID}";',
        code
    )
    
    # Update Password
    code = re.sub(
        r'const char\* pass = "[^"]*";',
        f'const char* pass = "{config.WIFI_PASSWORD}";',
        code
    )
    
    # Update G-Number
    code = re.sub(
        r'const char gNumber\[15\] = "[^"]*";',
        f'const char gNumber[15] = "{config.G_NUMBER}";',
        code
    )
    
    # Update Speed Danger threshold
    code = re.sub(
        r'float SPEED_DANGER = [\d.]+;',
        f'float SPEED_DANGER = {config.SPEED_DANGER};',
        code
    )
    
    # Update Acceleration threshold
    code = re.sub(
        r'float ACCEL_HARSH = [\d.]+;',
        f'float ACCEL_HARSH = {config.ACCEL_HARSH};',
        code
    )
    
    # Update scoring values
    code = re.sub(
        r'int SCORE_SPEEDING = -?\d+;',
        f'int SCORE_SPEEDING = {config.SCORE_SPEEDING};',
        code
    )
    
    code = re.sub(
        r'int SCORE_HARSH = -?\d+;',
        f'int SCORE_HARSH = {config.SCORE_HARSH};',
        code
    )
    
    # Write updated code
    with open(ARDUINO_FILE, 'w') as f:
        f.write(code)
    
    print("  ✓ Arduino code updated successfully!")
    print(f"  ✓ File: {ARDUINO_FILE}")
    print()
    print("  NEXT STEP: Open Arduino IDE and upload the code to your board.")
    print()
    return True


def update_telegraf_config():
    """Update Telegraf config with correct paths and G-number."""
    print("[2/3] Updating Telegraf configuration...")
    
    # Ensure data directories exist
    DATA_DIR.mkdir(exist_ok=True)
    HISTORY_DIR.mkdir(exist_ok=True)
    
    # Archive existing live data if it exists
    if LIVE_DATA_FILE.exists() and LIVE_DATA_FILE.stat().st_size > 0:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive_file = HISTORY_DIR / f"session_{timestamp}.out"
        shutil.move(str(LIVE_DATA_FILE), str(archive_file))
        print(f"  ✓ Previous session archived to: {archive_file.name}")
    
    # Create fresh live data file
    LIVE_DATA_FILE.touch()
    
    # Generate Telegraf config
    telegraf_config = f'''# Telegraf Configuration for DriveGuard IoT System
# Auto-generated by run.py - Do not edit manually

[global_tags]
  project = "driveguard"
  team = "team4"
  student = "{config.G_NUMBER}"

[agent]
  interval = "10s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  collection_jitter = "0s"
  flush_interval = "10s"
  flush_jitter = "0s"
  precision = "0s"
  hostname = ""
  omit_hostname = false

# ==================== MQTT INPUT ====================
[[inputs.mqtt_consumer]]
  servers = ["tcp://{config.MQTT_SERVER}:{config.MQTT_PORT}"]
  
  topics = [
    "ece508/team4/{config.G_NUMBER}/driveguard/#"
  ]
  
  username = "{config.MQTT_USER}"
  password = "{config.MQTT_PASSWORD}"
  
  qos = 0
  connection_timeout = "30s"
  client_id = "telegraf_driveguard_{config.G_NUMBER}"
  data_format = "json"
  topic_tag = "topic"

# ==================== OUTPUT TO FILE ====================
[[outputs.file]]
  files = ["stdout", "{LIVE_DATA_FILE.as_posix()}"]
  data_format = "influx"

# ==================== PROCESSING ====================
[[processors.parser]]
  parse_fields = ["text"]
  merge = "override"
  data_format = "json"
  namepass = ["*batch_data*"]

[[processors.parser]]
  parse_fields = ["text"]
  merge = "override"
  data_format = "json"
  namepass = ["*alert*"]

[[processors.parser]]
  parse_fields = ["text"]
  merge = "override"
  data_format = "json"
  namepass = ["*status*"]
'''
    
    TELEGRAF_DIR.mkdir(exist_ok=True)
    with open(TELEGRAF_CONF, 'w') as f:
        f.write(telegraf_config)
    
    print(f"  ✓ Telegraf config updated!")
    print(f"  ✓ Live data: {LIVE_DATA_FILE}")
    print(f"  ✓ History: {HISTORY_DIR}")
    print()
    return True


def find_telegraf():
    """Find Telegraf executable."""
    # Check common locations
    possible_paths = [
        TELEGRAF_DIR / "telegraf.exe",
        TELEGRAF_DIR / "telegraf",
        Path("C:/Program Files/InfluxData/telegraf/telegraf.exe"),
        Path("C:/telegraf/telegraf.exe"),
        Path("/usr/bin/telegraf"),
        Path("/usr/local/bin/telegraf"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Check if in PATH
    telegraf_cmd = shutil.which("telegraf")
    if telegraf_cmd:
        return Path(telegraf_cmd)
    
    return None


def start_telegraf():
    """Start Telegraf in background."""
    print("[3/3] Starting Telegraf...")
    
    telegraf_exe = find_telegraf()
    
    if not telegraf_exe:
        print()
        print("  ⚠ Telegraf not found!")
        print()
        print("  To install Telegraf:")
        print("  1. Download from: https://portal.influxdata.com/downloads/")
        print("  2. Extract telegraf.exe to the 'telegraf' folder")
        print(f"     Expected location: {TELEGRAF_DIR / 'telegraf.exe'}")
        print()
        print("  Dashboard will still run, but no new data will be collected.")
        print()
        return None
    
    print(f"  ✓ Found Telegraf: {telegraf_exe}")
    
    # Start Telegraf
    try:
        if sys.platform == "win32":
            # Windows: start in new console window
            process = subprocess.Popen(
                [str(telegraf_exe), "--config", str(TELEGRAF_CONF)],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Linux/Mac: start in background
            process = subprocess.Popen(
                [str(telegraf_exe), "--config", str(TELEGRAF_CONF)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print(f"  ✓ Telegraf started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"  ERROR starting Telegraf: {e}")
        return None


def start_dashboard():
    """Start the Flask dashboard."""
    print()
    print("Starting Dashboard...")
    print(f"  ✓ URL: http://localhost:{config.DASHBOARD_PORT}")
    print()
    print("═" * 66)
    print("  Press Ctrl+C to stop everything")
    print("═" * 66)
    print()
    
    # Open browser
    if config.AUTO_OPEN_BROWSER:
        time.sleep(1)
        webbrowser.open(f"http://localhost:{config.DASHBOARD_PORT}")
    
    # Set environment variable for data file path
    os.environ["DRIVEGUARD_DATA_FILE"] = str(LIVE_DATA_FILE)
    os.environ["DRIVEGUARD_HISTORY_DIR"] = str(HISTORY_DIR)
    
    # Import and run Flask app
    sys.path.insert(0, str(DASHBOARD_DIR))
    from app import app
    
    try:
        app.run(host='0.0.0.0', port=config.DASHBOARD_PORT, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down...")


def show_help():
    """Show help message."""
    print("""
DriveGuard - IoT Driver Safety Monitoring System

USAGE:
    python run.py              Start Telegraf + Dashboard (normal operation)
    python run.py --update     Update Arduino code with settings from config.py
    python run.py --dashboard  Start only the dashboard (no Telegraf)
    python run.py --help       Show this help message

SETUP STEPS:
    1. Edit config.py with your WiFi credentials and settings
    2. Run: python run.py --update
    3. Open Arduino IDE and upload the code to your board
    4. Run: python run.py
    5. Open http://localhost:5000 in your browser

FILES:
    config.py                  Your settings (edit this!)
    arduino/                   Arduino code (upload via Arduino IDE)
    dashboard/                 Web dashboard
    telegraf/                  Telegraf configuration
    data/live_data.out         Current session data
    data/history/              Previous sessions
""")


def main():
    """Main entry point."""
    print_banner()
    
    # Parse arguments
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        show_help()
        return
    
    if "--update" in args:
        print_config()
        update_arduino_code()
        print()
        print("Done! Now open Arduino IDE and upload the code to your board.")
        return
    
    if "--dashboard" in args:
        print_config()
        start_dashboard()
        return
    
    # Normal operation: start everything
    print_config()
    
    update_telegraf_config()
    telegraf_process = start_telegraf()
    
    try:
        start_dashboard()
    finally:
        # Cleanup
        if telegraf_process:
            print("Stopping Telegraf...")
            telegraf_process.terminate()
            telegraf_process.wait(timeout=5)


if __name__ == "__main__":
    main()
