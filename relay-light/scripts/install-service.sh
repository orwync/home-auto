#!/bin/bash
# Installs relay-light as a systemd service.
# Run from the relay-light/ directory: bash scripts/install-service.sh

set -e

SERVICE=relay-light
SERVICE_FILE="$SERVICE.service"
SYSTEMD_DIR="/etc/systemd/system"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Replace placeholder paths in the service file with the actual project path
sed "s|/home/pi/Projects/home-auto/relay-light|$SCRIPT_DIR|g" \
    "$SCRIPT_DIR/$SERVICE_FILE" \
    | sudo tee "$SYSTEMD_DIR/$SERVICE_FILE" > /dev/null

# Replace placeholder user with the current user
sudo sed -i "s|User=pi|User=$USER|g" "$SYSTEMD_DIR/$SERVICE_FILE"

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE"
sudo systemctl start "$SERVICE"

echo "Service installed and started."
echo "Run 'systemctl status $SERVICE' to check."
