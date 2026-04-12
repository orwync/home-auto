#!/usr/bin/env python3
"""
Relay light controller — Raspberry Pi 4B
Toggles a 100W light ON/OFF every 10 seconds. Default state: ON.
"""

import time
import signal
import sys
from relay import Relay

RELAY_GPIO_PIN = 17   # BCM GPIO17 = physical pin 11
TOGGLE_INTERVAL = 10  # seconds


def main():
    relay = Relay(pin=RELAY_GPIO_PIN, active_low=True, contact='NO')

    def shutdown(sig, frame):
        print("\nShutting down — restoring light to ON...")
        relay.on()
        relay.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"Relay controller started on GPIO{RELAY_GPIO_PIN}")
    print(f"Toggling every {TOGGLE_INTERVAL}s. Default state: ON. Ctrl+C to stop.\n")

    relay.on()
    state = True  # True = ON

    while True:
        print(f"Light {'ON ' if state else 'OFF'}")
        time.sleep(TOGGLE_INTERVAL)
        state = not state
        if state:
            relay.on()
        else:
            relay.off()


if __name__ == "__main__":
    main()
