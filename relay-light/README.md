# relay-light

Controls a 100W mains light via a 1-channel relay on a Raspberry Pi 4B.
Reads temperature and humidity from a DHT22 sensor every 60 seconds.

## Schedule

| Time          | State |
|---------------|-------|
| 00:00 – 12:00 | ON    |
| 12:00 – 18:00 | OFF   |
| 18:00 – 00:00 | ON    |

Power loss defaults to ON (relay de-energized, NO contact open).

## Hardware

- Raspberry Pi 4B
- 1-channel 5V relay module (active LOW, NO terminal)
- DHT22 (AM2302) temperature & humidity sensor + 10 kΩ pull-up resistor
- 100W mains light

## Wiring

### Full connection map

```
 Raspberry Pi 4B
 ┌──────────────────────────────────────────────────────────┐
 │                                                          │
 │  Pin  1   3.3V  ────────────────────────────┬───────────┼──► Relay VCC
 │                                             ├───────────┼──► DHT22 pin 1 (VCC)
 │                                             └──[10 kΩ]──┼──► DHT22 pin 2 (DATA)
 │  Pin  6   GND   ────────────────────────────┬───────────┼──► Relay GND
 │                                             └───────────┼──► DHT22 pin 4 (GND)
 │  Pin  7   GPIO4  (BCM)  ────────────────────────────────┼──► DHT22 pin 2 (DATA)
 │  Pin 11   GPIO17 (BCM)  ────────────────────────────────┼──► Relay IN
 │                                                          │
 └──────────────────────────────────────────────────────────┘

 Relay load side (mains voltage — de-power before touching)

   Mains Live ────► COM
                    NO ──────────────────────────────────► Light (live terminal)
   Mains Neutral ───────────────────────────────────────► Light (neutral terminal)
```

---

### Relay module

| Relay Pin | Pi Pin       | BCM    |
|-----------|--------------|--------|
| VCC       | Pin 1 (3.3V) | —      |
| GND       | Pin 6        | —      |
| IN        | Pin 11       | GPIO17 |

> Use Pin 1 (3.3V), not Pin 2/4 (5V). At 5V the optocoupler stays partially on
> and the relay never de-energizes.
>
> **JD-VCC modules:** remove the jumper, wire JD-VCC to Pin 2 (5V) and VCC to Pin 1 (3.3V).
> This runs the coil on 5V while keeping the signal side on 3.3V logic.

> **Warning:** The load side carries mains voltage (120V/240V AC). Ensure all connections
> are insulated and the circuit is de-powered before wiring.

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
```

## Run

```bash
python3 main.py
```

Press `Ctrl+C` to stop. The light is restored to ON on exit.

## Make targets

| Target          | Description                        |
|-----------------|------------------------------------|
| `make run`      | Run in foreground                  |
| `make start`    | Run in background (logs to file)   |
| `make stop`     | Stop background process            |
| `make status`   | Show if running                    |
| `make logs`     | Tail the log file                  |
| `make temp`     | One-shot sensor read               |
| `make diag`     | Raw GPIO diagnostic                |
| `make power`    | Power & cost report                |
| `make test`     | Run unit tests                     |

## Configuration

Edit `main.py`:

| Variable         | Default | Description                           |
|------------------|---------|---------------------------------------|
| `RELAY_GPIO_PIN` | `17`    | BCM GPIO pin connected to relay IN    |
| `OFF_START`      | `12`    | Hour (24h) when light turns OFF       |
| `OFF_END`        | `18`    | Hour (24h) when light turns back ON   |
| `CHECK_INTERVAL` | `30`    | Seconds between schedule checks       |
| `TEMP_GPIO_PIN`  | `4`     | BCM GPIO pin connected to DHT22 DATA  |
| `TEMP_INTERVAL`  | `60`    | Seconds between temperature log lines |

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
├── main.py          # Schedule loop + temp logging
├── relay.py         # Relay GPIO control
├── temp_sensor.py   # DHT22 sensor wrapper
├── power.py         # Power & cost calculator
├── diag.py          # Raw GPIO diagnostic
└── requirements.txt
```
