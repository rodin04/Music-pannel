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

### backend.py

#### 1. Sensor Trigger Logic (ESP32 Control)
The ESP32 triggers this route to toggle music playback on or off when movement is detected.

<p>
  <img src="logic-1.png" width="450" alt="Sensor Trigger Part 1" style="margin-right: 10px;" />
  <img src="logic-2.png" width="450" alt="Sensor Trigger Part 2" />
</p>

- **Check Status:** Validates if the sensor feature is enabled and a playlist is selected.
- **Toggle State:** Stops the music if it's currently playing, or starts it if it's off.
- **Song Selection:** Picks either a random song or a specific one based on web settings.

---

#### 2. YouTube Downloader Route (`/download`)
Downloads and converts YouTube links directly into the selected playlist folder as high-quality MP3 files using `yt-dlp` and `FFmpeg`.

<p>
  <img src="logic-3.png" width="600" alt="Download Logic" />
</p>

- **URL & Playlist Check:** Ensures both a valid YouTube URL and target playlist are provided.
- **Audio Extraction:** Uses `yt-dlp` options to extract best audio and convert it to 320kbps MP3.
- **Error Handling:** Catches any download or network errors and returns a JSON error response.

---

#### 3. Play Song Route (`/play`)
Controls manual playback, starting a specific track or stopping it if it is already active.

<p>
  <img src="logic-4.png" width="600" alt="Play Song Route" />
</p>

- **File Verification:** Checks if the requested song file actually exists in the playlist folder.
- **Toggle / Stop:** If the exact same song is already playing, it stops the music.
- **Pygame Player:** Loads the audio file path into `pygame.mixer.music` and starts playback.

