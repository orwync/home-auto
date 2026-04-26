# home-auto

Home automation projects running on Raspberry Pi 4B.

## Hardware

- **Board:** Raspberry Pi 4B
- **100W light relay:** 1-channel 5V relay module, wired to NO contact — GPIO17 (physical pin 11)
- **40W light relay:** 1-channel 5V relay module, wired to NO contact — GPIO27 (physical pin 13)
- **Load:** 100W mains light + 40W mains light
- **Temp sensor:** DHT22 (AM2302) — temperature & humidity, 1-wire-like single-bus protocol
- **Camera:** Logitech USB webcam — USB, streams via mjpg-streamer on port 8080

## Projects

- `relay-light/` — Time-scheduled 100W + 40W lights via relays. Both ON 00:00–12:00 and 18:00–00:00, OFF 12:00–18:00. Logs temperature/humidity every 60 s to console, log file, and SQLite DB.
- `webcam/` — MJPEG live stream over HTTP via mjpg-streamer. Accessible on local network at port 8080 with basic auth.

## Conventions

- GPIO pin numbering uses BCM mode throughout.
- 100W light relay control pin: GPIO17 (physical pin 11).
- 40W light relay control pin: GPIO27 (physical pin 13).
- DHT22 data pin: GPIO4 (physical pin 7). Requires a 10 kΩ pull-up resistor to 3.3V.
- Relay VCC must be wired to 5V (Pin 2 or 4). At 3.3V the coil does not reliably actuate the contacts.
- Relay GPIO signal is 3.3V logic (active LOW — LOW energizes). However, driving HIGH (3.3V) leaves 1.7V across the 5V coil, which is enough to hold the relay in. The only reliable OFF state is floating the pin (INPUT mode). `relay.py` implements `off()` this way.
- All scripts must restore hardware to a safe default state on exit (relays de-energized, lights OFF).
- Use `RPi.GPIO` for relay GPIO control. Use `pigpio` (daemon-based, hardware-timed) for DHT22 — pure Python bit-banging is too jittery for reliable reads.
- Both lights are wired to NO (Normally Open) terminal on their relay.
- DHT22 reads are best-effort — transient failures (RuntimeError) are expected and retried silently.
- Temperature/humidity readings are stored in `relay-light/sensor_data.db` (SQLite, one row per minute).

## Running

```bash
# relay-light
pip install -r relay-light/requirements.txt
sudo pigpiod
python3 relay-light/main.py

# webcam
sudo bash webcam/manage.sh install   # first time
bash webcam/manage.sh start
```

## Safety

The relay load side carries mains voltage. Never modify load-side wiring while powered.
The Pi GPIO side (control) is always 3.3V logic only.
