#!/usr/bin/env python3
"""
Relay light controller — Raspberry Pi 4B
- Light: time-scheduled ON 00:00–12:00 and 18:00–00:00, OFF 12:00–18:00
- Fans:  temperature-triggered, ON above FAN_TEMP_ON, OFF below FAN_TEMP_OFF
- DHT22 temp/humidity logged every TEMP_INTERVAL seconds
- Manual control via FIFO: echo "light on|off|auto" or "fan on|off|auto" > CMD_FIFO
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

CMD_FIFO = '/tmp/relay-light.cmd'


def light_should_be_on() -> bool:
    hour = datetime.now().hour
    return not (OFF_START <= hour < OFF_END)


def _open_fifo() -> int:
    if not os.path.exists(CMD_FIFO):
        os.mkfifo(CMD_FIFO)
    # O_RDWR keeps the pipe open even with no external writer — prevents EOF on read
    return os.open(CMD_FIFO, os.O_RDWR | os.O_NONBLOCK)


def _handle_command(cmd: str, light: Relay, fan: Relay, overrides: dict) -> None:
    parts = cmd.strip().lower().split()
    if len(parts) != 2:
        return
    device, action = parts
    ts = datetime.now().strftime('%H:%M:%S')

    if device == 'light':
        if action == 'on':
            light.on()
            overrides['light'] = True
            print(f"[{ts}] [CMD] Light ON (manual override)")
        elif action == 'off':
            light.off()
            overrides['light'] = False
            print(f"[{ts}] [CMD] Light OFF (manual override)")
        elif action == 'auto':
            overrides['light'] = None
            print(f"[{ts}] [CMD] Light → auto (schedule)")
    elif device == 'fan':
        if action == 'on':
            fan.on()
            overrides['fan'] = True
            print(f"[{ts}] [CMD] Fan ON (manual override)")
        elif action == 'off':
            fan.off()
            overrides['fan'] = False
            print(f"[{ts}] [CMD] Fan OFF (manual override)")
        elif action == 'auto':
            overrides['fan'] = None
            print(f"[{ts}] [CMD] Fan → auto (temp-triggered)")


def main():
    light    = Relay(pin=RELAY_GPIO_PIN, active_low=True, contact='NO')
    fan      = Relay(pin=FAN_GPIO_PIN,   active_low=True, contact='NO')
    sensor   = TempSensor(gpio_pin=TEMP_GPIO_PIN)
    fifo_fd  = _open_fifo()
    overrides = {'light': None, 'fan': None}  # None = auto; True/False = manual

    def shutdown(sig, frame):
        print("\nShutting down...")
        light.on()    # restore light to ON (safe default)
        fan.off()
        light.cleanup()
        fan.cleanup()
        sensor.cleanup()
        os.close(fifo_fd)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"Light relay  GPIO{RELAY_GPIO_PIN} | Fan relay GPIO{FAN_GPIO_PIN} | Sensor GPIO{TEMP_GPIO_PIN}")
    print(f"Light schedule: ON 00:00–{OFF_START:02d}:00 and {OFF_END:02d}:00–00:00 | OFF {OFF_START:02d}:00–{OFF_END:02d}:00")
    print(f"Fan thresholds: ON >{FAN_TEMP_ON}°C  OFF <{FAN_TEMP_OFF}°C")
    print(f"Commands: echo 'light on|off|auto' > {CMD_FIFO}")
    print(f"          echo 'fan   on|off|auto' > {CMD_FIFO}\n")

    last_light_state = None
    fan_on           = False
    last_temp_log    = 0.0

    while True:
        now = datetime.now()

        # ── Light ──────────────────────────────────────────────────────────────
        if overrides['light'] is None:
            desired = light_should_be_on()
            if desired != last_light_state:
                if desired:
                    light.on()
                    print(f"[{now.strftime('%H:%M:%S')}] Light ON")
                else:
                    light.off()
                    print(f"[{now.strftime('%H:%M:%S')}] Light OFF")
                last_light_state = desired
        else:
            last_light_state = overrides['light']

        # ── Temperature & fans ─────────────────────────────────────────────────
        if time.monotonic() - last_temp_log >= TEMP_INTERVAL:
            temp, hum = sensor.read()
            ts = datetime.now().strftime('%H:%M:%S')
            if temp is not None:
                print(f"[{ts}] Temp {temp:.1f}°C  Humidity {hum:.1f}%")
                if overrides['fan'] is None:
                    if not fan_on and temp >= FAN_TEMP_ON:
                        fan.on()
                        fan_on = True
                        print(f"[{ts}] Fan ON  ({temp:.1f}°C >= {FAN_TEMP_ON}°C)")
                    elif fan_on and temp <= FAN_TEMP_OFF:
                        fan.off()
                        fan_on = False
                        print(f"[{ts}] Fan OFF ({temp:.1f}°C <= {FAN_TEMP_OFF}°C)")
            else:
                print(f"[{ts}] Temp read failed (will retry)")
            last_temp_log = time.monotonic()

        # ── Wait for next cycle, wake immediately on incoming command ───────────
        ready, _, _ = select.select([fifo_fd], [], [], CHECK_INTERVAL)
        if ready:
            data = os.read(fifo_fd, 256).decode(errors='replace').strip()
            for line in data.splitlines():
                if line:
                    _handle_command(line, light, fan, overrides)


if __name__ == "__main__":
    main()
