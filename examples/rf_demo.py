"""
DATA VEIL – RF Power Demo

Synthetic RF power time series:
  - Base level around -65 dB (for example)
  - Slow fading-like variation
We apply veil_rf to simulate:
  - warped baseline
  - interference-like bursts
  - time-varying noise
"""

import os
import sys
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import veil_rf
from data_veil_core.random_control import get_rng


def synth_rf(n: int = 600, dt: float = 0.05) -> dict:
    rng = get_rng()
    t = np.linspace(0, (n - 1) * dt, n, dtype=np.float32)

    base_level = -65.0
    slow_fade = 2.0 * np.sin(2.0 * np.pi * 0.01 * t)
    noise = rng.normal(0.0, 0.8, size=n)

    power = base_level + slow_fade + noise

    return {"t": t, "power": power}


def summarize_rf(label: str, rf: dict) -> None:
    p = rf["power"]
    print(f"\n{label}")
    print(f"  power min..max: {p.min():.2f} .. {p.max():.2f}")


def main():
    rf = synth_rf()
    veiled = veil_rf(rf, strength=1.4)

    summarize_rf("Trusted RF", rf)
    summarize_rf("Veiled RF", veiled)

    diff = np.abs(rf["power"] - veiled["power"])
    print("\nDifferences (absolute):")
    print(f"  mean: {diff.mean():.3f}")
    print(f"  max:  {diff.max():.3f}")


if __name__ == "__main__":
    main()
