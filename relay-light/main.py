#!/usr/bin/env python3
"""
Relay light controller — Raspberry Pi 4B
Schedule: ON from 00:00–12:00 and 18:00–00:00. OFF from 12:00–18:00.
Logs temperature and humidity from a DHT22 sensor every TEMP_INTERVAL seconds.
"""

import time
import signal
import sys
from datetime import datetime
from relay import Relay
from temp_sensor import TempSensor

RELAY_GPIO_PIN = 17   # BCM GPIO17 = physical pin 11
TEMP_GPIO_PIN  = 4    # BCM GPIO4  = physical pin 7
CHECK_INTERVAL = 30   # seconds between schedule checks
TEMP_INTERVAL  = 60   # seconds between temperature readings

# Light is OFF between these hours (24h), ON the rest of the day
OFF_START = 12  # noon
OFF_END   = 18  # 6pm


def light_should_be_on() -> bool:
    hour = datetime.now().hour
    return not (OFF_START <= hour < OFF_END)


def main():
    relay  = Relay(pin=RELAY_GPIO_PIN, active_low=True, contact='NO')
    sensor = TempSensor(gpio_pin=TEMP_GPIO_PIN)

    def shutdown(sig, frame):
        print("\nShutting down — restoring light to ON...")
        relay.on()
        relay.cleanup()
        sensor.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"Relay controller started on GPIO{RELAY_GPIO_PIN}")
    print(f"Schedule: ON 00:00–{OFF_START:02d}:00 and {OFF_END:02d}:00–00:00 | OFF {OFF_START:02d}:00–{OFF_END:02d}:00")
    print(f"Checking every {CHECK_INTERVAL}s. Temp logged every {TEMP_INTERVAL}s. Ctrl+C to stop.\n")

    last_state    = None
    last_temp_log = 0.0

    while True:
        now     = datetime.now()
        desired = light_should_be_on()

        if desired != last_state:
            if desired:
                relay.on()
                print(f"[{now.strftime('%H:%M:%S')}] Light ON")
            else:
                relay.off()
                print(f"[{now.strftime('%H:%M:%S')}] Light OFF")
            last_state = desired

        if time.monotonic() - last_temp_log >= TEMP_INTERVAL:
            temp, hum = sensor.read()
            ts = datetime.now().strftime('%H:%M:%S')
            if temp is not None:
                print(f"[{ts}] Temp {temp:.1f}°C  Humidity {hum:.1f}%")
            else:
                print(f"[{ts}] Temp read failed (will retry)")
            last_temp_log = time.monotonic()

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
