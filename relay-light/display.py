from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas


class Display:
    """
    SSD1306 128x64 I2C OLED display.

    Wiring:
      VCC → 3.3V (Pin 1)
      GND → GND  (Pin 6)
      SCL → GPIO3 (Pin 5)
      SDA → GPIO2 (Pin 3)

    Enable I2C first: sudo raspi-config → Interface Options → I2C → Enable
    Default I2C address is 0x3C; some boards use 0x3D.
    """

    def __init__(self, i2c_port: int = 1, i2c_address: int = 0x3C):
        serial = i2c(port=i2c_port, address=i2c_address)
        self._device = ssd1306(serial)

    def update(
        self,
        temp: float | None,
        hum: float | None,
        light_on: bool,
        fan_on: bool,
    ) -> None:
        """Redraw the display with current sensor and relay state."""
        temp_str = f"{temp:.1f} C" if temp is not None else "---"
        hum_str  = f"{hum:.1f} %" if hum is not None else "---"
        with canvas(self._device) as draw:
            draw.text((0,  0), f"Temp:  {temp_str}",               fill="white")
            draw.text((0, 16), f"Hum:   {hum_str}",                fill="white")
            draw.text((0, 32), f"Light: {'ON' if light_on else 'OFF'}", fill="white")
            draw.text((0, 48), f"Fan:   {'ON' if fan_on else 'OFF'}",   fill="white")

    def clear(self) -> None:
        self._device.clear()

    def cleanup(self) -> None:
        self.clear()
        self._device.cleanup()
