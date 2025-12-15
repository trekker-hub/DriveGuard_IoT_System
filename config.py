# LLM Prompt:
# "Create a Python configuration file for the DriveGuard web dashboard that:
# - Stores WiFi credentials
# - Contains Shiftr.io MQTT broker settings (host, port, username, password)
# - Defines MQTT topics for the system
# - Uses the topic structure: ece508/team4/Gxxxx6647/driveguard/#
# - Is easy for users to edit with clear comments"
#
#

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     DRIVEGUARD CONFIGURATION                                 ║
║                     Edit your settings below                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# WIFI SETTINGS (Required)
# =============================================================================
WIFI_SSID = "WIFI NAME"           # Your WiFi network name
WIFI_PASSWORD = "WIFI PASSWORD"   # Your WiFi password

# =============================================================================
# STUDENT INFO (Required for ECE508)
# =============================================================================
G_NUMBER = "Gxxxx6647"               # Your G-Number

# =============================================================================
# DRIVING THRESHOLDS (Adjust as needed)
# =============================================================================
SPEED_DANGER = 120.0                 # Speed limit in km/h (triggers alert above this)
ACCEL_HARSH = 0.4                    # Acceleration threshold in g (triggers alert above this)

# =============================================================================
# SCORING PENALTIES (Optional - adjust scoring sensitivity)
# =============================================================================
SCORE_SPEEDING = -5                  # Points lost per speeding event
SCORE_HARSH = -3                     # Points lost per harsh driving event

# =============================================================================
# MQTT SETTINGS (Usually no need to change)
# =============================================================================
MQTT_SERVER = "public.cloud.shiftr.io"
MQTT_PORT = 1883
MQTT_USER = "public"
MQTT_PASSWORD = "public"

# =============================================================================
# DASHBOARD SETTINGS
# =============================================================================
DASHBOARD_PORT = 5000                # Web dashboard runs on this port
AUTO_OPEN_BROWSER = True             # Open browser automatically when starting
