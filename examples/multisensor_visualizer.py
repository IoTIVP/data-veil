"""
DATA VEIL – Multi-Sensor Trusted vs Veiled Visualizer

This example:
  - Synthesizes four aligned 1D sensor streams:
      * depth_front_mean      (meters)
      * lidar_front_range     (meters)
      * rf_power              (dB)
      * ultrasonic_range      (meters)
  - Applies veil_fusion_timeseries to all four at once
  - Plots Trusted (top row) vs Veiled (bottom row) in a single figure

Output:
  examples/multisensor_trusted_vs_veiled.png
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


def synth_multisensor(n: int = 400, dt: float = 0.05):
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

    # Simulated ultrasonic range (meters)
    us_base = 1.5 + 0.1 * np.sin(2.0 * np.pi * 0.04 * t)
    us_noise = rng.normal(0.0, 0.02, size=n)
    us_series = np.clip(us_base + us_noise, 0.05, 4.0)

    sensors = {
        "depth_front_mean": depth_series,
        "lidar_front_range": lidar_series,
        "rf_power": rf_series,
        "ultrasonic_range": us_series,
    }

    return t, sensors


def main():
    # Local import to avoid hard dependency if matplotlib is not installed
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is required for this demo. Install with:")
        print("    pip install matplotlib")
        return

    t, trusted = synth_multisensor()
    veiled = veil_fusion_timeseries(trusted, strength=1.2)

    # Prepare figure
    sensor_names = [
        "depth_front_mean",
        "lidar_front_range",
        "rf_power",
        "ultrasonic_range",
    ]
    titles = [
        "Depth (front mean)",
        "LiDAR (front range)",
        "RF power",
        "Ultrasonic range",
    ]

    fig, axes = plt.subplots(
        nrows=2,
        ncols=len(sensor_names),
        figsize=(16, 6),
        sharex=True,
    )

    for col, (name, title) in enumerate(zip(sensor_names, titles)):
        ax_trusted = axes[0, col]
        ax_veiled = axes[1, col]

        y_trusted = trusted[name]
        y_veiled = veiled[name]

        ax_trusted.plot(t, y_trusted)
        ax_trusted.set_title(f"{title}\nTrusted")
        ax_trusted.grid(True, linestyle="--", linewidth=0.3)

        ax_veiled.plot(t, y_veiled)
        ax_veiled.set_title("Veiled")
        ax_veiled.grid(True, linestyle="--", linewidth=0.3)

    for ax in axes[1, :]:
        ax.set_xlabel("time (s)")

    fig.suptitle("DATA VEIL – Multi-Sensor Trusted vs Veiled", fontsize=14)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    out_path = os.path.join(CURRENT_DIR, "multisensor_trusted_vs_veiled.png")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print("Saved multi-sensor trusted vs veiled visualization to:")
    print(f"  {out_path}")


if __name__ == "__main__":
    main()
