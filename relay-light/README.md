# relay-light

Controls a 100W mains light and cooling fans via relays on a Raspberry Pi 4B.
Reads temperature and humidity from a DHT22 sensor every 60 seconds.

## Behaviour

**Light** — time-scheduled:

| Time          | State |
|---------------|-------|
| 00:00 – 12:00 | ON    |
| 12:00 – 18:00 | OFF   |
| 18:00 – 00:00 | ON    |

Power loss defaults to ON (relay de-energized, NO contact open).

**Fans** — temperature-triggered:

| Condition       | Action   |
|-----------------|----------|
| Temp ≥ 28 °C   | Fans ON  |
| Temp ≤ 25 °C   | Fans OFF |

Hysteresis prevents rapid cycling between thresholds.

## Hardware

- Raspberry Pi 4B
- 2× 1-channel 5V relay module (active LOW, NO terminal)
- DHT22 (AM2302) temperature & humidity sensor + 10 kΩ pull-up resistor
- 100W mains light
- Cooling fans

## Wiring

### Full connection map

```
 Raspberry Pi 4B
 ┌──────────────────────────────────────────────────────────────┐
 │                                                              │
 │  Pin  1   3.3V  ──────────────────────────┬─────────────────┼──► Light relay VCC
 │                                           ├─────────────────┼──► Fan relay VCC
 │                                           ├─────────────────┼──► DHT22 pin 1 (VCC)
 │                                           └──[10 kΩ]────────┼──► DHT22 pin 2 (DATA)
 │  Pin  6   GND   ──────────────────────────┬─────────────────┼──► Light relay GND
 │                                           ├─────────────────┼──► Fan relay GND
 │                                           └─────────────────┼──► DHT22 pin 4 (GND)
 │  Pin  7   GPIO4  (BCM)  ─────────────────────────────────────┼──► DHT22 pin 2 (DATA)
 │  Pin 11   GPIO17 (BCM)  ─────────────────────────────────────┼──► Light relay IN
 │  Pin 13   GPIO27 (BCM)  ─────────────────────────────────────┼──► Fan relay IN
 │                                                              │
 └──────────────────────────────────────────────────────────────┘

 Light relay — load side (mains voltage, de-power before touching)

   Mains Live ────► COM
                    NO ──────────────────────────────────► Light (live terminal)
   Mains Neutral ───────────────────────────────────────► Light (neutral terminal)

 Fan relay — load side

   Fan V+ ────► COM
                NO ──────────────────────────────────────► Fan V+ (switched)
   Fan GND  ───────────────────────────────────────────► Fan GND
```

> **Warning:** The light relay load side carries mains voltage (120V/240V AC).
> De-power before wiring.

---

### Light relay

| Relay Pin | Pi Pin       | BCM    |
|-----------|--------------|--------|
| VCC       | Pin 1 (3.3V) | —      |
| GND       | Pin 6        | —      |
| IN        | Pin 11       | GPIO17 |

---

### Fan relay

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

Press `Ctrl+C` to stop. Light restores to ON; fans turn OFF on exit.

## Make targets

| Target             | Description                              |
|--------------------|------------------------------------------|
| `make run`         | Run in foreground                        |
| `make start`       | Run in background (logs to file)         |
| `make stop`        | Stop background process                  |
| `make restart`     | Stop then start                          |
| `make status`      | Show if running                          |
| `make logs`        | Tail the log file                        |
| `make temp`        | One-shot sensor read                     |
| `make diag`        | Raw GPIO diagnostic                      |
| `make power`       | Power & cost report                      |
| `make test`        | Run unit tests                           |
| `make light-on`    | Turn light ON  (manual override)         |
| `make light-off`   | Turn light OFF (manual override)         |
| `make light-auto`  | Return light to time schedule            |
| `make fan-on`      | Turn fans ON   (manual override)         |
| `make fan-off`     | Turn fans OFF  (manual override)         |
| `make fan-auto`    | Return fans to temperature control       |

Manual commands take effect immediately. The service must be running.
Use `light-auto` / `fan-auto` to hand control back to the schedule/sensor.

## Configuration

Edit `main.py`:

| Variable         | Default | Description                           |
|------------------|---------|---------------------------------------|
| `RELAY_GPIO_PIN` | `17`    | BCM GPIO pin — light relay IN         |
| `FAN_GPIO_PIN`   | `27`    | BCM GPIO pin — fan relay IN           |
| `OFF_START`      | `12`    | Hour (24h) when light turns OFF       |
| `OFF_END`        | `18`    | Hour (24h) when light turns back ON   |
| `CHECK_INTERVAL` | `30`    | Seconds between schedule checks       |
| `TEMP_GPIO_PIN`  | `4`     | BCM GPIO pin — DHT22 DATA             |
| `TEMP_INTERVAL`  | `60`    | Seconds between temperature log lines |
| `FAN_TEMP_ON`    | `28.0`  | °C threshold to turn fans ON          |
| `FAN_TEMP_OFF`   | `25.0`  | °C threshold to turn fans OFF         |

## Run on boot (systemd)

```bash
make service-install
make service-start
```

Or via cron:

```bash
crontab -e
# add:
@reboot cd /home/orwync/Projects/home-auto/relay-light && python3 main.py &
```

## Files

```
relay-light/
├── main.py          # Schedule + fan + temp logging loop
├── relay.py         # Relay GPIO control
├── temp_sensor.py   # DHT22 sensor wrapper
├── power.py         # Power & cost calculator
├── diag.py          # Raw GPIO diagnostic
└── requirements.txt
```
