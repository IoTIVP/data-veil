"""
DATA VEIL – Ultrasonic Demo

Synthetic ultrasonic range time series:
  - Base distance with small movement / jitter
We apply veil_ultrasonic to simulate:
  - baseline bias
  - dead zones
  - phantom obstacles
  - adaptive noise
"""

import os
import sys
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import veil_ultrasonic
from data_veil_core.random_control import get_rng


def synth_ultrasonic(n: int = 400, dt: float = 0.05) -> dict:
    rng = get_rng()
    t = np.linspace(0, (n - 1) * dt, n, dtype=np.float32)

    # Base distance ~ 1.5 m with small oscillations
    base_dist = 1.5
    slow_motion = 0.1 * np.sin(2.0 * np.pi * 0.03 * t)
    noise = rng.normal(0.0, 0.02, size=n)

    ranges = base_dist + slow_motion + noise
    ranges = np.clip(ranges, 0.05, 4.0)  # plausible ultrasonic span

    return {"t": t, "range": ranges}


def summarize_us(label: str, us: dict) -> None:
    r = us["range"]
    print(f"\n{label}")
    print(f"  range min..max: {r.min():.3f} .. {r.max():.3f}")


def main():
    us = synth_ultrasonic()
    veiled = veil_ultrasonic(us, strength=1.3)

    summarize_us("Trusted ultrasonic", us)
    summarize_us("Veiled ultrasonic", veiled)

    diff = np.abs(us["range"] - veiled["range"])
    print("\nDifferences (absolute):")
    print(f"  mean: {diff.mean():.4f}")
    print(f"  max:  {diff.max():.4f}")


if __name__ == "__main__":
    main()
