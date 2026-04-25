import time
import pigpio

_RETRIES    = 3
_RETRY_DELAY = 2.0  # DHT22 minimum interval between reads


class TempSensor:
    """
    DHT22 (AM2302) via pigpio daemon — hardware-timed for reliable reads.

    Requires pigpiod: sudo pigpiod
    The sensor needs ~2 s between reads.
    """

    def __init__(self, gpio_pin: int = 4):
        self._gpio      = gpio_pin
        self._pi        = pigpio.pi()
        if not self._pi.connected:
            raise RuntimeError(
                "Cannot connect to pigpio daemon. Start it with: sudo pigpiod"
            )
        self._armed     = False
        self._high_tick = 0
        self._bit_count = -1   # -1 = waiting for ack pulse
        self._data      = [0] * 5
        self._cb = self._pi.callback(gpio_pin, pigpio.EITHER_EDGE, self._edge)

    def _edge(self, gpio, level, tick):
        if not self._armed:
            return
        if level == pigpio.HIGH:
            self._high_tick = tick
            return
        # Falling edge — measure how long the pin was HIGH
        if self._high_tick == 0:
            return
        pulse = pigpio.tickDiff(self._high_tick, tick)
        if pulse < 10:          # noise
            return
        if self._bit_count < 0:
            # Waiting for the ~80 µs ack HIGH pulse from the sensor
            if pulse > 60:
                self._bit_count = 0
            return
        if self._bit_count < 40:
            # DHT22: ~26–28 µs = 0 bit, ~70 µs = 1 bit
            bit = 1 if pulse > 50 else 0
            self._data[self._bit_count // 8] = (
                (self._data[self._bit_count // 8] << 1) | bit
            )
            self._bit_count += 1

    def _trigger(self) -> tuple[float | None, float | None]:
        """Send one start pulse and collect 40 bits via the pigpio callback."""
        self._data      = [0] * 5
        self._bit_count = -1
        self._high_tick = 0

        self._pi.set_mode(self._gpio, pigpio.OUTPUT)
        self._pi.write(self._gpio, 0)
        time.sleep(0.018)                       # pull low 18 ms (start signal)
        self._pi.set_mode(self._gpio, pigpio.INPUT)
        self._pi.set_pull_up_down(self._gpio, pigpio.PUD_UP)
        self._armed = True
        time.sleep(0.5)                         # wait for all 40 bits
        self._armed = False

        if self._bit_count != 40:
            return None, None

        checksum = sum(self._data[:4]) & 0xFF
        if checksum != self._data[4]:
            return None, None

        hum  = ((self._data[0] << 8) | self._data[1]) / 10.0
        temp = ((self._data[2] & 0x7F) << 8 | self._data[3]) / 10.0
        if self._data[2] & 0x80:
            temp = -temp
        if temp == 0.0 and hum == 0.0:
            return None, None
        return temp, hum

    def read(self) -> tuple[float | None, float | None]:
        """Return (temperature_celsius, humidity_percent), or (None, None) on failure."""
        for attempt in range(_RETRIES):
            temp, hum = self._trigger()
            if temp is not None:
                return temp, hum
            if attempt < _RETRIES - 1:
                time.sleep(_RETRY_DELAY)
        return None, None

    def cleanup(self):
        self._cb.cancel()
        self._pi.stop()


if __name__ == "__main__":
    import logging
    import sys
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)-8s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log = logging.getLogger(__name__)
    log.info("Reading DHT22 on GPIO4 (up to %d attempts, %.1fs apart)...", _RETRIES, _RETRY_DELAY)
    try:
        sensor = TempSensor()
    except RuntimeError as e:
        log.error("%s", e)
        sys.exit(1)

    for attempt in range(_RETRIES):
        temp, hum = sensor._trigger()
        bits = sensor._bit_count
        chk  = sum(sensor._data[:4]) & 0xFF
        chk_status = "ok" if chk == sensor._data[4] else f"FAIL (got {sensor._data[4]}, expected {chk})"
        log.debug("Attempt %d: bits=%d  data=%s  checksum=%s",
                  attempt + 1, bits, sensor._data, chk_status)
        if temp is not None:
            log.info("Temp: %.1f°C  Humidity: %.1f%%", temp, hum)
            break
        if attempt < _RETRIES - 1:
            time.sleep(_RETRY_DELAY)
    else:
        log.warning("Read failed after all attempts.")

    sensor.cleanup()
