import unittest
from power import calculate


class TestCalculate(unittest.TestCase):

    def _default(self):
        return calculate(
            pi_watts=6.0,
            light_watts=100.0,
            off_start=12,
            off_end=18,
            cost_per_kwh=0.24,
        )

    # ── Hours ─────────────────────────────────────────────────────────────────

    def test_hours_on(self):
        self.assertEqual(self._default()['hours_on'], 18)

    def test_hours_off(self):
        self.assertEqual(self._default()['hours_off'], 6)

    def test_hours_on_off_sum_to_24(self):
        r = self._default()
        self.assertEqual(r['hours_on'] + r['hours_off'], 24)

    # ── Energy ────────────────────────────────────────────────────────────────

    def test_daily_kwh(self):
        # 18h × 106W + 6h × 6W = 1944Wh = 1.944kWh
        self.assertAlmostEqual(self._default()['kwh_daily'], 1.944, places=3)

    def test_monthly_kwh(self):
        self.assertAlmostEqual(self._default()['kwh_monthly'], 1.944 * 30, places=3)

    def test_yearly_kwh(self):
        self.assertAlmostEqual(self._default()['kwh_yearly'], 1.944 * 365, places=3)

    # ── Cost ─────────────────────────────────────────────────────────────────

    def test_daily_cost(self):
        self.assertAlmostEqual(self._default()['cost_daily'], 1.944 * 0.24, places=4)

    def test_monthly_cost(self):
        self.assertAlmostEqual(self._default()['cost_monthly'], 1.944 * 30 * 0.24, places=3)

    def test_yearly_cost(self):
        self.assertAlmostEqual(self._default()['cost_yearly'], 1.944 * 365 * 0.24, places=2)

    # ── Edge cases ────────────────────────────────────────────────────────────

    def test_light_always_on(self):
        """off_start == off_end → 0 off hours, 24 on hours."""
        r = calculate(6.0, 100.0, 12, 12, 0.24)
        self.assertEqual(r['hours_off'], 0)
        self.assertEqual(r['hours_on'], 24)
        self.assertAlmostEqual(r['kwh_daily'], 24 * 106 / 1000, places=3)

    def test_zero_cost_rate(self):
        r = calculate(6.0, 100.0, 12, 18, 0.0)
        self.assertEqual(r['cost_daily'], 0.0)
        self.assertEqual(r['cost_monthly'], 0.0)
        self.assertEqual(r['cost_yearly'], 0.0)

    def test_pi_only_no_light(self):
        """Light wattage 0 — only the Pi draws power."""
        r = calculate(6.0, 0.0, 12, 18, 0.24)
        self.assertAlmostEqual(r['kwh_daily'], 24 * 6.0 / 1000, places=3)


if __name__ == '__main__':
    unittest.main()
