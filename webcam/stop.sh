#!/bin/bash
# Stop the webcam stream

pkill -f mjpg_streamer && echo "Stream stopped." || echo "Stream was not running."
