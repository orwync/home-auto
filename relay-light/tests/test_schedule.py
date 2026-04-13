import sys
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Mock RPi.GPIO so main.py can be imported on non-Pi machines
_gpio = MagicMock()
_gpio.HIGH = 1
_gpio.LOW  = 0
_gpio.BCM  = 11
_gpio.OUT  = 0
sys.modules['RPi']      = MagicMock()
sys.modules['RPi.GPIO'] = _gpio

from main import light_should_be_on  # noqa: E402


def _at(hour):
    """Return a datetime with the given hour."""
    return datetime(2024, 1, 1, hour, 0, 0)


class TestSchedule(unittest.TestCase):

    # ── Should be ON ──────────────────────────────────────────────────────────

    def test_midnight_is_on(self):
        with patch('main.datetime') as m:
            m.now.return_value = _at(0)
            self.assertTrue(light_should_be_on())

    def test_early_morning_is_on(self):
        with patch('main.datetime') as m:
            m.now.return_value = _at(6)
            self.assertTrue(light_should_be_on())

    def test_just_before_off_is_on(self):
        with patch('main.datetime') as m:
            m.now.return_value = _at(11)
            self.assertTrue(light_should_be_on())

    def test_evening_start_is_on(self):
        with patch('main.datetime') as m:
            m.now.return_value = _at(18)
            self.assertTrue(light_should_be_on())

    def test_late_evening_is_on(self):
        with patch('main.datetime') as m:
            m.now.return_value = _at(23)
            self.assertTrue(light_should_be_on())

    # ── Should be OFF ─────────────────────────────────────────────────────────

    def test_noon_is_off(self):
        with patch('main.datetime') as m:
            m.now.return_value = _at(12)
            self.assertFalse(light_should_be_on())

    def test_afternoon_is_off(self):
        with patch('main.datetime') as m:
            m.now.return_value = _at(15)
            self.assertFalse(light_should_be_on())

    def test_just_before_evening_is_off(self):
        with patch('main.datetime') as m:
            m.now.return_value = _at(17)
            self.assertFalse(light_should_be_on())

    # ── Boundary: OFF_END is inclusive (18:00 → ON) ───────────────────────────

    def test_off_end_boundary_is_on(self):
        """Hour 18 marks the start of ON, not OFF."""
        with patch('main.datetime') as m:
            m.now.return_value = _at(18)
            self.assertTrue(light_should_be_on())

    def test_off_start_boundary_is_off(self):
        """Hour 12 marks the start of OFF."""
        with patch('main.datetime') as m:
            m.now.return_value = _at(12)
            self.assertFalse(light_should_be_on())


if __name__ == '__main__':
    unittest.main()
