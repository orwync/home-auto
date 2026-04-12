# relay-light

Controls a 100W mains light via a 1-channel 5V relay module on a Raspberry Pi 4B.

The light turns ON and OFF every 10 seconds. Default state is **ON** — if the Pi loses power the light stays on (relay de-energized, NC contact closed).

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

### Load side (Relay → Light)

```
Mains Live ──► COM
              NC ──► Light (Live terminal)
Mains Neutral ────► Light (Neutral terminal)
```

Use the **NC (Normally Closed)** terminal so the light is on when the relay is not energized.

> **Warning:** The load side carries mains voltage (120V/240V AC). Ensure all connections are properly insulated and the circuit is unpowered before wiring.

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

Edit `main.py` to adjust:

| Variable          | Default | Description                        |
|-------------------|---------|------------------------------------|
| `RELAY_GPIO_PIN`  | `17`    | BCM GPIO pin connected to relay IN |
| `TOGGLE_INTERVAL` | `10`    | Seconds between ON/OFF toggles     |

If your relay module is active HIGH instead of active LOW, set `active_low=False` in the `Relay(...)` call in `main.py`.

## Files

```
relay-light/
├── main.py          # Entry point, toggle loop
├── relay.py         # Relay class (GPIO control)
└── requirements.txt
```
