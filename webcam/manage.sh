#!/bin/bash
# Manage the webcam systemd service

SERVICE=webcam
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_FILE="/etc/systemd/system/$SERVICE.service"

usage() {
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  install    Install and enable as a systemd service"
    echo "  uninstall  Disable and remove the service"
    echo "  start      Start the service"
    echo "  stop       Stop the service"
    echo "  restart    Restart the service"
    echo "  status     Show service status"
    echo "  update     Pull latest code and restart"
    echo "  logs       Tail live service logs"
    exit 1
}

require_sudo() {
    if [ "$EUID" -ne 0 ]; then
        echo "This command requires sudo. Run: sudo $0 $1"
        exit 1
    fi
}

case "$1" in
    install)
        require_sudo install
        # Load .env so values are resolved at install time
        if [ -f "$SCRIPT_DIR/.env" ]; then
            set -a; source "$SCRIPT_DIR/.env"; set +a
        fi
        _DEVICE="${DEVICE:-/dev/video0}"
        _RESOLUTION="${RESOLUTION:-640x480}"
        _FPS="${FPS:-15}"
        _PORT="${PORT:-8080}"
        _USERNAME="${USERNAME:-admin}"
        _PASSWORD="${PASSWORD:-changeme}"

        cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Webcam MJPEG stream
After=network.target

[Service]
ExecStart=/usr/local/bin/mjpg_streamer \
    -i "input_uvc.so -d $_DEVICE -r $_RESOLUTION -f $_FPS" \
    -o "output_http.so -p $_PORT -w /usr/local/share/mjpg-streamer/www -c $_USERNAME:$_PASSWORD"
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
        systemctl daemon-reload
        systemctl enable $SERVICE
        systemctl start $SERVICE
        echo "Service installed, enabled, and started."
        echo "Stream: http://$(hostname -I | awk '{print $1}'):${PORT:-8080}/?action=stream"
        ;;

    uninstall)
        require_sudo uninstall
        systemctl stop $SERVICE 2>/dev/null
        systemctl disable $SERVICE 2>/dev/null
        rm -f "$SERVICE_FILE"
        systemctl daemon-reload
        echo "Service removed."
        ;;

    start)
        sudo systemctl start $SERVICE && echo "Started."
        ;;

    stop)
        sudo systemctl stop $SERVICE && echo "Stopped."
        ;;

    restart)
        sudo systemctl restart $SERVICE && echo "Restarted."
        ;;

    status)
        systemctl status $SERVICE
        ;;

    update)
        echo "Pulling latest code..."
        git -C "$SCRIPT_DIR/.." pull
        sudo systemctl restart $SERVICE
        echo "Updated and restarted."
        ;;

    logs)
        journalctl -u $SERVICE -f
        ;;

    *)
        usage
        ;;
esac
