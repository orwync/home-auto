# relay-light

Controls a 100W and a 40W mains light via relays on a Raspberry Pi 4B.
Reads temperature and humidity from a DHT22 sensor every 60 seconds and stores readings in a SQLite database.

## Behaviour

Both lights follow the same time schedule:

| Time          | State |
|---------------|-------|
| 00:00 – 12:00 | ON    |
| 12:00 – 18:00 | OFF   |
| 18:00 – 00:00 | ON    |

On shutdown both lights restore to ON (relays de-energized, NO contact open).

## Hardware

- Raspberry Pi 4B
- 2× 1-channel 5V relay module (active LOW, NO terminal)
- DHT22 (AM2302) temperature & humidity sensor + 10 kΩ pull-up resistor
- 100W mains light
- 40W mains light

## Wiring

### Full connection map

```
 Raspberry Pi 4B
 ┌──────────────────────────────────────────────────────────────┐
 │                                                              │
 │  Pin  1   3.3V  ──────────────────────────┬─────────────────┼──► 100W relay VCC
 │                                           ├─────────────────┼──► 40W relay VCC
 │                                           ├─────────────────┼──► DHT22 pin 1 (VCC)
 │                                           └──[10 kΩ]────────┼──► DHT22 pin 2 (DATA)
 │  Pin  6   GND   ──────────────────────────┬─────────────────┼──► 100W relay GND
 │                                           ├─────────────────┼──► 40W relay GND
 │                                           └─────────────────┼──► DHT22 pin 4 (GND)
 │  Pin  7   GPIO4  (BCM)  ─────────────────────────────────────┼──► DHT22 pin 2 (DATA)
 │  Pin 11   GPIO17 (BCM)  ─────────────────────────────────────┼──► 100W relay IN
 │  Pin 13   GPIO27 (BCM)  ─────────────────────────────────────┼──► 40W relay IN
 │                                                              │
 └──────────────────────────────────────────────────────────────┘

 100W relay — load side (mains voltage, de-power before touching)

   Mains Live ────► COM
                    NO ──────────────────────────────────► 100W Light (live terminal)
   Mains Neutral ───────────────────────────────────────► 100W Light (neutral terminal)

 40W relay — load side (mains voltage, de-power before touching)

   Mains Live ────► COM
                    NO ──────────────────────────────────► 40W Light (live terminal)
   Mains Neutral ───────────────────────────────────────► 40W Light (neutral terminal)
```

> **Warning:** Both relay load sides carry mains voltage (120V/240V AC). De-power before wiring.

---

### 100W light relay

| Relay Pin | Pi Pin       | BCM    |
|-----------|--------------|--------|
| VCC       | Pin 1 (3.3V) | —      |
| GND       | Pin 6        | —      |
| IN        | Pin 11       | GPIO17 |

---

### 40W light relay

| Relay Pin | Pi Pin       | BCM    |
|-----------|--------------|--------|
| VCC       | Pin 1 (3.3V) | —      |
| GND       | Pin 6        | —      |
| IN        | Pin 13       | GPIO27 |

> Use Pin 1 (3.3V) for relay VCC on both modules, not Pin 2/4 (5V). At 5V the
> optocoupler stays partially on and the relay never fully de-energizes.
>
> **JD-VCC modules:** remove the jumper, wire JD-VCC to Pin 2 (5V) and VCC to
> Pin 1 (3.3V). This runs the coil on 5V while keeping signal logic at 3.3V.

---

### DHT22 sensor

```
 DHT22 / AM2302 (face-on, pins down)

  ┌─────────────┐
  │    DHT22    │
  └──┬──┬──┬──┬┘
     1  2  3  4
     │  │     │
     │  │     └──── Pi Pin 6   GND
     │  │
     │  └─────────── Pi Pin 7   GPIO4 ──┐
     │                                  │ 10 kΩ pull-up
     └────────────── Pi Pin 1   3.3V ───┘

  Pin 3 (NC) — leave unconnected
```

| DHT22 Pin | Pi Pin       | BCM   | Note                          |
|-----------|--------------|-------|-------------------------------|
| 1 VCC     | Pin 1 (3.3V) | —     | Also ties to pull-up resistor |
| 2 DATA    | Pin 7        | GPIO4 | 10 kΩ pull-up to VCC required |
| 3 NC      | —            | —     | Not connected                 |
| 4 GND     | Pin 6        | —     |                               |

> Many DHT22 breakout boards include the pull-up on-board — check before adding a separate resistor.
> Do not use 5V; the DATA line would exceed Pi GPIO input limits.

---

## Setup

```bash
pip install -r requirements.txt

# Start the pigpio daemon (required for DHT22 hardware-timed reads)
sudo pigpiod

# To start pigpiod automatically on boot:
sudo systemctl enable pigpiod
```

## Run

```bash
python3 main.py
```

Press `Ctrl+C` to stop. Both lights restore to ON on exit.

## Make targets

| Target              | Description                          |
|---------------------|--------------------------------------|
| `make run`          | Run in foreground                    |
| `make start`        | Run in background (logs to file)     |
| `make stop`         | Stop background process              |
| `make restart`      | Stop then start                      |
| `make status`       | Show if running                      |
| `make logs`         | Tail the log file                    |
| `make temp`         | One-shot sensor read                 |
| `make diag`         | Raw GPIO diagnostic                  |
| `make power`        | Power & cost report                  |
| `make plot`         | Plot temp/humidity from DB           |
| `make test`         | Run unit tests                       |
| `make light-on`     | Turn both lights ON (manual)         |
| `make light-off`    | Turn both lights OFF (manual)        |
| `make light-auto`   | Return lights to time schedule       |
| `make service-install`   | Install and enable systemd service  |
| `make service-uninstall` | Remove systemd service              |
| `make service-start`     | Start service                       |
| `make service-stop`      | Stop service                        |
| `make service-restart`   | Restart service                     |
| `make service-status`    | Show service status                 |
| `make service-logs`      | Tail service logs                   |

## Configuration

Edit `main.py`:

| Variable            | Default | Description                           |
|---------------------|---------|---------------------------------------|
| `LIGHT100_GPIO_PIN` | `17`    | BCM GPIO pin — 100W relay IN          |
| `LIGHT40_GPIO_PIN`  | `27`    | BCM GPIO pin — 40W relay IN           |
| `TEMP_GPIO_PIN`     | `4`     | BCM GPIO pin — DHT22 DATA             |
| `OFF_START`         | `12`    | Hour (24h) when lights turn OFF       |
| `OFF_END`           | `18`    | Hour (24h) when lights turn back ON   |
| `CHECK_INTERVAL`    | `30`    | Seconds between schedule checks       |
| `TEMP_INTERVAL`     | `60`    | Seconds between temperature readings  |

## Sensor data

Temperature and humidity are stored in `sensor_data.db` (SQLite, one row per minute).

Plot the data:

```bash
python3 plot.py              # all data
python3 plot.py --hours 24   # last 24 hours
python3 plot.py --from "2026-04-01" --to "2026-04-25"
```

## Run on boot (systemd)

```bash
make service-install
```

## Files

```
relay-light/
├── main.py          # Schedule + temp logging loop
├── relay.py         # Relay GPIO control
├── temp_sensor.py   # DHT22 sensor wrapper
├── plot.py          # Plot temp/humidity from sensor_data.db
├── power.py         # Power & cost calculator
├── diag.py          # Raw GPIO diagnostic
├── sensor_data.db   # SQLite database (created at runtime)
├── relay-light.log  # Rotating log file (created at runtime)
└── requirements.txt
```
