# home-auto

Home automation running on a Raspberry Pi 4B.

## Projects

| Project | Description |
|---------|-------------|
| [`relay-light/`](relay-light/README.md) | Time-scheduled 100W + 40W mains lights via relays. Logs temp/humidity to SQLite. |
| [`webcam/`](#webcam) | MJPEG live stream over HTTP via mjpg-streamer. |

---

## relay-light

Controls two mains lights on a time schedule and logs temperature/humidity from a DHT22 sensor.

**Schedule — both lights:**

| Time          | State |
|---------------|-------|
| 00:00 – 12:00 | ON    |
| 12:00 – 18:00 | OFF   |
| 18:00 – 00:00 | ON    |

**Quick start:**

```bash
pip install -r relay-light/requirements.txt
sudo pigpiod
python3 relay-light/main.py
```

See [`relay-light/README.md`](relay-light/README.md) for full wiring, configuration, and make targets.

---

## webcam

MJPEG live stream accessible from any browser on the local network.

**Quick start:**

```bash
# First time — build mjpg-streamer
bash webcam/install.sh

# Configure credentials
cp webcam/.env.example webcam/.env
nano webcam/.env

# Install as a systemd service (auto-starts on boot)
sudo bash webcam/manage.sh install
```

**Stream URL:** `http://<pi-ip>:8080/?action=stream`

**Management:**

```bash
bash webcam/manage.sh start      # start
bash webcam/manage.sh stop       # stop
bash webcam/manage.sh restart    # restart
bash webcam/manage.sh status     # check status
bash webcam/manage.sh logs       # live logs
bash webcam/manage.sh update     # git pull + restart
bash webcam/manage.sh uninstall  # remove service
```

---

## Hardware

- **Board:** Raspberry Pi 4B
- **100W light relay:** GPIO17 (physical pin 11)
- **40W light relay:** GPIO27 (physical pin 13)
- **Temp sensor:** DHT22 (AM2302) — GPIO4 (physical pin 7)
- **Camera:** Logitech USB webcam

## Safety

The relay load side carries mains voltage. Never modify load-side wiring while powered.
