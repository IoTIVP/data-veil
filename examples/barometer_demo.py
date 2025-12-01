"""
DATA VEIL – Barometer Demo

Synthetic barometric pressure time series:
  - Base pressure around 1013 hPa
  - Small variations (weather, movement)
We apply veil_barometer to simulate drift and fake altitude changes.
"""

import os
import sys
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import veil_barometer
from data_veil_core.random_control import get_rng


def synth_barometer(n: int = 500, dt: float = 0.1) -> dict:
    rng = get_rng()
    t = np.linspace(0, (n - 1) * dt, n, dtype=np.float32)

    # Base sea-level like pressure with slow oscillation
    base_pressure = 1013.0  # hPa
    slow_wave = 2.0 * np.sin(2.0 * np.pi * 0.01 * t)  # slow variation
    noise = rng.normal(0.0, 0.2, size=n)  # small measurement noise

    pressure = base_pressure + slow_wave + noise

    return {"t": t, "pressure": pressure}


def summarize_baro(label: str, baro: dict) -> None:
    p = baro["pressure"]
    print(f"\n{label}")
    print(f"  pressure min..max: {p.min():.2f} .. {p.max():.2f}")


def main():
    baro = synth_barometer()
    veiled = veil_barometer(baro, strength=1.3)

    summarize_baro("Trusted barometer", baro)
    summarize_baro("Veiled barometer", veiled)

    diff = np.abs(baro["pressure"] - veiled["pressure"])
    print("\nDifferences (absolute):")
    print(f"  mean: {diff.mean():.3f}")
    print(f"  max:  {diff.max():.3f}")


if __name__ == "__main__":
    main()
