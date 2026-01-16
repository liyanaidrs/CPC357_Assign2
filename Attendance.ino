/*
 * ============================================================================
 *                    CLOUD RFID ATTENDANCE SYSTEM
 * ============================================================================
 */

// ============================================================================
// LIBRARY DEPENDENCIES
// ============================================================================
#include <SPI.h>           // Serial Peripheral Interface for RFID communication
#include <MFRC522.h>       // MFRC522 RFID reader library
#include <WiFi.h>          // ESP32 WiFi connectivity library
#include <PubSubClient.h>  // MQTT client library for pub/sub messaging

// ============================================================================
// SECTION 1: NETWORK CONFIGURATION
// ============================================================================
/**
 * WiFi Network Credentials
 */
const char* ssid = "NL";                      // WiFi network name (SSID)
const char* password = "haechan123";          // WiFi network password

/**
 * MQTT Broker Configuration
 * The IP address of the Google Cloud VM instance running Mosquitto broker
 */
const char* mqtt_server = "136.111.62.120";   // Cloud server external IP address

// ============================================================================
// SECTION 2: HARDWARE PIN CONFIGURATION
// ============================================================================
/**
 * SPI Interface Pins for MFRC522 RFID Reader
 */
#define SCK_PIN   17   // Serial Clock
#define MISO_PIN  18   // Master In Slave Out 
#define MOSI_PIN  8    // Master Out Slave In
#define SS_PIN    7    // Slave Select (SDA)
#define RST_PIN   4    // Reset Pin

/**
 * Output Components
 */
#define BUZZER    6    // Onboard piezo buzzer for audio feedback

/**
 * Power Management Pin
 */
#define POWER_PIN 11   // Enables external sensor power supply

// ============================================================================
// SECTION 3: GLOBAL OBJECT INSTANTIATION
// ============================================================================
MFRC522 mfrc522(SS_PIN, RST_PIN);  // RFID reader object with pin configuration
WiFiClient espClient;              // WiFi client for network communication
PubSubClient client(espClient);    // MQTT client using WiFi connection

/**
 * MQTT Topic Definitions
 * These topics follow the pub/sub pattern for bidirectional communication
 */
const char* topic_scan = "attendance/scan";         // Publishing channel (ESP32 → Cloud)
const char* topic_feedback = "attendance/feedback"; // Subscription channel (Cloud → ESP32)

// ============================================================================
// SECTION 4: WIFI INITIALIZATION FUNCTION
// ============================================================================
/**
 * Function: setup_wifi()
 */
void setup_wifi() {
  delay(10);  // Brief delay for stability
  
  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  // Begin WiFi connection attempt
  WiFi.begin(ssid, password);

  // Wait for connection establishment
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");  // Progress indicator
  }
  
  // Connection successful - display network information
  Serial.println("\nWiFi connected successfully!");
  Serial.print("Device IP Address: ");
  Serial.println(WiFi.localIP());
}

// ============================================================================
// SECTION 5: MQTT CALLBACK HANDLER
// ============================================================================

void callback(char* topic, byte* payload, unsigned int length) {
  // Convert byte payload to String for easier processing
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  // Log received message to Serial Monitor
  Serial.print("Cloud Reply: ");
  Serial.println(message);

  // -------------------------------------------------------------------------
  // Access Control Logic
  // -------------------------------------------------------------------------
  
  // CASE 1: ACCESS DENIED
  // Triggered when UID is invalid or account is suspended
  if (message.indexOf("invalid") >= 0 || message.indexOf("suspended") >= 0) {
    Serial.println(">> ACCESS DENIED ❌");
    
    // Audio Feedback: Three short error beeps
    // Low frequency (200 Hz) indicates error condition
    for (int i = 0; i < 3; i++) {
      tone(BUZZER, 200, 100);   // 200 Hz tone for 100ms
      delay(200);               // 200ms interval between beeps
    }
  } 
  
  // CASE 2: ACCESS GRANTED
  // Triggered when UID is valid and account is active
  else if (message.indexOf("valid") >= 0) {
    Serial.println(">> ACCESS GRANTED ✅");
    
    // Audio Feedback: Two-tone success melody
    // Ascending frequency pattern indicates successful operation
    tone(BUZZER, 1000, 150);    // First tone: 1000 Hz for 150ms
    delay(150);
    tone(BUZZER, 2000, 300);    // Second tone: 2000 Hz for 300ms (success confirmation)
  }
}

// ============================================================================
// SECTION 6: MQTT CONNECTION MANAGEMENT
// ============================================================================

void reconnect() {
  // Loop until connection is established
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    // Generate unique client identifier
    // Random hex suffix prevents ID conflicts with multiple devices
    String clientId = "FeatherS3-";
    clientId += String(random(0xffff), HEX);
    
    // Attempt connection to broker
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      
      // Resubscribe to feedback topic to receive server responses
      client.subscribe(topic_feedback); 
    } else {
      // Connection failed - log error and retry
      Serial.print("failed, rc=");
      Serial.print(client.state());  // Print connection state code
      Serial.println(" try again in 5 seconds");
      delay(5000);  // Wait before retry
    }
  }
}

// ============================================================================
// SECTION 7: SYSTEM INITIALIZATION (SETUP)
// ============================================================================

void setup() {
  // Initialize serial communication at 115200 baud for debugging
  Serial.begin(115200);
  
  // -------------------------------------------------------------------------
  // Step 1: Power Management Configuration
  // -------------------------------------------------------------------------
  // Enable 3.3V power rail for external sensors
  pinMode(POWER_PIN, OUTPUT);
  digitalWrite(POWER_PIN, HIGH);  // Turn on power supply
  delay(100);                     // Allow power to stabilize

  // -------------------------------------------------------------------------
  // Step 2: Output Device Configuration
  // -------------------------------------------------------------------------
  pinMode(BUZZER, OUTPUT);  // Configure buzzer pin as output

  // -------------------------------------------------------------------------
  // Step 3: SPI and RFID Initialization
  // -------------------------------------------------------------------------
  // Initialize SPI bus with custom pin configuration
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN);

  // Initialize MFRC522 RFID reader
  mfrc522.PCD_Init();
  
  // Set antenna gain to maximum for improved read range and reliability
  mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);

  // -------------------------------------------------------------------------
  // Step 4: Network Connectivity Setup
  // -------------------------------------------------------------------------
  setup_wifi();  // Establish WiFi connection
  
  // Configure MQTT client parameters
  client.setServer(mqtt_server, 1883);  // Set broker address and port
  client.setCallback(callback);         // Register message handler function

  // -------------------------------------------------------------------------
  // Step 5: System Ready Notification
  // -------------------------------------------------------------------------
  // Play short high-pitched beep to indicate successful initialization
  tone(BUZZER, 2000, 100);  // 2000 Hz tone for 100ms
  
  Serial.println("--- SYSTEM READY ---");
  Serial.println("Waiting for RFID cards...");
}

// ============================================================================
// SECTION 8: MAIN PROGRAM LOOP
// ============================================================================

void loop() {
  // -------------------------------------------------------------------------
  // Step 1: MQTT Connection Maintenance
  // -------------------------------------------------------------------------
  // Ensure active connection to broker; reconnect if disconnected
  if (!client.connected()) {
    reconnect();
  }
  
  // Process incoming MQTT messages and maintain connection
  client.loop();

  // -------------------------------------------------------------------------
  // Step 2: RFID Card Detection
  // -------------------------------------------------------------------------
  // Check if a new card is present in the reader's electromagnetic field
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;  // No card detected, skip to next loop iteration
  }
  
  // Attempt to read the card's serial number (UID)
  if (!mfrc522.PICC_ReadCardSerial()) {
    return;  // Read failed, skip to next loop iteration
  }

  // -------------------------------------------------------------------------
  // Step 3: UID Extraction and Formatting
  // -------------------------------------------------------------------------
  // Build UID string from byte array
  String content = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    // Add leading space and zero for single-digit hex values
    content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
    // Convert byte to hexadecimal string
    content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  
  // Normalize UID format: uppercase and trim whitespace
  content.toUpperCase();
  content.trim();

  // Log scanned UID to Serial Monitor
  Serial.print("Card Scanned - UID: ");
  Serial.println(content);

  // -------------------------------------------------------------------------
  // Step 4: Cloud Communication
  // -------------------------------------------------------------------------
  // Construct JSON payload for MQTT publish
  // Format: {"uid": "XX XX XX XX"}
  String payload = "{\"uid\": \"" + content + "\"}";
  
  // Publish UID to cloud server via MQTT
  client.publish(topic_scan, payload.c_str());
  Serial.println("UID sent to cloud for validation...");

  // -------------------------------------------------------------------------
  // Step 5: Card Communication Cleanup
  // -------------------------------------------------------------------------
  // Halt PICC (card) communication to prepare for next scan
  mfrc522.PICC_HaltA();
  
  // Stop encryption on PCD (reader) side
  mfrc522.PCD_StopCrypto1();
  
  // -------------------------------------------------------------------------
  // Step 6: Scan Cooldown Period
  // -------------------------------------------------------------------------
  // Wait 1 second before allowing next scan to prevent duplicate reads
  delay(1000);
}
