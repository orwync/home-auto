#!/usr/bin/env python3
"""
Relay light controller — Raspberry Pi 4B
- Light 100W: time-scheduled ON 00:00–12:00 and 18:00–00:00, OFF 12:00–18:00
- Light  40W: same schedule as 100W light
- DHT22 temp/humidity logged every TEMP_INTERVAL seconds
"""

import logging
import signal
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from relay import Relay
from temp_sensor import TempSensor

LIGHT100_GPIO_PIN = 17   # BCM GPIO17 = physical pin 11  — 100W light relay
LIGHT40_GPIO_PIN  = 27   # BCM GPIO27 = physical pin 13  — 40W light relay
TEMP_GPIO_PIN     = 4    # BCM GPIO4  = physical pin 7   — DHT22

CHECK_INTERVAL = 30   # seconds between schedule checks
TEMP_INTERVAL  = 60   # seconds between temperature readings

# Light schedule — OFF between these hours (24h), ON the rest of the day
OFF_START = 12  # noon
OFF_END   = 18  # 6pm

LOG_FILE = Path(__file__).parent / "relay-light.log"

log = logging.getLogger(__name__)


def setup_logging():
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)

    root.addHandler(fh)
    root.addHandler(ch)


def light_should_be_on() -> bool:
    hour = datetime.now().hour
    return not (OFF_START <= hour < OFF_END)


def main():
    setup_logging()

    light100 = Relay(pin=LIGHT100_GPIO_PIN, active_low=True, contact='NO')
    light40  = Relay(pin=LIGHT40_GPIO_PIN,  active_low=True, contact='NO')
    sensor   = TempSensor(gpio_pin=TEMP_GPIO_PIN)

    def shutdown(sig, frame):
        log.info("Shutting down")
        light100.on()    # restore lights to ON (safe default)
        light40.on()
        light100.cleanup()
        light40.cleanup()
        sensor.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    log.info(
        "100W relay GPIO%d | 40W relay GPIO%d | Sensor GPIO%d",
        LIGHT100_GPIO_PIN, LIGHT40_GPIO_PIN, TEMP_GPIO_PIN,
    )
    log.info(
        "Light schedule: ON 00:00-%02d:00 and %02d:00-00:00 | OFF %02d:00-%02d:00",
        OFF_START, OFF_END, OFF_START, OFF_END,
    )

    last_light_state = None
    last_temp_log    = 0.0

    while True:
        # ── Lights (schedule) ─────────────────────────────────────────────────
        desired = light_should_be_on()
        if desired != last_light_state:
            if desired:
                light100.on()
                light40.on()
            else:
                light100.off()
                light40.off()
            log.info("Lights %s (schedule)", "ON" if desired else "OFF")
            last_light_state = desired

        # ── Temperature ───────────────────────────────────────────────────────
        if time.monotonic() - last_temp_log >= TEMP_INTERVAL:
            temp, hum = sensor.read()
            if temp is not None:
                log.info("Temp %.1f°C  Humidity %.1f%%", temp, hum)
            else:
                log.warning("Temp read failed (will retry)")
            last_temp_log = time.monotonic()

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
