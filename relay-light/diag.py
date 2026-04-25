#!/usr/bin/env python3
"""
Raw GPIO diagnostic — bypasses Relay class entirely.
Toggles GPIO17 (physical pin 11) HIGH/LOW every 3 seconds.
Watch the relay module LED and the light to find the working combo.
"""

import logging
import time

import RPi.GPIO as GPIO

PIN = 17  # BCM GPIO17 = physical pin 11

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.LOW)

log.info("Driving GPIO%d (physical pin 11)", PIN)
log.info("Watch the relay LED on the module and the light.")

try:
    cycle = 0
    while True:
        cycle += 1
        log.info("[%d] GPIO HIGH", cycle)
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(3)

        log.info("[%d] GPIO LOW", cycle)
        GPIO.output(PIN, GPIO.LOW)
        time.sleep(3)

except KeyboardInterrupt:
    log.info("Done.")
    GPIO.cleanup(PIN)
