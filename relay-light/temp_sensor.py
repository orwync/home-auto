import adafruit_dht
import board


class TempSensor:
    """DHT22 (AM2302) wrapper. The sensor needs ~2 s between reads."""

    def __init__(self, gpio_pin: int = 4):
        try:
            pin = getattr(board, f"D{gpio_pin}")
        except AttributeError:
            raise ValueError(f"GPIO{gpio_pin} is not a valid board pin.")
        self._dht = adafruit_dht.DHT22(pin)

    def read(self) -> tuple[float | None, float | None]:
        """Return (temperature_celsius, humidity_percent), or (None, None) on transient error."""
        try:
            return self._dht.temperature, self._dht.humidity
        except RuntimeError:
            # DHT sensors occasionally miss a read; caller should retry.
            return None, None

    def cleanup(self):
        self._dht.exit()


if __name__ == "__main__":
    sensor = TempSensor()
    temp, hum = sensor.read()
    if temp is not None:
        print(f"Temp: {temp:.1f}°C  Humidity: {hum:.1f}%")
    else:
        print("Read failed")
    sensor.cleanup()
