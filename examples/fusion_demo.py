"""
DATA VEIL – Fusion Timeseries Demo

We synthesize three aligned 1D sensor streams:

  - depth_front_mean      (e.g. mean depth in front of robot)
  - lidar_front_range     (e.g. primary lidar distance)
  - rf_power              (e.g. RF power level over time)

Then we apply veil_fusion_timeseries so all three are distorted by a
shared set of latent processes, but with different mixtures per sensor.

This shows how to apply a correlated fusion veil to multiple sensors at once.
"""

import os
import sys
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import veil_fusion_timeseries
from data_veil_core.random_control import get_rng


def synth_timeseries(n: int = 400, dt: float = 0.05):
    rng = get_rng()
    t = np.linspace(0, (n - 1) * dt, n, dtype=np.float32)

    # Simulated "forward mean depth" (meters)
    depth_base = 2.0 + 0.2 * np.sin(2.0 * np.pi * 0.03 * t)
    depth_noise = rng.normal(0.0, 0.05, size=n)
    depth_series = depth_base + depth_noise

    # Simulated lidar front range (meters)
    lidar_base = 3.0 + 0.3 * np.cos(2.0 * np.pi * 0.02 * t)
    lidar_noise = rng.normal(0.0, 0.07, size=n)
    lidar_series = lidar_base + lidar_noise

    # Simulated RF power (dB)
    rf_base = -65.0 + 2.0 * np.sin(2.0 * np.pi * 0.01 * t)
    rf_noise = rng.normal(0.0, 0.8, size=n)
    rf_series = rf_base + rf_noise

    sensors = {
        "depth_front_mean": depth_series,
        "lidar_front_range": lidar_series,
        "rf_power": rf_series,
    }

    return t, sensors


def summarize_series(label: str, series: dict):
    print(f"\n{label}")
    for name, arr in series.items():
        arr = np.asarray(arr)
        print(f"  {name}: min..max = {arr.min():.3f} .. {arr.max():.3f}")


def main():
    t, sensors = synth_timeseries()
    veiled = veil_fusion_timeseries(sensors, strength=1.2)

    summarize_series("Trusted series", sensors)
    summarize_series("Veiled series", veiled)

    print("\nDifferences (mean abs) per sensor:")
    for name, base in sensors.items():
        diff = np.abs(np.asarray(base) - np.asarray(veiled[name]))
        print(f"  {name}: mean |diff| = {diff.mean():.4f}, max |diff| = {diff.max():.4f}")


if __name__ == "__main__":
    main()
