#!/usr/bin/env python3
"""
Raw GPIO diagnostic — bypasses Relay class entirely.
Toggles GPIO17 (physical pin 11) HIGH/LOW every 3 seconds.
Watch the relay module LED and the light to find the working combo.
"""

import RPi.GPIO as GPIO
import time

PIN = 17  # BCM GPIO17 = physical pin 11

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.LOW)

print(f"Driving GPIO{PIN} (physical pin 11)")
print("Watch the relay LED on the module and the light.\n")

try:
    cycle = 0
    while True:
        cycle += 1
        print(f"[{cycle}] GPIO HIGH")
        GPIO.output(PIN, GPIO.HIGH)
        time.sleep(3)

        print(f"[{cycle}] GPIO LOW")
        GPIO.output(PIN, GPIO.LOW)
        time.sleep(3)

except KeyboardInterrupt:
    print("\nDone.")
    GPIO.cleanup(PIN)
