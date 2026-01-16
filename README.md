# ☁️ RFID Attendance System

**Course:** CPC357 IoT Architecture & Smart Applications  
**University:** Universiti Sains Malaysia (USM) \
**Assignment:** 2 \
**Semester:** 2025/2026 

## 👥 Group Members
1. **Nurul Liyana Binti Idris** (160438)
2. **Nurin Farah Izzati Binti Muhd Rusdi** (160406)

---

## 📖 Project Overview
A smart attendance tracking system that integrates physical RFID hardware with Google Cloud Platform (GCP). This project scans student ID cards using an ESP32 microcontroller, processes the data on a Cloud VM via MQTT and visualizes real-time attendance logs on a modern web dashboard.

### 🚀 Key Features
* **Real-time Authentication:** Instant audio-visual feedback (Buzzer) for valid/invalid cards.
* **Cloud Architecture:** Powered by Google Cloud Compute Engine (VM) and Cloud SQL.
* **MQTT Messaging:** Fast, lightweight communication using the Mosquitto broker.
* **Live Web Dashboard:** A responsive Flask-based interface to monitor entry logs.
* **Timezone Aware:** Automatically logs events in Malaysia Time (GMT+8).
* **Security:** Differentiates between active students, suspended users and intruders.

---

## 🛠️ Tech Stack

### **Hardware**
* **Microcontroller:** Cytron Maker Feather AIoT S3 (ESP32-S3)
* **Input:** RC522 RFID Reader Module (SPI)
* **Output:** Piezo Buzzer
* **Power:** USB-C

### **Software & Cloud**
* **Cloud Provider:** Google Cloud Platform (GCP)
* **Broker:** Eclipse Mosquitto (MQTT)
* **Database:** Google Cloud SQL (MySQL 8.0)
* **Backend:** Python 3 (Paho-MQTT, PyMySQL, Pytz)
* **Frontend:** Flask (Python Web Framework), Bootstrap 5
* **Firmware:** C++ (Arduino IDE)

---

## 📂 Project Structure

| File Name | Description | Location |
| :--- | :--- | :--- |
| `Attendance.ino` | C++ code for ESP32 to scan cards and handle MQTT. | Hardware |
| `attendance_logic.py` | Python script that acts as the system "brain" (MQTT <-> SQL). | Cloud VM |
| `dashboard.py` | Flask web application for the visual dashboard. | Cloud VM |

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

* **Buzzer:** GPIO 6 (Positive leg)
* **Power Enable:** GPIO 11 

---

## ⚙️ Deployment Guide

### Phase 1: Google Cloud Platform (GCP) Setup

1.  **Create VM Instance:**
    * Go to **Compute Engine** > **VM Instances**.
    * Create a new instance (e.g., `Attendance-server`).
    * OS: **Ubuntu 20.04 LTS**.
    * Firewall: Allow HTTP/HTTPS.
2.  **Create SQL Database:**
    * Go to **SQL** and create a **MySQL** instance.
    * Go to **Connections** > **Networking**.
    * Add your VM's **External IP** to the "Authorized Networks" list.
3.  **Configure Firewall:**
    * Go to **VPC Network** > **Firewall**.
    * Create a rule to allow **Ingress** on ports:
        * `1883` (MQTT)
        * `5000` (Flask Dashboard)

### Phase 2: Backend Environment (On VM)

SSH into your VM and run the following commands to set up the environment:

1.  **Update System & Install Dependencies:**
    ```bash
    sudo apt update
    sudo apt install python3-pip mosquitto mosquitto-clients -y
    ```

2.  **Install Required Python Libraries:**
    ```bash
    pip3 install paho-mqtt pymysql flask pytz
    ```

3.  **Verify MQTT Broker:**
    ```bash
    sudo service mosquitto status
    # Output should show: active (running)
    ```

### Phase 3: Database Schema

Connect to your SQL instance and run these queries to create the necessary tables:

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

-- Insert dummy student
INSERT INTO students (uid, name) VALUES ('C1 2A 4B 99', 'Test Student');
```

### Phase 4: Hardware & Firmware Setup

1.  **Install Arduino IDE** & Drivers for your ESP32 board.
2.  **Install Board Definitions:**
    * Open Arduino IDE and go to **File** > **Preferences**.
    * Add this URL to "Additional Boards Manager URLs": \
        `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
    * Go to **Tools** > **Board** > **Boards Manager**, search for `esp32` by Espressif Systems and click **Install**.
3.  **Install Libraries:**
    * Go to **Sketch** > **Include Library** > **Manage Libraries**.
    * Search for and install the following:
        * `MFRC522` by GithubCommunity
        * `PubSubClient` by Nick O'Leary
4.  **Configure & Upload:**
    * Open the `attendance.ino` file.
    * Update the `ssid`, `password`, and `mqtt_server` variables with your specific details (use the VM's External IP for the MQTT server).
    * Select Board: **"Cytron Maker Feather AIoT S3"**.
    * Select the correct **Port**.
    * Click **Upload**.

---

## ▶️ How to Run the System

To see the system in action, you need to run two scripts simultaneously on your Cloud VM.

### 1. Start the Logic Engine
This script acts as the "brain," listening for card scans and checking the database.
```bash
python3 attendance_logic.py
```

### 2. Start the Web Dashboard
Open a new SSH terminal window and run the dashboard server.
```bash
python3 dashboard.py
```

### 3. Usage Steps
1. Open your web browser and navigate to: `http://<YOUR_VM_EXTERNAL_IP>:5000`
2. Scan an RFID card on the ESP32 hardware.
3. Valid Card:
    * Hardware: Buzzer plays a success melody.
    * Dashboard: Updates immediately with the student's name and "Access Granted" (Green).

4. Invalid Card:
    * Hardware: Buzzer beeps 3 times (error tone).
    * Dashboard: Logs "Unknown Card" with "Access Denied" (Red).
