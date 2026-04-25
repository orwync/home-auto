#!/bin/bash
# Start the webcam stream

# Load .env if present
if [ -f "$(dirname "$0")/.env" ]; then
    set -a
    source "$(dirname "$0")/.env"
    set +a
fi

DEVICE="${DEVICE:-/dev/video0}"
RESOLUTION="${RESOLUTION:-640x480}"
FPS="${FPS:-15}"
PORT="${PORT:-8080}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-changeme}"

if ! command -v mjpg_streamer &> /dev/null; then
    echo "mjpg_streamer not found. Run install.sh first."
    exit 1
fi

if [ ! -e "$DEVICE" ]; then
    echo "Device $DEVICE not found. Is the webcam plugged in?"
    exit 1
fi

mjpg_streamer \
    -i "input_uvc.so -d $DEVICE -r $RESOLUTION -f $FPS" \
    -o "output_http.so -p $PORT -w /usr/local/share/mjpg-streamer/www -c $USERNAME:$PASSWORD" &

echo "Stream started:"
echo "  http://$(hostname -I | awk '{print $1}'):$PORT/?action=stream"
echo "  http://$(hostname -I | awk '{print $1}'):$PORT  (full web UI)"
