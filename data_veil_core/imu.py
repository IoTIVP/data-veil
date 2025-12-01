"""
IMU veiling – Sci-Fi / DARPA mode.

Input:
    imu_dict with:
        t:  (N,)
        gx, gy, gz: (N,) gyro rates
        ax, ay, az: (N,) accelerations

Output:
    new dict with:
        - slow drift
        - fake impact spikes
        - jitter
"""

from __future__ import annotations
import numpy as np
from typing import Dict


def veil_imu(imu: Dict[str, np.ndarray], strength: float = 1.0) -> Dict[str, np.ndarray]:
    """
    Veil IMU data (gyro + accel) with sci-fi distortions.

    Args:
        imu: dict with keys "t", "gx", "gy", "gz", "ax", "ay", "az"
        strength: intensity of veiling

    Returns:
        new dict with same keys.
    """
    required = {"t", "gx", "gy", "gz", "ax", "ay", "az"}
    missing = required - set(imu.keys())
    if missing:
        raise ValueError(f"veil_imu missing keys: {missing}")

    veiled = {k: np.asarray(v, dtype=np.float32).copy() for k, v in imu.items()}
    n = veiled["t"].shape[0]
    if n == 0:
        return veiled

    rng = np.random.default_rng()

    # --- 1) Slow drift on some channels ---
    drift_scale = strength
    drift_gz = np.linspace(0.0, 0.3 * drift_scale, n)
    drift_ax = np.linspace(0.0, 1.0 * drift_scale, n)
    drift_ay = np.linspace(0.0, -0.7 * drift_scale, n)

    veiled["gz"] += drift_gz
    veiled["ax"] += drift_ax
    veiled["ay"] += drift_ay

    # --- 2) Fake impact spikes ---
    spike_count = int(6 * strength)
    for _ in range(spike_count):
        idx = rng.integers(5, max(6, n - 5))
        span = rng.integers(3, 10)
        end = min(n, idx + span)

        gyro_spike = rng.choice([-1.8, -1.2, 1.2, 1.8])
        accel_spike_x = rng.choice([-4.0, 4.0])
        accel_spike_y = rng.choice([-3.0, 3.0])
        accel_spike_z = rng.choice([-6.0, 6.0])

        veiled["gx"][idx:end] += gyro_spike
        veiled["gy"][idx:end] += gyro_spike * 0.7

        veiled["ax"][idx:end] += accel_spike_x
        veiled["ay"][idx:end] += accel_spike_y
        veiled["az"][idx:end] += accel_spike_z

    # --- 3) High-frequency jitter / sensor noise ---

    for key in ["gx", "gy", "gz"]:
        sigma = 0.05 * strength
        veiled[key] += rng.normal(0.0, sigma, size=n)

    for key in ["ax", "ay", "az"]:
        sigma = 0.2 * strength
        veiled[key] += rng.normal(0.0, sigma, size=n)

    return veiled
