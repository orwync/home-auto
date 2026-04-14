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
    """

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
        GPIO.cleanup(self._pins)
