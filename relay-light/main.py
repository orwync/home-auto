#!/usr/bin/env python3
"""
Relay light controller — Raspberry Pi 4B
- Light: time-scheduled ON 00:00–12:00 and 18:00–00:00, OFF 12:00–18:00
- Fans:  temperature-triggered, ON above FAN_TEMP_ON, OFF below FAN_TEMP_OFF
- DHT22 temp/humidity logged every TEMP_INTERVAL seconds
"""

import os
import select
import signal
import sys
import time
from datetime import datetime
from relay import Relay
from temp_sensor import TempSensor

RELAY_GPIO_PIN = 17   # BCM GPIO17 = physical pin 11  — light relay
FAN_GPIO_PIN   = 27   # BCM GPIO27 = physical pin 13  — fan relay
TEMP_GPIO_PIN  = 4    # BCM GPIO4  = physical pin 7   — DHT22

CHECK_INTERVAL = 30   # seconds between schedule checks
TEMP_INTERVAL  = 60   # seconds between temperature readings

# Light schedule — OFF between these hours (24h), ON the rest of the day
OFF_START = 12  # noon
OFF_END   = 18  # 6pm

# Fan thresholds with hysteresis to prevent rapid cycling
FAN_TEMP_ON  = 28.0  # °C — turn fans ON  above this
FAN_TEMP_OFF = 25.0  # °C — turn fans OFF below this


def light_should_be_on() -> bool:
    hour = datetime.now().hour
    return not (OFF_START <= hour < OFF_END)


def main():
    light  = Relay(pin=RELAY_GPIO_PIN, active_low=True, contact='NO')
    fan    = Relay(pin=FAN_GPIO_PIN,   active_low=True, contact='NO')
    sensor = TempSensor(gpio_pin=TEMP_GPIO_PIN)

    def shutdown(sig, frame):
        print("\nShutting down...")
        light.on()    # restore light to ON (safe default)
        fan.off()
        light.cleanup()
        fan.cleanup()
        sensor.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"Light relay  GPIO{RELAY_GPIO_PIN} | Fan relay GPIO{FAN_GPIO_PIN} | Sensor GPIO{TEMP_GPIO_PIN}")
    print(f"Light schedule: ON 00:00–{OFF_START:02d}:00 and {OFF_END:02d}:00–00:00 | OFF {OFF_START:02d}:00–{OFF_END:02d}:00")
    print(f"Fan thresholds: ON >{FAN_TEMP_ON}°C  OFF <{FAN_TEMP_OFF}°C\n")

    last_light_state = None
    fan_on           = False
    last_temp_log    = 0.0
    last_temp        = None

    while True:
        now = datetime.now()
        ts  = now.strftime('%H:%M:%S')

        # ── Light (schedule) ──────────────────────────────────────────────────
        desired = light_should_be_on()
        if desired != last_light_state:
            light.on() if desired else light.off()
            print(f"[{ts}] Light {'ON' if desired else 'OFF'} (schedule)")
            last_light_state = desired

        # ── Temperature ───────────────────────────────────────────────────────
        if time.monotonic() - last_temp_log >= TEMP_INTERVAL:
            temp, hum = sensor.read()
            ts = datetime.now().strftime('%H:%M:%S')
            if temp is not None:
                last_temp = temp
                print(f"[{ts}] Temp {temp:.1f}°C  Humidity {hum:.1f}%")
            else:
                print(f"[{ts}] Temp read failed (will retry)")
            last_temp_log = time.monotonic()

        # ── Fan (temperature-triggered) ───────────────────────────────────────
        if last_temp is not None:
            if not fan_on and last_temp >= FAN_TEMP_ON:
                fan.on()
                fan_on = True
                print(f"[{ts}] Fan ON  ({last_temp:.1f}°C >= {FAN_TEMP_ON}°C)")
            elif fan_on and last_temp <= FAN_TEMP_OFF:
                fan.off()
                fan_on = False
                print(f"[{ts}] Fan OFF ({last_temp:.1f}°C <= {FAN_TEMP_OFF}°C)")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
