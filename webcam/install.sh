#!/bin/bash
# Install mjpg-streamer from source on Raspberry Pi OS

set -e

echo "Installing dependencies..."
sudo apt update
sudo apt install -y cmake libjpeg-dev gcc g++ git

echo "Cloning mjpg-streamer..."
git clone https://github.com/jacksonliam/mjpg-streamer.git /tmp/mjpg-streamer

echo "Building..."
cd /tmp/mjpg-streamer/mjpg-streamer-experimental
make
sudo make install

rm -rf /tmp/mjpg-streamer
echo ""
echo "Done. Plug in your webcam and run: ./start.sh"
