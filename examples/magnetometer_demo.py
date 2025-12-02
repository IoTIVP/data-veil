"""
DATA VEIL – Magnetometer Demo

Synthetic magnetometer time series:
  - Robot walking around a building
  - Earth's field plus small movements
We then apply veil_magnetometer to simulate soft-iron drift and magnetic ghosts.
"""

import os
import sys
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import veil_magnetometer
from data_veil_core.random_control import get_rng


def synth_magnetometer(n: int = 300, dt: float = 0.05) -> dict:
    rng = get_rng()
    t = np.linspace(0, (n - 1) * dt, n, dtype=np.float32)

    # Base field roughly pointing in some direction with small motion
    base_dir = np.array([0.3, 0.1, 0.9], dtype=np.float32)
    base_dir /= max(np.linalg.norm(base_dir), 1e-6)

    mag_strength = 45.0  # microtesla scale
    mx = np.full(n, mag_strength * base_dir[0], dtype=np.float32)
    my = np.full(n, mag_strength * base_dir[1], dtype=np.float32)
    mz = np.full(n, mag_strength * base_dir[2], dtype=np.float32)

    # small oscillations as the robot turns
    yaw = 0.5 * np.sin(2 * np.pi * 0.1 * t)
    pitch = 0.2 * np.sin(2 * np.pi * 0.05 * t)

    # apply simple yaw/pitch rotation to base field
    cos_yaw = np.cos(yaw)
    sin_yaw = np.sin(yaw)
    cos_pitch = np.cos(pitch)
    sin_pitch = np.sin(pitch)

    # for simplicity, apply yaw then pitch
    # base vector in world frame:
    bx = mx.copy()
    by = my.copy()
    bz = mz.copy()

    # yaw around Z
    x_yaw = bx * cos_yaw - by * sin_yaw
    y_yaw = bx * sin_yaw + by * cos_yaw
    z_yaw = bz

    # pitch around Y
    x_rot = x_yaw * cos_pitch + z_yaw * sin_pitch
    y_rot = y_yaw
    z_rot = -x_yaw * sin_pitch + z_yaw * cos_pitch

    mx = x_rot
    my = y_rot
    mz = z_rot

    # measurement noise
    mx += rng.normal(0.0, 0.1, size=n)
    my += rng.normal(0.0, 0.1, size=n)
    mz += rng.normal(0.0, 0.1, size=n)

    return {"t": t, "mx": mx, "my": my, "mz": mz}


def summarize_mag(label: str, mag: dict) -> None:
    mx = mag["mx"]
    my = mag["my"]
    mz = mag["mz"]

    print(f"\n{label}")
    print(f"  mx min..max: {mx.min():.2f} .. {mx.max():.2f}")
    print(f"  my min..max: {my.min():.2f} .. {my.max():.2f}")
    print(f"  mz min..max: {mz.min():.2f} .. {mz.max():.2f}")


def main():
    mag = synth_magnetometer()
    veiled = veil_magnetometer(mag, strength=1.3)

    summarize_mag("Trusted magnetometer", mag)
    summarize_mag("Veiled magnetometer", veiled)

    # difference stats
    diff_mx = np.abs(mag["mx"] - veiled["mx"])
    diff_my = np.abs(mag["my"] - veiled["my"])
    diff_mz = np.abs(mag["mz"] - veiled["mz"])

    print("\nDifferences (absolute):")
    print(f"  mx mean / max: {diff_mx.mean():.3f} / {diff_mx.max():.3f}")
    print(f"  my mean / max: {diff_my.mean():.3f} / {diff_my.max():.3f}")
    print(f"  mz mean / max: {diff_mz.mean():.3f} / {diff_mz.max():.3f}")


if __name__ == "__main__":
    main()
