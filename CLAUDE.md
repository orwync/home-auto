# home-auto

Home automation projects running on Raspberry Pi 4B.

## Hardware

- **Board:** Raspberry Pi 4B
- **Light relay:** 1-channel 5V relay module (active LOW), wired to NO contact — GPIO17 (physical pin 11)
- **Fan relay:** 1-channel 5V relay module (active LOW), wired to NO contact — GPIO27 (physical pin 13)
- **Load:** 100W mains light + cooling fans
- **Temp sensor:** DHT22 (AM2302) — temperature & humidity, 1-wire-like single-bus protocol
- **Camera:** Logitech USB webcam (planned)

## Projects

- `relay-light/` — Time-scheduled 100W light + temperature-triggered fans via relays. Light ON 00:00–12:00 and 18:00–00:00, OFF 12:00–18:00. Fans ON above 28°C, OFF below 25°C. Logs temperature/humidity every 60 s.

## Conventions

- GPIO pin numbering uses BCM mode throughout.
- Light relay control pin: GPIO17 (physical pin 11).
- Fan relay control pin: GPIO27 (physical pin 13).
- DHT22 data pin: GPIO4 (physical pin 7). Requires a 10 kΩ pull-up resistor to 3.3V.
- All sensor/relay VCC must be wired to Pin 1 (3.3V), not 5V — Pi GPIO logic is 3.3V.
- All scripts must restore hardware to a safe default state on exit (light ON, relay de-energized).
- Use `RPi.GPIO` for relay GPIO control. Use `pigpio` (daemon-based, hardware-timed) for DHT22 — pure Python bit-banging is too jittery for reliable reads.
- Light is wired to NO (Normally Open) terminal on the relay.
- DHT22 reads are best-effort — transient failures (RuntimeError) are expected and retried silently.

## Running

```bash
pip install -r relay-light/requirements.txt
python3 relay-light/main.py
```

## Safety

The relay load side carries mains voltage. Never modify load-side wiring while powered.
The Pi GPIO side (control) is always 3.3V logic only.
