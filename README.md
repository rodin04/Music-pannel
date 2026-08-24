# Music-pannel
An automated smart-home music system that detects when someone enters the room via a door sensor and triggers music playback across a Python GUI and a web-based interface.

---



### Web interface 

<p>
  <img src="musik-panel-1.png" width="400" alt="Musik Panel 1" style="margin-right: 10px;" />
  <img src="musik-panel-2.png" width="400" alt="Musik Panel 2" />
  
</p>

### esp32 detector 

<p>
  <img src="musik-panel-3.png" width="400" alt="Musik Panel 1" style="margin-right: 10px;" />
</p>



## ✨ Features
- **Tailscale Control:** Control your music safely from anywhere using the Tailscale network.
- **ESP32 Sensor Integration:** Detects when someone walks in or out and sends requests to the server automatically.
- **Auto Play/Stop:** Music turns on when you enter the room and turns off when you leave.
- **Raspberry Pi 5 Powered:** Runs fast and smooth on a Pi 5 to manage your songs and sensors.
- **YouTube Downloader:** Easily convert and download music directly from YouTube links.
- **Easy Web & App Control:** Play music via the web browser or local app.


## 📁 File Structure

- **backend.py** — Main Flask server, API routes, and Pygame music player backend
- **start.sh** — Shell script to easily start, stop, or manage the application process
- **frontend/templates/index.html** — Web interface for controlling playlists and settings
- **playlists/** — Directory containing your audio folders and downloaded music files


## 🛠️ Hardware
- Controller: ESP32 DevKit V1
- Sensor: HC-SR04P
- Powerbank

| Component | Image | Recommended Link |
| :--- | :---: | :--- |
| **ESP32 DevKit V1** | <img src="esp32.png" alt="ESP32" width="150"> | [Buy here](https://www.amazon.de/dp/B0DHRV7784) |
| **HC-SR04P sensor** | <img src="HC-SR04P.png" alt="HC-SR04P" width="150"> | [Buy here](https://www.amazon.com/dp/B0GZNRW6XR) |
| **Powerbank** | <img src="powerbank.png" alt="Powerbank" width="150"> | [Buy here](https://www.amazon.de/dp/B0BHZ6RY6C) |



## 🔌 Pin Connections

The ESP32 acts as the core controller, playing and stopping music based on movement detection. Below is the wiring diagram for the sensor.

### 1. Sound Sensor (KY-037/038) to ESP32
| Sound Sensor Pin | ESP32 Pin | Description |
| :--- | :--- | :--- |
| **VCC** | 3.3V / VIN | Power Supply |
| **GND** | GND | Ground |
| **AO** | GPIO 2 | Analog Output |
| **DO** | GPIO 4 | Digital Output |


## 🔍 Code Insights & Logic




