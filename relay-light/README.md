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

## Wiring

### Control side (Pi → Relay module)

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

### Load side (Relay → Light)

```
Mains Live ──► COM
              NO ──► Light (Live terminal)
Mains Neutral ───► Light (Neutral terminal)
```

> **Warning:** The load side carries mains voltage (120V/240V AC). Ensure all connections
> are properly insulated and the circuit is unpowered before wiring.

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

Edit `main.py` to adjust the schedule:

| Variable         | Default | Description                          |
|------------------|---------|--------------------------------------|
| `RELAY_GPIO_PIN` | `17`    | BCM GPIO pin connected to relay IN   |
| `OFF_START`      | `12`    | Hour (24h) when light turns OFF      |
| `OFF_END`        | `18`    | Hour (24h) when light turns back ON  |
| `CHECK_INTERVAL` | `30`    | Seconds between schedule checks      |

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
├── main.py          # Entry point, schedule loop
├── relay.py         # Relay class (GPIO control)
├── diag.py          # Raw GPIO diagnostic tool
└── requirements.txt
```
