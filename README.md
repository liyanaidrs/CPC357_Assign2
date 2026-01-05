# CPC357 ASSIGNMENT 2

**Course:** CPC357 IoT Architecture & Smart Applications  
**University:** Universiti Sains Malaysia (USM)  
**Semester:** 2025/2026  

## 👥 Group Members
1. **Nurul Liyana Binti Idris** (160438)
2. **Nurin Farah Izzati Binti Muhd Rusdi** (160406)

# ☁️ Cloud-Based IoT Attendance System

A smart attendance tracking system that integrates physical RFID hardware with Google Cloud Platform. This project scans student ID cards using an ESP32 microcontroller, processes the data on a Cloud VM, and visualizes real-time attendance logs on a web dashboard.

## 🚀 Features

* **Real-time Authentication:** Instant feedback (Buzzer & LED) for valid or invalid cards.
* **Cloud Architecture:** Powered by Google Cloud Compute Engine (VM) and Cloud SQL.
* **MQTT Messaging:** Fast, lightweight communication between hardware and the cloud using Mosquitto.
* **Live Web Dashboard:** A modern, responsive Flask-based dashboard to view entry logs and statistics.
* **Timezone Aware:** Automatically logs events in Malaysia Time (GMT+8).
* **Security:** Differentiates between active students, suspended users, and unknown intruders.

---

## 🛠️ Tech Stack

### **Hardware**
* **Microcontroller:** Cytron Maker Feather AIoT S3 (ESP32-S3)
* **Input:** RC522 RFID Reader Module (SPI)
* **Output:** Piezo Buzzer, LED Indicator
* **Power:** USB-C / LiPo Battery

### **Software & Cloud**
* **Cloud Provider:** Google Cloud Platform (GCP)
* **Broker:** Eclipse Mosquitto (MQTT)
* **Database:** Google Cloud SQL (MySQL)
* **Backend:** Python 3 (Paho-MQTT, PyMySQL)
* **Frontend:** Flask (Python), Bootstrap 5, Jinja2
* **Firmware:** C++ (Arduino IDE)

---

## 🔌 Circuit Connection

**Board:** Cytron Maker Feather AIoT S3

| RC522 Pin | Feather S3 Pin | Function |
| :--- | :--- | :--- |
| **SDA (SS)** | GPIO 7 | Chip Select |
| **SCK** | GPIO 17 | SPI Clock |
| **MOSI** | GPIO 8 | Master Out Slave In |
| **MISO** | GPIO 18 | Master In Slave Out |
| **RST** | GPIO 4 | Reset |
| **3.3V** | 3.3V | Power |
| **GND** | GND | Ground |

* **Buzzer:** GPIO 6
* **LED:** GPIO 5
* **Power Enable:** GPIO 11 (Must be set HIGH in code to enable 3.3V rail)

---

## ⚙️ Setup & Installation

### 1. Cloud Setup (Google Cloud Platform)
1.  **VM Instance:** Set up an Ubuntu VM on Compute Engine.
2.  **SQL Database:** Create a Cloud SQL instance (MySQL) and whitelist your VM's IP.
3.  **Firewall:** Allow ingress traffic on ports `1883` (MQTT) and `5000` (Dashboard).

### 2. Database Schema
Run the following SQL commands to set up your tables:

```sql
CREATE DATABASE attendance_db;
USE attendance_db;

CREATE TABLE students (
    uid VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    is_active INT DEFAULT 1
);

CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(50),
    status VARCHAR(20),
    timestamp DATETIME
); 
```

### 3. Backend Setup (On Google Cloud VM)
SSH into your VM instance and execute the following commands to install the MQTT Broker and Python dependencies:

1.  **Update and Install System Packages:**
    ```bash
    sudo apt update
    sudo apt install python3-pip mosquitto mosquitto-clients -y
    ```

2.  **Install Python Libraries:**
    ```bash
    pip3 install paho-mqtt pymysql flask pytz
    ```

3.  **Verify Mosquitto is Running:**
    ```bash
    sudo service mosquitto status
    ```
    *(It should say "active (running)")*

### 4. Firmware Upload (ESP32)
1.  **Install Arduino IDE:** Download and install the latest version.
2.  **Install Board Definitions:**
    * Go to **File** > **Preferences**.
    * Add this URL to "Additional Boards Manager URLs":
        `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
    * Go to **Tools** > **Board** > **Boards Manager**, search for `esp32` by Espressif Systems, and install it.
3.  **Install Libraries:**
    * Go to **Sketch** > **Include Library** > **Manage Libraries**.
    * Search for and install:
        * `MFRC522` by GithubCommunity
        * `PubSubClient` by Nick O'Leary
4.  **Configure Code:**
    Open the `.ino` file and update these lines with your details:
    ```cpp
    const char* ssid = "YOUR_WIFI_NAME";
    const char* password = "YOUR_WIFI_PASSWORD";
    const char* mqtt_server = "YOUR_VM_EXTERNAL_IP"; // e.g., 34.66.x.x
    ```
5.  **Upload:**
    * Select Board: **"Adafruit Feather ESP32-S3 No PSRAM"** (Compatible with Cytron Feather S3).
    * Select Port: The COM port your device is connected to.
    * Click **Upload**.


## ▶️ How to Run

To run the full system, you need two terminal windows open on your VM.

### 1. Start the Logic Engine (The "Brain")
This script listens for card scans, checks the database, and sends commands back to the ESP32.
```bash
python3 attendance_logic.py
```
### 2. Start the Web Dashboard
Open a new SSH window (or use screen/tmux) and run:
```bash
python3 dashboard.py
```
### 3. Access the System
* Open your web browser.
* Go to: http://<YOUR_VM_EXTERNAL_IP>:5000
* Scan an RFID card on the hardware.
* Watch the dashboard update in real-time!

