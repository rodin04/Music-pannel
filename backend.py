import os
import time
import threading
import re
import random
from flask import Flask, jsonify, request, render_template
import pygame
import shutil
from yt_dlp import YoutubeDL

app = Flask(__name__, template_folder="/home/rodin-serdan/Dokumente/3_MUSIK_HOME_PANNEL/WEB_PANNEL_PHONE/templates")

PLAYLIST_DIR = "/home/rodin-serdan/Dokumente/3_MUSIK_HOME_PANNEL/playlists"

pygame.mixer.init()
volume = 0.5
pygame.mixer.music.set_volume(volume)

current_track = {"playlist": None, "song": None, "index": -1}

sensor_settings = {
    "enabled": True,
    "playlist": "",
    "song": "random"
}

def clean_song_name(filename):
    return re.sub(r'^\d+_+', '', filename)

def get_clean_sorted_songs(playlist_path):
    AUDIO_FORMATS = ('.mp3', '.m4a', '.wav', '.flac', '.wma', '.ogg')
    if not os.path.exists(playlist_path):
        return []
    songs = [f for f in os.listdir(playlist_path) if f.lower().endswith(AUDIO_FORMATS)]
    songs.sort()
    return songs

def auto_next_player_thread():
    global current_track
    while True:
        time.sleep(1.0)
        if current_track["playlist"] and not pygame.mixer.music.get_busy():
            playlist = current_track["playlist"]
            current_index = current_track["index"]
            playlist_path = os.path.join(PLAYLIST_DIR, playlist)

            songs = get_clean_sorted_songs(playlist_path)
            next_index = current_index + 1
            if next_index < len(songs):
                next_song = songs[next_index]
                try:
                    pygame.mixer.music.load(os.path.join(playlist_path, next_song))
                    pygame.mixer.music.play()
                    current_track = {"playlist": playlist, "song": next_song, "index": next_index}
                    print(f"[AUTO-NEXT] Spiele: {next_song}")
                except Exception as e:
                    print(f"[FEHLER AUTO-NEXT] {e}")
                    current_track = {"playlist": None, "song": None, "index": -1}
            else:
                current_track = {"playlist": None, "song": None, "index": -1}

threading.Thread(target=auto_next_player_thread, daemon=True).start()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/check", methods=["GET"])
def connect_check():
    return jsonify({"status": "OK"}), 200

@app.route("/playlists", methods=["GET"])
def get_playlists_and_songs():
    try:
        if not os.path.exists(PLAYLIST_DIR):
            return jsonify({"error": "Pfad nicht gefunden"}), 404
        playlist_daten = {}
        for item in os.listdir(PLAYLIST_DIR):
            path_to_item = os.path.join(PLAYLIST_DIR, item)
            if os.path.isdir(path_to_item):
                playlist_daten[item] = get_clean_sorted_songs(path_to_item)
        return jsonify({"playlists": playlist_daten}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/play", methods=["POST"])
def play_song():
    global current_track
    data = request.json
    playlist = data.get("playlist")
    song = data.get("song")

    playlist_path = os.path.join(PLAYLIST_DIR, playlist)
    song_path = os.path.join(playlist_path, song)
    if not os.path.exists(song_path):
        return jsonify({"error": "Datei nicht gefunden"}), 404

    songs = get_clean_sorted_songs(playlist_path)
    try: song_index = songs.index(song)
    except ValueError: song_index = -1

    try:
        if current_track["playlist"] == playlist and current_track["song"] == song:
            pygame.mixer.music.stop()
            current_track = {"playlist": None, "song": None, "index": -1}
            return jsonify({"status": "stopped", "current_song": None}), 200

        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        current_track = {"playlist": playlist, "song": song, "index": song_index}
        return jsonify({"status": "playing", "current_song": song}), 200
    except Exception as e:
        current_track = {"playlist": None, "song": None, "index": -1}
        return jsonify({"status": "error", "error": str(e)}), 200

@app.route("/status", methods=["GET"])
def get_status():
    global current_track
    if pygame.mixer.music.get_busy() and current_track["song"]:
        return jsonify({"status": "playing", "current_song": current_track["song"], "playlist": current_track["playlist"]}), 200
    return jsonify({"status": "stopped", "current_song": None, "playlist": None}), 200

@app.route("/reorder", methods=["POST"])
def reorder_songs():
    global current_track
    data = request.json
    playlist = data.get("playlist")
    ordered_songs = data.get("songs", [])

    if not playlist or not ordered_songs:
        return jsonify({"error": "Fehlende Daten"}), 400

    playlist_path = os.path.join(PLAYLIST_DIR, playlist)
    if not os.path.exists(playlist_path):
        return jsonify({"error": "Playlist existiert nicht"}), 404

    try:
        pygame.mixer.music.stop()
        current_track = {"playlist": None, "song": None, "index": -1}

        temp_mapping = []
        for file in os.listdir(playlist_path):
            if file.lower().endswith(('.mp3', '.m4a', '.wav', '.flac', '.wma', '.ogg')):
                clean_name = clean_song_name(file)
                old_path = os.path.join(playlist_path, file)
                temp_path = os.path.join(playlist_path, f"tmp_{clean_name}")
                os.rename(old_path, temp_path)
                temp_mapping.append((clean_name, temp_path))

        for index, song_name in enumerate(ordered_songs):
            pure_name = clean_song_name(song_name)
            for clean_name, temp_path in temp_mapping:
                if clean_name == pure_name:
                    new_filename = f"{str(index+1).zfill(2)}_{pure_name}"
                    final_path = os.path.join(playlist_path, new_filename)
                    os.rename(temp_path, final_path)
                    break

        print(f"[SERVER] Neue Sortierung für '{playlist}' erfolgreich gesichert!")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"[REORDER ERROR] {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["POST"])
def download_song():
    data = request.json
    url = data.get("url")
    playlist = data.get("playlist")

    if not url or not playlist:
        return jsonify({"error": "Fehlende Daten"}), 400

    target_path = os.path.join(PLAYLIST_DIR, playlist)
    if not os.path.exists(target_path):
        return jsonify({"error": "Playlist nicht gefunden"}), 404

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(target_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'quiet': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print(f"[SERVER] Download erfolgreich in: {playlist}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"[DOWNLOAD ERROR] {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    data = request.json
    playlist_name = data.get("name", "").strip()
    if not playlist_name:
        return jsonify({"error": "Kein Name"}), 400

    playlist_path = os.path.join(PLAYLIST_DIR, playlist_name)
    if os.path.exists(playlist_path):
        return jsonify({"error": "Playlist existiert bereits"}), 400

    try:
        os.makedirs(playlist_path)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete_song", methods=["POST"])
def delete_song():
    data = request.json
    playlist = data.get("playlist")
    song = data.get("song")

    if not playlist or not song:
        return jsonify({"error": "Fehlende Daten"}), 400

    song_path = os.path.join(PLAYLIST_DIR, playlist, song)
    if not os.path.exists(song_path):
        return jsonify({"error": "Song nicht gefunden"}), 404

    try:
        os.remove(song_path)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete_playlist", methods=["POST"])
def delete_playlist():
    data = request.json
    playlist = data.get("playlist")

    if not playlist:
        return jsonify({"error": "Keine Playlist"}), 400

    playlist_path = os.path.join(PLAYLIST_DIR, playlist)
    if not os.path.exists(playlist_path):
        return jsonify({"error": "Playlist existiert nicht"}), 404

    try:
        shutil.rmtree(playlist_path)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/set_volume", methods=["POST"])
def set_volume():
    global volume
    data = request.json
    volume = float(data.get("volume", 0.5))
    if volume < 0: volume = 0
    if volume > 1: volume = 1

    pygame.mixer.music.set_volume(volume)
    return jsonify({"status": "success", "volume": volume}), 200

@app.route("/get_volume", methods=["GET"])
def get_volume():
    return jsonify({"volume": volume}), 200

@app.route("/get_sensor_settings", methods=["GET"])
def get_sensor_settings():
    return jsonify(sensor_settings), 200

@app.route("/set_sensor_settings", methods=["POST"])
def set_sensor_settings():
    global sensor_settings
    data = request.json
    sensor_settings["enabled"] = bool(data.get("enabled", True))
    sensor_settings["playlist"] = data.get("playlist", "")
    sensor_settings["song"] = data.get("song", "random")
    return jsonify({"status": "success", "settings": sensor_settings}), 200

@app.route("/sensor_trigger", methods=["POST"])
def sensor_trigger():
    global current_track

    if not sensor_settings["enabled"]:
        return jsonify({"status": "ignored", "reason": "Sensor-Erkennung ist deaktiviert"}), 200

    selected_playlist = sensor_settings["playlist"]
    if not selected_playlist:
        return jsonify({"status": "ignored", "reason": "Keine Playlist für Sensor ausgewählt"}), 200

    playlist_path = os.path.join(PLAYLIST_DIR, selected_playlist)
    if not os.path.exists(playlist_path):
        return jsonify({"status": "error", "reason": "Ausgewählte Sensor-Playlist existiert nicht"}), 400

    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        current_track = {"playlist": None, "song": None, "index": -1}
        print("[SENSOR] Musik gestoppt wegen erneuter Erkennung.")
        return jsonify({"status": "stopped", "action": "stopped"}), 200

    songs = get_clean_sorted_songs(playlist_path)
    if not songs:
        return jsonify({"status": "ignored", "reason": "Keine Songs in der Playlist"}), 200

    selected_song = sensor_settings["song"]

    if selected_song == "random":
        chosen_song = random.choice(songs)
    else:
        if selected_song in songs:
            chosen_song = selected_song
        else:
            chosen_song = songs[0]

    song_path = os.path.join(playlist_path, chosen_song)
    try:
        song_index = songs.index(chosen_song)
    except ValueError:
        song_index = -1

    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        current_track = {"playlist": selected_playlist, "song": chosen_song, "index": song_index}
        print(f"[SENSOR] Musik gestartet: {chosen_song} aus Playlist {selected_playlist}")
        return jsonify({"status": "playing", "action": "played", "song": chosen_song}), 200
    except Exception as e:
        current_track = {"playlist": None, "song": None, "index": -1}
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)