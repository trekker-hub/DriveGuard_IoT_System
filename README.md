# DriveGuard - IoT Driver Safety Monitoring System

A comprehensive IoT system for monitoring driving behavior using Arduino Nano 33 IoT with GPS tracking, IMU sensors, and real-time cloud visualization.

![DriveGuard Dashboard](assets/dashboard_preview.png)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Configure Your Settings
Edit `config.py` with your WiFi credentials:

```python
WIFI_SSID = "YourWiFiName"
WIFI_PASSWORD = "YourWiFiPassword"
G_NUMBER = "Gxxxx6647"
SPEED_DANGER = 120.0  # km/h
```

### Step 2: Update & Upload Arduino Code
```bash
python run.py --update
```
Then open Arduino IDE → Open `arduino/DriveGuard_Shiftr_Production/DriveGuard_Shiftr_Production.ino` → Upload to board

### Step 3: Start the Dashboard
```bash
python run.py
```
Open http://localhost:5000 in your browser 🎉

---

## 📁 Project Structure

```
DriveGuard/
├── config.py                    ← EDIT THIS (your settings)
├── run.py                       ← RUN THIS (starts everything)
├── arduino/
│   └── DriveGuard_Shiftr_Production/
│       ├── DriveGuard_Shiftr_Production.ino
│       ├── myiot33_library.cpp
│       └── myiot33_library.h
├── dashboard/
│   ├── app.py
│   └── templates/
│       └── dashboard.html
├── telegraf/
│   ├── telegraf.exe             ← Download this (see below)
│   └── telegraf_driveguard.conf
├── data/
│   ├── live_data.out            ← Current session
│   └── history/                 ← Previous sessions
└── README.md
```

---

## 🔧 Requirements

### Software
- Python 3.8+ with Flask (`pip install flask`)
- Arduino IDE 2.0+
- Telegraf (optional, for data collection)

### Hardware
- Arduino Nano 33 IoT
- BN220 GPS Module
- SSD1306 OLED Display (128x64, I2C)
- LEDs: Red, Yellow, Green
- Buzzer

### Arduino Libraries (Install via Arduino IDE)
- WiFiNINA
- Arduino_LSM6DS3
- PubSubClient
- Adafruit_SSD1306
- Adafruit_GFX
- SSD1306Ascii

---

## 📥 Telegraf Installation

Telegraf collects data from the MQTT broker. **Optional but recommended.**

### Windows
1. Download from: https://portal.influxdata.com/downloads/
2. Select: Telegraf → Windows → AMD64
3. Extract `telegraf.exe` to the `telegraf/` folder

### Mac
```bash
brew install telegraf
```

### Linux
```bash
sudo apt install telegraf
```

---

## 🖥️ Commands

| Command | Description |
|---------|-------------|
| `python run.py` | Start Telegraf + Dashboard |
| `python run.py --update` | Update Arduino code with your config |
| `python run.py --dashboard` | Start only the dashboard |
| `python run.py --help` | Show help |

---

## 📊 Dashboard Features

- **Real-time Charts**: Speed, Score, Acceleration over time
- **Live Statistics**: Current score, max speed, total readings
- **Alert History**: Speeding and harsh driving events
- **Score Distribution**: Histogram of driving scores
- **Session History**: View previous driving sessions

---

## 🔌 Hardware Wiring

| Component | Arduino Pin |
|-----------|-------------|
| GPS TX | D0 (RX) |
| GPS RX | D1 (TX) |
| Red LED | D2 |
| Yellow LED | D3 |
| Green LED | D4 |
| Buzzer | D6 |
| GPS Status Green | D7 |
| GPS Status Red | D8 |
| OLED SDA | A4 |
| OLED SCL | A5 |

---

## 📡 MQTT Topics

Subscribe to these topics on Shiftr.io to see your data:

```
ece508/team4/{G_NUMBER}/driveguard/batch_data    # Sensor readings
ece508/team4/{G_NUMBER}/driveguard/alert_speed   # Speeding alerts
ece508/team4/{G_NUMBER}/driveguard/alert_harsh   # Harsh driving alerts
ece508/team4/{G_NUMBER}/driveguard/status        # System status
```

---

## 🎯 Scoring System

| Score | Grade | Status |
|-------|-------|--------|
| 90-100 | A | Excellent |
| 80-89 | B | Good |
| 70-79 | C | Fair |
| 60-69 | D | Poor |
| 0-59 | F | Failing |

**Penalties:**
- Speeding (>120 km/h): -5 points
- Harsh acceleration (>0.5g): -3 points

**Bonus:**
- 10 minutes smooth driving: +1 point

---

## 🐛 Troubleshooting

### "No data on dashboard"
1. Check Arduino is powered and connected to WiFi
2. Verify Telegraf is running (check the console window)
3. Make sure `live_data.out` exists in `data/` folder

### "MQTT upload failed"
- The Arduino code includes `setBufferSize(1024)` fix
- If still failing, check WiFi connection

### "Telegraf not found"
- Download telegraf.exe and place in `telegraf/` folder
- Or install system-wide and it will be auto-detected

### "Arduino code won't compile"
- Install all required libraries via Arduino Library Manager
- Board: Arduino Nano 33 IoT

---

## 📝 License

MIT License - ECE508 Fall 2025

---

## 👤 Author

**Tarek** - ECE508 IoT Final Project
