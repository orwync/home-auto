import RPi.GPIO as GPIO


class Relay:
    """
    Controls a single-channel 5V relay module (VCC = 5V, signal = 3.3V GPIO).

    active_low: True if the module energizes on GPIO LOW.
    contact:    'NC' or 'NO' — whichever terminal the load is wired to.

    off() floats the pin (INPUT mode) rather than driving HIGH, because 3.3V
    HIGH leaves 1.7V across the 5V coil — enough to hold the relay in.
    """

    def __init__(self, pin: int, active_low: bool = True, contact: str = 'NC'):
        self.pin = pin
        self.active_low = active_low
        self.contact = contact  # 'NC' or 'NO'

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT, initial=self._signal(on=True))

    def _signal(self, on: bool) -> int:
        """Return the GPIO level needed to set the light on or off."""
        # NC: light on  → coil de-energized | light off → coil energized
        # NO: light on  → coil energized     | light off → coil de-energized
        energize = (self.contact == 'NO') if on else (self.contact == 'NC')
        if self.active_low:
            return GPIO.LOW if energize else GPIO.HIGH
        else:
            return GPIO.HIGH if energize else GPIO.LOW

    def on(self):
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, self._signal(on=True))

    def off(self):
        # Float the pin (INPUT mode) to de-energize — driving HIGH still leaves
        # 1.7 V across the 5 V coil, which is enough to hold the relay in.
        GPIO.setup(self.pin, GPIO.IN)

    def cleanup(self):
        GPIO.cleanup(self.pin)
