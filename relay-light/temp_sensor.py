import time
import adafruit_dht
import board

_RETRIES = 3
_RETRY_DELAY = 2.0  # DHT22 minimum interval between reads


class TempSensor:
    """DHT22 (AM2302) wrapper. The sensor needs ~2 s between reads."""

    def __init__(self, gpio_pin: int = 4):
        try:
            pin = getattr(board, f"D{gpio_pin}")
        except AttributeError:
            raise ValueError(f"GPIO{gpio_pin} is not a valid board pin.")
        # use_pulseio=False: PulseIO backend conflicts with RPi GPIO subsystem
        self._dht = adafruit_dht.DHT22(pin, use_pulseio=False)

    def read(self) -> tuple[float | None, float | None]:
        """Return (temperature_celsius, humidity_percent), or (None, None) on transient error."""
        for attempt in range(_RETRIES):
            try:
                temp, hum = self._dht.temperature, self._dht.humidity
                # (0, 0) means all bits were misread — treat as a failed read
                if temp is not None and hum is not None and not (temp == 0 and hum == 0):
                    return temp, hum
            except RuntimeError:
                pass
            if attempt < _RETRIES - 1:
                time.sleep(_RETRY_DELAY)
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
