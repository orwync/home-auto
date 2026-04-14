import os
import threading
import time
import RPi.GPIO as GPIO


class Switches:
    """
    Physical toggle switches for light, fan, and service control.

    Light / fan — 3-position toggle (e.g. centre-off toggle switch):
      Common → GND
      Pin A  → GPIO (pull-up): LOW = ON  position
      Pin B  → GPIO (pull-up): LOW = OFF position
      Both HIGH (centre) = AUTO

    Service — 2-position toggle:
      Common → GND
      Pin    → GPIO (pull-up): HIGH = running, LOW = stopped

    Default GPIO assignments (BCM):
      Light:   ON → GPIO22 (pin 15)  OFF → GPIO23 (pin 16)
      Fan:     ON → GPIO24 (pin 18)  OFF → GPIO25 (pin 22)
      Service:       GPIO26 (pin 37)

    A background thread polls pins every 50 ms and writes to a pipe when any
    pin changes. Add self.fileno to the main select() to wake immediately.
    """

    _POLL_INTERVAL = 0.05   # seconds (50 ms)

    def __init__(
        self,
        light_on_pin:  int = 22,
        light_off_pin: int = 23,
        fan_on_pin:    int = 24,
        fan_off_pin:   int = 25,
        service_pin:   int = 26,
    ):
        self._light_on  = light_on_pin
        self._light_off = light_off_pin
        self._fan_on    = fan_on_pin
        self._fan_off   = fan_off_pin
        self._service   = service_pin
        self._pins = [light_on_pin, light_off_pin, fan_on_pin, fan_off_pin, service_pin]

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in self._pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self._pipe_r, self._pipe_w = os.pipe()
        self._prev  = {pin: GPIO.input(pin) for pin in self._pins}
        print(f"[SW] Initial pin states: light_on={GPIO.input(light_on_pin)} light_off={GPIO.input(light_off_pin)}"
              f" fan_on={GPIO.input(fan_on_pin)} fan_off={GPIO.input(fan_off_pin)} service={GPIO.input(service_pin)}"
              f"  (0=LOW/active, 1=HIGH/inactive)")
        self._stop  = threading.Event()
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()

    def _poll(self) -> None:
        """Background thread — wakes the main loop when any pin changes."""
        while not self._stop.is_set():
            for pin in self._pins:
                val = GPIO.input(pin)
                if val != self._prev[pin]:
                    print(f"[SW] GPIO{pin} changed: {'HIGH' if self._prev[pin] else 'LOW'} → {'HIGH' if val else 'LOW'}")
                    self._prev[pin] = val
                    try:
                        os.write(self._pipe_w, b'\x00')
                    except OSError:
                        pass
            time.sleep(self._POLL_INTERVAL)

    @property
    def fileno(self) -> int:
        """Read end of the wakeup pipe — becomes readable when any switch changes."""
        return self._pipe_r

    def light(self) -> str:
        """Return 'on', 'off', or 'auto'."""
        if not GPIO.input(self._light_on):
            return 'on'
        if not GPIO.input(self._light_off):
            return 'off'
        return 'auto'

    def fan(self) -> str:
        """Return 'on', 'off', or 'auto'."""
        if not GPIO.input(self._fan_on):
            return 'on'
        if not GPIO.input(self._fan_off):
            return 'off'
        return 'auto'

    def service_running(self) -> bool:
        """Return True when the service switch is in the RUN position."""
        return bool(GPIO.input(self._service))

    def cleanup(self):
        self._stop.set()
        self._thread.join()
        os.close(self._pipe_r)
        os.close(self._pipe_w)
        GPIO.cleanup(self._pins)
