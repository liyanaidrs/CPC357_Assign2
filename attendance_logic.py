"""
================================================================================
                CLOUD RFID ATTENDANCE SYSTEM - SERVER LOGIC
================================================================================

Server logic for cloud-based RFID attendance system. Receives UID scans from
ESP32 via MQTT, validates against MySQL database, logs attendance with Malaysia
timezone (GMT+8) and sends validation feedback to devices.

MQTT Topics:
- Subscribe: "attendance/scan" (receives UID from ESP32)
- Publish: "attendance/feedback" (sends validation result)

================================================================================
"""

import paho.mqtt.client as mqtt
import pymysql
import json
import datetime
import pytz

# ============================================================================
# CONFIGURATION
# ============================================================================
# Database Configuration
DB_HOST = '34.29.88.122'
DB_USER = 'liyana'
DB_PASS = '123456'
DB_NAME = 'attendance_db'

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_SCAN = "attendance/scan"
MQTT_TOPIC_FEEDBACK = "attendance/feedback"

# Timezone & Status Codes
MALAYSIA_TIMEZONE = 'Asia/Kuala_Lumpur'
STATUS_PRESENT = 'Present'
STATUS_DENIED = 'Denied'
STATUS_SUSPENDED = 'Suspended'

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_db_connection():
    """Establish MySQL database connection with autocommit enabled."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        return connection
    except pymysql.Error as e:
        print(f"❌ DATABASE CONNECTION ERROR: {e}")
        raise

def validate_student(cursor, uid):
    """Check if UID exists in students table and return student record."""
    query = "SELECT * FROM students WHERE uid = %s"
    cursor.execute(query, (uid,))
    return cursor.fetchone()

def log_attendance(cursor, uid, status, timestamp):
    """Record attendance event in logs table."""
    insert_query = "INSERT INTO logs (uid, status, timestamp) VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (uid, status, timestamp))
    return cursor.lastrowid

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_malaysia_timestamp():
    """Generate current timestamp in Malaysia timezone (GMT+8)."""
    malaysia_tz = pytz.timezone(MALAYSIA_TIMEZONE)
    now_malaysia = datetime.datetime.now(malaysia_tz)
    return now_malaysia.strftime('%Y-%m-%d %H:%M:%S')

def send_feedback(client, status, name=None):
    """Publish validation result back to ESP32 via MQTT."""
    response = {"status": status}
    if name:
        response["name"] = name
    
    json_payload = json.dumps(response)
    client.publish(MQTT_TOPIC_FEEDBACK, json_payload)
    print(f"📤 FEEDBACK SENT: {json_payload}")

# ============================================================================
# MQTT CALLBACK HANDLERS
# ============================================================================

def on_message(client, userdata, msg):
    """
    Handle incoming RFID scan messages from ESP32.
    Process: Decode payload → Validate UID → Log attendance → Send feedback
    """
    try:
        # Decode and parse JSON payload
        payload_bytes = msg.payload.decode('utf-8')
        print(f"\n{'='*70}")
        print(f"[📥 RECEIVED] {payload_bytes}")
        
        data = json.loads(payload_bytes)
        uid = data.get("uid")
        
        if not uid:
            print("❌ ERROR: UID not found in payload")
            send_feedback(client, "invalid")
            return
        
        print(f"[🔍 SCANNING] UID: {uid}")
        
        # Connect to database and validate
        conn = get_db_connection()
        
        try:
            with conn.cursor() as cursor:
                timestamp = get_malaysia_timestamp()
                student = validate_student(cursor, uid)
                
                # CASE 1: Valid student found
                if student:
                    name = student['name']
                    account_status = student.get('status', 'Active')
                    
                    # Check if account is suspended
                    if account_status == STATUS_SUSPENDED:
                        print(f"⚠️  SUSPENDED: {name} at {timestamp}")
                        log_attendance(cursor, uid, STATUS_SUSPENDED, timestamp)
                        send_feedback(client, "suspended", name)
                    
                    # Account is active - grant access
                    else:
                        print(f"✅ ACCESS GRANTED: {name} at {timestamp}")
                        log_attendance(cursor, uid, STATUS_PRESENT, timestamp)
                        send_feedback(client, "valid", name)
                
                # CASE 2: Unknown UID
                else:
                    print(f"❌ ACCESS DENIED: Unknown UID at {timestamp}")
                    log_attendance(cursor, uid, STATUS_DENIED, timestamp)
                    send_feedback(client, "invalid")
        
        finally:
            conn.close()
            print(f"{'='*70}\n")
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON PARSE ERROR: {e}")
        send_feedback(client, "invalid")
    
    except pymysql.Error as e:
        print(f"❌ DATABASE ERROR: {e}")
        send_feedback(client, "invalid")
    
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        send_feedback(client, "invalid")

def on_connect(client, userdata, flags, rc):
    """Callback when MQTT client connects to broker."""
    if rc == 0:
        print("✅ Connected to MQTT broker")
        print(f"📡 Subscribing to: {MQTT_TOPIC_SCAN}")
        client.subscribe(MQTT_TOPIC_SCAN)
    else:
        print(f"❌ Connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    """Callback when MQTT client disconnects from broker."""
    if rc != 0:
        print(f"⚠️  Unexpected disconnection (code {rc}). Reconnecting...")
    else:
        print("🔌 Disconnected from MQTT broker")

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Initialize MQTT client and start message processing loop."""
    print("="*70)
    print("  CLOUD RFID ATTENDANCE SYSTEM - SERVER STARTING")
    print("="*70)
    print(f"Database: {DB_HOST}")
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Timezone: {MALAYSIA_TIMEZONE} (GMT+8)")
    print("="*70)
    
    # Create and configure MQTT client
    client = mqtt.Client(client_id="AttendanceServer", clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        print("\n🔄 Connecting to MQTT broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        
        print("✅ SERVER READY - Waiting for RFID scans...\n")
        client.loop_forever()
    
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested")
        client.disconnect()
        print("👋 Goodbye!")
    
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        client.disconnect()

if __name__ == "__main__":
    main()

"""
================================================================================
Database Schema Required:

1. students table:
   - uid VARCHAR(50) PRIMARY KEY
   - name VARCHAR(100) NOT NULL
   - status VARCHAR(20) DEFAULT 'Active'

2. logs table:
   - id INT PRIMARY KEY AUTO_INCREMENT
   - uid VARCHAR(50)
   - status VARCHAR(20)
   - timestamp DATETIME
================================================================================
"""