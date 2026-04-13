import sys
import unittest
from unittest.mock import MagicMock, patch

# ── Mock RPi.GPIO before importing relay (not available on dev machines) ──────
_gpio = MagicMock()
_gpio.HIGH = 1
_gpio.LOW  = 0
_gpio.BCM  = 11
_gpio.OUT  = 0
sys.modules['RPi']      = MagicMock()
sys.modules['RPi.GPIO'] = _gpio

from relay import Relay  # noqa: E402


class TestRelaySignal(unittest.TestCase):
    """Tests for Relay._signal() — no real GPIO needed."""

    def _make(self, active_low, contact):
        return Relay.__new__(Relay)  # skip __init__ / GPIO setup

    def setUp(self):
        # Patch GPIO calls so __init__ doesn't fail if called
        _gpio.reset_mock()

    # ── NC contact (default wiring) ───────────────────────────────────────────

    def test_nc_active_low_on_deenergizes(self):
        """NC + active LOW: light ON → coil OFF → GPIO HIGH."""
        r = self._make(True, 'NC')
        r.active_low, r.contact = True, 'NC'
        self.assertEqual(r._signal(on=True), _gpio.HIGH)

    def test_nc_active_low_off_energizes(self):
        """NC + active LOW: light OFF → coil ON → GPIO LOW."""
        r = self._make(True, 'NC')
        r.active_low, r.contact = True, 'NC'
        self.assertEqual(r._signal(on=False), _gpio.LOW)

    def test_nc_active_high_on_deenergizes(self):
        """NC + active HIGH: light ON → coil OFF → GPIO LOW."""
        r = self._make(False, 'NC')
        r.active_low, r.contact = False, 'NC'
        self.assertEqual(r._signal(on=True), _gpio.LOW)

    def test_nc_active_high_off_energizes(self):
        """NC + active HIGH: light OFF → coil ON → GPIO HIGH."""
        r = self._make(False, 'NC')
        r.active_low, r.contact = False, 'NC'
        self.assertEqual(r._signal(on=False), _gpio.HIGH)

    # ── NO contact (current wiring) ───────────────────────────────────────────

    def test_no_active_low_on_energizes(self):
        """NO + active LOW: light ON → coil ON → GPIO LOW."""
        r = self._make(True, 'NO')
        r.active_low, r.contact = True, 'NO'
        self.assertEqual(r._signal(on=True), _gpio.LOW)

    def test_no_active_low_off_deenergizes(self):
        """NO + active LOW: light OFF → coil OFF → GPIO HIGH."""
        r = self._make(True, 'NO')
        r.active_low, r.contact = True, 'NO'
        self.assertEqual(r._signal(on=False), _gpio.HIGH)

    def test_no_active_high_on_energizes(self):
        """NO + active HIGH: light ON → coil ON → GPIO HIGH."""
        r = self._make(False, 'NO')
        r.active_low, r.contact = False, 'NO'
        self.assertEqual(r._signal(on=True), _gpio.HIGH)

    def test_no_active_high_off_deenergizes(self):
        """NO + active HIGH: light OFF → coil OFF → GPIO LOW."""
        r = self._make(False, 'NO')
        r.active_low, r.contact = False, 'NO'
        self.assertEqual(r._signal(on=False), _gpio.LOW)

    # ── on() / off() call GPIO.output with correct signal ────────────────────

    def test_on_calls_gpio_output(self):
        r = self._make(True, 'NO')
        r.active_low, r.contact, r.pin = True, 'NO', 17
        r.on()
        _gpio.output.assert_called_with(17, _gpio.LOW)

    def test_off_calls_gpio_output(self):
        r = self._make(True, 'NO')
        r.active_low, r.contact, r.pin = True, 'NO', 17
        r.off()
        _gpio.output.assert_called_with(17, _gpio.HIGH)


if __name__ == '__main__':
    unittest.main()
