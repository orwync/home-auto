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

# ── Calculations ──────────────────────────────────────────────────────────────
hours_off    = OFF_END - OFF_START          # light off window
hours_on     = 24 - hours_off               # light on window

# Energy per day (Wh)
wh_light_on  = hours_on  * (PI_WATTS + LIGHT_WATTS)
wh_light_off = hours_off * PI_WATTS
wh_daily     = wh_light_on + wh_light_off

kwh_daily    = wh_daily / 1000
kwh_monthly  = kwh_daily * 30
kwh_yearly   = kwh_daily * 365

cost_daily   = kwh_daily   * COST_PER_KWH
cost_monthly = kwh_monthly * COST_PER_KWH
cost_yearly  = kwh_yearly  * COST_PER_KWH

# ── Report ────────────────────────────────────────────────────────────────────
print("=" * 44)
print("  Relay-Light Power & Cost Report")
print("=" * 44)

print(f"\n{'Hardware':}")
print(f"  Raspberry Pi 4B       {PI_WATTS:>6.1f} W")
print(f"  Flood light           {LIGHT_WATTS:>6.1f} W")
print(f"  Combined (light ON)   {PI_WATTS + LIGHT_WATTS:>6.1f} W")

print(f"\nSchedule")
print(f"  Light ON   {hours_on:>2}h/day  (00:00–{OFF_START:02d}:00 and {OFF_END:02d}:00–00:00)")
print(f"  Light OFF  {hours_off:>2}h/day  ({OFF_START:02d}:00–{OFF_END:02d}:00, Pi only)")

print(f"\nEnergy")
print(f"  Daily                 {kwh_daily:>6.3f} kWh")
print(f"  Monthly (~30 days)    {kwh_monthly:>6.2f} kWh")
print(f"  Yearly  (~365 days)   {kwh_yearly:>6.1f} kWh")

print(f"\nCost  (@ {CURRENCY}{COST_PER_KWH:.2f}/kWh)")
print(f"  Daily                 {CURRENCY}{cost_daily:>5.2f}")
print(f"  Monthly               {CURRENCY}{cost_monthly:>5.2f}")
print(f"  Yearly                {CURRENCY}{cost_yearly:>6.2f}")
print("=" * 44)
