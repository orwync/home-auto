#!/usr/bin/env python3
"""
Power consumption and cost calculator for the relay-light system.
Edit the constants below to match your setup and electricity rate.
"""

# ── Hardware ──────────────────────────────────────────────────────────────────
PI_WATTS    = 6.0    # Raspberry Pi 4B typical draw (W)
LIGHT_WATTS = 100.0  # Flood light (W)

# ── Schedule (must match main.py) ─────────────────────────────────────────────
OFF_START = 12  # hour light turns OFF
OFF_END   = 18  # hour light turns back ON

# ── Electricity rate ──────────────────────────────────────────────────────────
COST_PER_KWH = 0.24  # £/kWh — change to your local rate
CURRENCY     = "£"


def calculate(pi_watts, light_watts, off_start, off_end, cost_per_kwh):
    """Return a dict of energy and cost figures for the given parameters."""
    hours_off = off_end - off_start
    hours_on  = 24 - hours_off

    wh_daily = (hours_on * (pi_watts + light_watts)) + (hours_off * pi_watts)

    kwh_daily   = wh_daily / 1000
    kwh_monthly = kwh_daily * 30
    kwh_yearly  = kwh_daily * 365

    return {
        "hours_on":    hours_on,
        "hours_off":   hours_off,
        "kwh_daily":   kwh_daily,
        "kwh_monthly": kwh_monthly,
        "kwh_yearly":  kwh_yearly,
        "cost_daily":   kwh_daily   * cost_per_kwh,
        "cost_monthly": kwh_monthly * cost_per_kwh,
        "cost_yearly":  kwh_yearly  * cost_per_kwh,
    }


def report():
    r = calculate(PI_WATTS, LIGHT_WATTS, OFF_START, OFF_END, COST_PER_KWH)

    print("=" * 44)
    print("  Relay-Light Power & Cost Report")
    print("=" * 44)

    print(f"\nHardware")
    print(f"  Raspberry Pi 4B       {PI_WATTS:>6.1f} W")
    print(f"  Flood light           {LIGHT_WATTS:>6.1f} W")
    print(f"  Combined (light ON)   {PI_WATTS + LIGHT_WATTS:>6.1f} W")

    print(f"\nSchedule")
    print(f"  Light ON   {r['hours_on']:>2}h/day  (00:00–{OFF_START:02d}:00 and {OFF_END:02d}:00–00:00)")
    print(f"  Light OFF  {r['hours_off']:>2}h/day  ({OFF_START:02d}:00–{OFF_END:02d}:00, Pi only)")

    print(f"\nEnergy")
    print(f"  Daily                 {r['kwh_daily']:>6.3f} kWh")
    print(f"  Monthly (~30 days)    {r['kwh_monthly']:>6.2f} kWh")
    print(f"  Yearly  (~365 days)   {r['kwh_yearly']:>6.1f} kWh")

    print(f"\nCost  (@ {CURRENCY}{COST_PER_KWH:.2f}/kWh)")
    print(f"  Daily                 {CURRENCY}{r['cost_daily']:>5.2f}")
    print(f"  Monthly               {CURRENCY}{r['cost_monthly']:>5.2f}")
    print(f"  Yearly                {CURRENCY}{r['cost_yearly']:>6.2f}")
    print("=" * 44)


if __name__ == "__main__":
    report()
