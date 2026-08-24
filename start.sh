#!/bin/bash
BACKEND_DIR="/home/rodin-serdan/Dokumente/3_MUSIK_HOME_PANNEL/bakend"
BACKEND_SCRIPT="bakend.py"
LOG_FILE="/home/rodin-serdan/Dokumente/3_MUSIK_HOME_PANNEL/backend.log"
PORT=5000

PID=$(lsof -t -i:$PORT)

if [ -n "$PID" ]; then
    echo "Backend läuft bereits auf Port $PORT (PID: $PID)."
    read -p "Möchtest du das Backend neustarten? (y/n): " choice
    case "$choice" in
        y|Y )
            echo "Beende alten Prozess ($PID) für Neustart..."
            kill -9 $PID
            sleep 1
            ;;
        * )
            read -p "Nicht neugestartet. Möchtest du den Prozess stattdessen nur killen (kill -9)? (y/n): " kill_choice
            case "$kill_choice" in
                y|Y )
                    echo "Erzwinge Beenden von Prozess ($PID)..."
                    kill -9 $PID
                    sleep 1
                    echo "Prozess wurde beendet. Es wird KEIN neues Backend gestartet."
                    exit 0
                    ;;
                * )
                    echo "Abbruch. Nichts wurde geändert."
                    exit 0
                    ;;
            esac
            ;;
    esac
fi

echo "Starte Backend im Hintergrund..."
cd "$BACKEND_DIR" || exit 1

nohup python3 "$BACKEND_SCRIPT" > "$LOG_FILE" 2>&1 &

sleep 2
NEW_PID=$(lsof -t -i:$PORT)

if [ -n "$NEW_PID" ]; then
    echo "Backend erfolgreich gestartet! (Neue PID: $NEW_PID)"
    echo "Erreichbar unter http://100.81.72.103:$PORT"
    echo "Du kannst dieses Terminal jetzt bedenkenlos schließen."
else
    echo "Fehler beim Starten. Schau in die Logdatei: $LOG_FILE"
fi