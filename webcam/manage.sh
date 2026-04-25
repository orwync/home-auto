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
        # Generate service file with correct paths and .env support
        cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Webcam MJPEG stream
After=network.target

[Service]
EnvironmentFile=-$SCRIPT_DIR/.env
ExecStart=/usr/local/bin/mjpg_streamer \\
    -i "input_uvc.so -d \${DEVICE:-/dev/video0} -r \${RESOLUTION:-640x480} -f \${FPS:-15}" \\
    -o "output_http.so -p \${PORT:-8080} -w /usr/local/share/mjpg-streamer/www -c \${USERNAME:-admin}:\${PASSWORD:-changeme}"
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
