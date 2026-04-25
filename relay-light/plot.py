#!/usr/bin/env python3
"""
Plot temperature and humidity from sensor_data.db.

Usage:
  python3 relay-light/plot.py              # all data
  python3 relay-light/plot.py --hours 24   # last 24 hours
  python3 relay-light/plot.py --from "2026-04-01" --to "2026-04-25"
"""

import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DB_FILE = Path(__file__).parent / "sensor_data.db"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--hours", type=float, help="Show last N hours of data")
    p.add_argument("--from", dest="from_dt", help="Start datetime (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)")
    p.add_argument("--to",   dest="to_dt",   help="End datetime   (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)")
    return p.parse_args()


def fetch(args) -> tuple[list, list, list]:
    if not DB_FILE.exists():
        raise SystemExit(f"Database not found: {DB_FILE}")

    conn = sqlite3.connect(DB_FILE)

    query = "SELECT timestamp, temp, humidity FROM readings"
    params = []

    if args.hours:
        since = (datetime.now() - timedelta(hours=args.hours)).strftime("%Y-%m-%d %H:%M:%S")
        query += " WHERE timestamp >= ?"
        params.append(since)
    elif args.from_dt or args.to_dt:
        clauses = []
        if args.from_dt:
            clauses.append("timestamp >= ?")
            params.append(args.from_dt)
        if args.to_dt:
            clauses.append("timestamp <= ?")
            params.append(args.to_dt)
        query += " WHERE " + " AND ".join(clauses)

    query += " ORDER BY timestamp"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    if not rows:
        raise SystemExit("No data found for the given range.")

    timestamps = [datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S") for r in rows]
    temps      = [r[1] for r in rows]
    humidities = [r[2] for r in rows]
    return timestamps, temps, humidities


def plot(timestamps, temps, humidities):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    fig.suptitle("Sensor History", fontsize=13)

    ax1.plot(timestamps, temps, color="tomato", linewidth=1)
    ax1.set_ylabel("Temperature (°C)")
    ax1.grid(True, alpha=0.3)

    ax2.plot(timestamps, humidities, color="steelblue", linewidth=1)
    ax2.set_ylabel("Humidity (%)")
    ax2.grid(True, alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %H:%M"))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    args = parse_args()
    timestamps, temps, humidities = fetch(args)
    print(f"Plotting {len(timestamps)} readings "
          f"({timestamps[0]:%Y-%m-%d %H:%M} → {timestamps[-1]:%Y-%m-%d %H:%M})")
    plot(timestamps, temps, humidities)
