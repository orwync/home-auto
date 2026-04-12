import RPi.GPIO as GPIO


class Relay:
    """
    Controls a single-channel 5V relay module.

    Most relay modules are ACTIVE LOW:
      - GPIO LOW  → relay coil energized → NC opens  → light OFF
      - GPIO HIGH → relay coil de-energized → NC closed → light ON (default)

    If your module is active HIGH, set active_low=False.
    """

    def __init__(self, pin: int, active_low: bool = True):
        self.pin = pin
        self.active_low = active_low

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Default state: relay de-energized → light ON
        initial = GPIO.HIGH if active_low else GPIO.LOW
        GPIO.setup(self.pin, GPIO.OUT, initial=initial)

    def on(self):
        """Turn the light ON (de-energize relay coil via NC)."""
        GPIO.output(self.pin, GPIO.HIGH if self.active_low else GPIO.LOW)

    def off(self):
        """Turn the light OFF (energize relay coil, NC opens)."""
        GPIO.output(self.pin, GPIO.LOW if self.active_low else GPIO.HIGH)

    def cleanup(self):
        GPIO.cleanup(self.pin)
