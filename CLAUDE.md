# home-auto

Home automation projects running on Raspberry Pi 4B.

## Hardware

- **Board:** Raspberry Pi 4B
- **Relay:** 1-channel 5V relay module (active LOW)
- **Load:** 100W mains light

## Projects

- `relay-light/` — Toggles a 100W light ON/OFF via relay. Default state ON.

## Conventions

- GPIO pin numbering uses BCM mode throughout.
- Relay control pin: GPIO17 (physical pin 11).
- All scripts must restore hardware to a safe default state on exit (light ON, relay de-energized).
- Use `RPi.GPIO` for GPIO control.

## Running

```bash
pip install -r relay-light/requirements.txt
python3 relay-light/main.py
```

## Safety

The relay load side carries mains voltage. Never modify load-side wiring while powered.
The Pi GPIO side (control) is always 3.3V/5V logic only.
