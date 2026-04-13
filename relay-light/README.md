# relay-light

Controls a 100W mains light via a 1-channel 5V relay module on a Raspberry Pi 4B.

## Schedule

| Time | State |
|------|-------|
| 00:00 – 12:00 | ON |
| 12:00 – 18:00 | OFF |
| 18:00 – 00:00 | ON |

If the Pi loses power the light defaults to **ON** (relay de-energized, NO contact open — wait, see wiring below).

## Hardware

- Raspberry Pi 4B
- 1-channel 5V relay module (active LOW)
- 100W light (mains voltage, 120V/240V AC)
- DHT22 (AM2302) temperature & humidity sensor

## Wiring

### Pi 4B GPIO header reference (used pins)

```
                       3V3  [ 1] [ 2]  5V
  DHT22 DATA (GPIO4) ──────  [ 7] [ 6]  GND ── DHT22 GND / Relay GND
  Relay IN   (GPIO17) ─────  [11] [ 1]  3V3 ── DHT22 VCC / Relay VCC
```

Full pinout: https://pinout.xyz

---

### Relay module — control side (Pi → Relay)

| Relay Pin | Pi Physical Pin  | BCM GPIO |
|-----------|------------------|----------|
| VCC       | Pin 1 **(3.3V)** | —        |
| GND       | Pin 6            | —        |
| IN        | Pin 11           | GPIO17   |

> **Important:** Use Pin 1 (3.3V), not Pin 2/4 (5V). The Pi's GPIO outputs 3.3V logic.
> Powering the relay module from 5V causes the optocoupler to stay partially on,
> so the relay never de-energizes.
>
> If your module has a **JD-VCC** pin: remove the jumper, connect JD-VCC to Pin 2 (5V)
> and VCC to Pin 1 (3.3V). This keeps the coil on 5V while the signal circuit runs on 3.3V.

### Relay module — load side (Relay → Light)

```
Mains Live ──► COM
              NO ──► Light (Live terminal)
Mains Neutral ───► Light (Neutral terminal)
```

> **Warning:** The load side carries mains voltage (120V/240V AC). Ensure all connections
> are properly insulated and the circuit is unpowered before wiring.

---

### DHT22 temperature & humidity sensor

```
DHT22 / AM2302 pin order (face-on, pins down):

  ┌─────────────┐
  │  ╔═══════╗  │
  │  ║ DHT22 ║  │
  │  ╚═══════╝  │
  └──┬──┬──┬───┘
     1  2  3  4
     │  │     │
     │  │     └──── Pin 6  GND
     │  │
     │  └─────────── Pin 7  GPIO4 (BCM) ──┐
     │                                     │ 10 kΩ pull-up resistor
     └───────────────────────────────────  Pin 1  3.3V

  Pin 3 (NC) — not connected
```

| DHT22 Pin | Pi Physical Pin  | BCM GPIO | Note                          |
|-----------|------------------|----------|-------------------------------|
| 1 – VCC   | Pin 1 **(3.3V)** | —        | Also connects to pull-up      |
| 2 – DATA  | Pin 7            | GPIO4    | 10 kΩ pull-up to VCC required |
| 3 – NC    | —                | —        | Leave unconnected             |
| 4 – GND   | Pin 6            | —        |                               |

**Pull-up resistor:** Place a 10 kΩ resistor between DATA (pin 2) and VCC (pin 1).
Without it, reads will be unreliable. Many breadboard DHT22 breakout boards include
this resistor on-board — check your module before adding a separate one.

> The DHT22 works at 3.3V. Do not use 5V — the DATA line would exceed Pi GPIO input limits.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python3 main.py
```

Press `Ctrl+C` to stop. The light will be restored to ON before exit.

## Configuration

Edit `main.py` to adjust the schedule and sensor settings:

| Variable         | Default | Description                            |
|------------------|---------|----------------------------------------|
| `RELAY_GPIO_PIN` | `17`    | BCM GPIO pin connected to relay IN     |
| `OFF_START`      | `12`    | Hour (24h) when light turns OFF        |
| `OFF_END`        | `18`    | Hour (24h) when light turns back ON    |
| `CHECK_INTERVAL` | `30`    | Seconds between schedule checks        |
| `TEMP_GPIO_PIN`  | `4`     | BCM GPIO pin connected to DHT22 DATA   |
| `TEMP_INTERVAL`  | `60`    | Seconds between temperature log lines  |

## Run on boot (optional)

To start automatically on boot, add a cron entry:

```bash
crontab -e
```

Add:
```
@reboot python3 /home/pi/Projects/home-auto/relay-light/main.py &
```

## Files

```
relay-light/
├── main.py          # Entry point, schedule + temp logging loop
├── relay.py         # Relay class (GPIO control)
├── temp_sensor.py   # TempSensor class (DHT22 via adafruit-circuitpython-dht)
├── diag.py          # Raw GPIO diagnostic tool
└── requirements.txt
```
