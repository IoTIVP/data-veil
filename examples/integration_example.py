"""
DATA VEIL – Integration Example (Sci-Fi / DARPA Mode)

This script shows how a robotics / security engineer might use the
data_veil_core API in their own code.

We:
  - Synthesize fake sensor data (depth, LiDAR, radar, thermal, IMU)
  - Apply the veiling functions
  - Print a summary of how the data changed

Goal: Demonstrate how Data Veil would sit on the "exposure boundary":
internal code uses TRUTH, external / untrusted consumers get VEILED.

This version:
  - Uses the global RNG from data_veil_core.random_control (DATA_VEIL_SEED)
  - Avoids unicode characters so Windows consoles don't choke.
"""

import os
import sys
import numpy as np

# --- Ensure project root is on sys.path ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import (
    veil_depth,
    veil_lidar,
    veil_thermal,
    veil_radar,
    veil_imu,
)
from data_veil_core.random_control import get_rng

# Shared RNG (respects DATA_VEIL_SEED)
rng = get_rng()


def synth_depth(h: int = 64, w: int = 96) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w]
    yy_norm = yy / max(h - 1, 1)
    xx_norm = xx / max(w - 1, 1)
    base = 1.0 + 2.0 * yy_norm + 0.5 * np.sin(2 * np.pi * xx_norm)
    noise = rng.normal(0.0, 0.03, size=base.shape)
    return base + noise


def synth_lidar_ranges(n: int = 128) -> np.ndarray:
    angles = np.linspace(-np.pi, np.pi, n)
    base = 4.0 * np.ones_like(angles)
    front = np.abs(angles) < np.deg2rad(25)
    base[front] = 1.5  # wall in front
    side = (angles > np.deg2rad(60)) & (angles < np.deg2rad(120))
    base[side] = 2.5
    noise = rng.normal(0.0, 0.05, size=base.shape)
    return base + noise


def synth_radar_map(r: int = 48, v: int = 32) -> np.ndarray:
    # simple blob + noise
    rows = np.linspace(0, 1, r)
    cols = np.linspace(-1, 1, v)
    grid_r, grid_v = np.meshgrid(rows, cols, indexing="ij")
    base = 0.05 * np.ones_like(grid_r)

    # one target
    base += np.exp(
        -(((grid_r - 0.5) ** 2) / (2 * 0.05 ** 2)
          + ((grid_v - 0.2) ** 2) / (2 * 0.15 ** 2))
    )

    noise = rng.normal(0.0, 0.02, size=base.shape)
    return np.clip(base + noise, 0.0, None)


def synth_thermal(h: int = 48, w: int = 64) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w]
    center_y = h / 2
    center_x = w / 2
    dist = np.sqrt((yy - center_y) ** 2 + (xx - center_x) ** 2)
    base = 25.0 + 10.0 * np.exp(-(dist ** 2) / (2 * (min(h, w) / 4) ** 2))
    noise = rng.normal(0.0, 0.3, size=base.shape)
    return base + noise


def synth_imu(n: int = 200, dt: float = 0.01) -> dict:
    t = np.linspace(0, (n - 1) * dt, n)

    # Smooth rotation around Z
    gz = 0.4 * np.sin(2 * np.pi * 0.5 * t)
    gx = 0.05 * np.sin(2 * np.pi * 0.2 * t)
    gy = 0.03 * np.cos(2 * np.pi * 0.3 * t)

    # Gravity + small motion
    g = 9.81
    ax = 0.2 * np.sin(2 * np.pi * 0.7 * t)
    ay = 0.3 * np.cos(2 * np.pi * 0.4 * t)
    az = -g + 0.1 * np.sin(2 * np.pi * 0.6 * t)

    # measurement noise (use shared RNG)
    gx += rng.normal(0.0, 0.005, size=n)
    gy += rng.normal(0.0, 0.005, size=n)
    gz += rng.normal(0.0, 0.01, size=n)

    ax += rng.normal(0.0, 0.02, size=n)
    ay += rng.normal(0.0, 0.02, size=n)
    az += rng.normal(0.0, 0.02, size=n)

    return {
        "t": t,
        "gx": gx,
        "gy": gy,
        "gz": gz,
        "ax": ax,
        "ay": ay,
        "az": az,
    }


def summarize_sensor(name: str, trusted, veiled) -> None:
    """
    Utility to print basic stats before/after veiling.
    (No unicode so Windows encoding doesn't complain.)
    """
    trusted_arr = np.asarray(trusted)
    veiled_arr = np.asarray(veiled)

    print(f"\n=== {name} ===")
    print(f"  shape:             {trusted_arr.shape}")
    print(f"  trusted min..max:  {trusted_arr.min():.3f} .. {trusted_arr.max():.3f}")
    print(f"  veiled  min..max:  {veiled_arr.min():.3f} .. {veiled_arr.max():.3f}")
    diff = np.abs(trusted_arr - veiled_arr)
    print(f"  mean abs diff:     {diff.mean():.3f}")
    print(f"  max  abs diff:     {diff.max():.3f}")


def main():
    # Imagine these are your REAL sensor readings (trusted).
    depth = synth_depth()
    lidar_ranges = synth_lidar_ranges()
    radar_map = synth_radar_map()
    thermal = synth_thermal()
    imu = synth_imu()

    # On the exposure boundary, you decide to veil them
    depth_veiled = veil_depth(depth, strength=1.2)
    lidar_veiled = veil_lidar(lidar_ranges, strength=1.3)
    radar_veiled = veil_radar(radar_map, strength=1.0)
    thermal_veiled = veil_thermal(thermal, strength=1.0)
    imu_veiled = veil_imu(imu, strength=1.0)

    summarize_sensor("Depth", depth, depth_veiled)
    summarize_sensor("LiDAR ranges", lidar_ranges, lidar_veiled)
    summarize_sensor("Radar map", radar_map, radar_veiled)
    summarize_sensor("Thermal", thermal, thermal_veiled)

    # IMU is a dict; summarize gyro and accel separately
    summarize_sensor(
        "IMU gyro (gx, gy, gz)",
        np.vstack([imu["gx"], imu["gy"], imu["gz"]]),
        np.vstack([imu_veiled["gx"], imu_veiled["gy"], imu_veiled["gz"]]),
    )
    summarize_sensor(
        "IMU accel (ax, ay, az)",
        np.vstack([imu["ax"], imu["ay"], imu["az"]]),
        np.vstack([imu_veiled["ax"], imu_veiled["ay"], imu_veiled["az"]]),
    )

    print("\nIntegration example complete.")
    print("This is how you would call data_veil_core on raw sensor arrays.")
    print("Trusted = used internally; veiled = sent to untrusted consumers.")


if __name__ == "__main__":
    main()
