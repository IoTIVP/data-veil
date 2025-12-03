"""
Multi-Sensor + Profiles Demo for Data Veil

This script shows how different profiles affect multiple sensors.

It:
- Generates synthetic sensor arrays (depth, lidar, radar, thermal, IMU).
- Applies multiple profiles: light, privacy, ghost, chaos.
- Prints summary statistics for each sensor and profile.

Usage:
    python examples/multi_sensor_profiles_demo.py
"""

import os
import sys
from typing import Dict, Any

import numpy as np

# Make sure we can import data_veil_core when running from examples/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import (
    veil_depth,
    veil_lidar,
    veil_radar,
    veil_thermal,
    veil_imu,
)
from data_veil_core.random_control import set_seed
from data_veil_core.profiles import get_profile_strength, list_profiles


def generate_synthetic_sensors() -> Dict[str, Any]:
    """
    Produce a small bundle of synthetic sensor readings.

    Returns:
        Dictionary mapping sensor names to trusted arrays.
    """
    sensors: Dict[str, Any] = {}

    # Depth: 64 x 96
    x = np.linspace(0, 4 * np.pi, 96)
    y = np.linspace(0, 2 * np.pi, 64)
    X, Y = np.meshgrid(x, y)
    depth = 2.5 + 1.0 * np.sin(X) * np.cos(Y)
    depth += 0.1 * np.random.randn(64, 96)
    sensors["depth"] = np.abs(depth).astype(np.float32)

    # LiDAR ranges: 128 beams
    angles = np.linspace(-np.pi / 2, np.pi / 2, 128)
    base_range = 3.0 + 0.5 * np.cos(3 * angles)
    base_range += 0.1 * np.random.randn(128)
    sensors["lidar"] = np.abs(base_range).astype(np.float32)

    # Radar: 48 x 32 range–Doppler
    radar = np.random.rand(48, 32).astype(np.float32)
    sensors["radar"] = radar

    # Thermal: 48 x 64, around 25-30 degrees
    thermal = 25.0 + 5.0 * np.random.rand(48, 64)
    sensors["thermal"] = thermal.astype(np.float32)

    # IMU: expected structure:
    # {
    #   "t": 1D array,
    #   "gx", "gy", "gz": 1D arrays (gyro),
    #   "ax", "ay", "az": 1D arrays (accel)
    # }
    n = 200
    t = np.linspace(0.0, 10.0, n).astype(np.float32)

    gx = 0.05 * np.random.randn(n).astype(np.float32)
    gy = 0.05 * np.random.randn(n).astype(np.float32)
    gz = 0.05 * np.random.randn(n).astype(np.float32)

    ax = 0.2 * np.random.randn(n).astype(np.float32)
    ay = 0.2 * np.random.randn(n).astype(np.float32)
    az = (-9.81 + 0.2 * np.random.randn(n)).astype(np.float32)

    imu = {
        "t": t,
        "gx": gx,
        "gy": gy,
        "gz": gz,
        "ax": ax,
        "ay": ay,
        "az": az,
    }
    sensors["imu"] = imu

    return sensors


def apply_veil(sensor_name: str, data: Any, strength: float) -> Any:
    """
    Route a sensor through the appropriate veil function.
    """
    if sensor_name == "depth":
        return veil_depth(data, strength=strength)
    elif sensor_name == "lidar":
        return veil_lidar(data, strength=strength)
    elif sensor_name == "radar":
        return veil_radar(data, strength=strength)
    elif sensor_name == "thermal":
        return veil_thermal(data, strength=strength)
    elif sensor_name == "imu":
        return veil_imu(data, strength=strength)
    else:
        raise ValueError(f"Unsupported sensor type: {sensor_name}")


def summarize_array(arr: np.ndarray) -> str:
    """
    Return a short summary string for a numeric array.
    """
    return f"shape={arr.shape}, min={arr.min():.3f}, max={arr.max():.3f}, mean={arr.mean():.3f}"


def main():
    print("Multi-sensor + profiles demo")
    set_seed(42)

    sensors = generate_synthetic_sensors()

    # Decide which profiles to try (only those that actually exist)
    wanted_profiles = ["light", "privacy", "ghost", "chaos"]
    available_profiles = set(list_profiles())
    profiles_to_use = [p for p in wanted_profiles if p in available_profiles]

    print("Available profiles:", sorted(available_profiles))
    print("Using profiles:", profiles_to_use)
    print()

    # For each profile, apply to each sensor and print stats
    for profile in profiles_to_use:
        print("=" * 60)
        print(f"Profile: {profile}")
        print("=" * 60)

        for sensor_name, trusted in sensors.items():
            strength = float(get_profile_strength(profile, sensor_name))

            if sensor_name == "imu":
                # IMU: dict of 1D arrays with keys t, gx, gy, gz, ax, ay, az
                veiled = apply_veil(sensor_name, trusted, strength=strength)

                print(f"[{sensor_name}] strength={strength:.2f}")

                # do not compute diffs on time axis "t"
                for key in ["gx", "gy", "gz", "ax", "ay", "az"]:
                    t_arr = trusted[key]
                    v_arr = veiled[key]
                    diff = np.abs(v_arr - t_arr)

                    print(f"  {key} trusted: {summarize_array(t_arr)}")
                    print(f"  {key} veiled : {summarize_array(v_arr)}")
                    print(
                        f"  {key} diff   : mean_abs_diff={diff.mean():.4f}, max_abs_diff={diff.max():.4f}"
                    )
                print()

            else:
                veiled = apply_veil(sensor_name, trusted, strength=strength)
                t_arr = trusted
                v_arr = veiled
                diff = np.abs(v_arr - t_arr)

                print(f"[{sensor_name}] strength={strength:.2f}")
                print(f"  trusted: {summarize_array(t_arr)}")
                print(f"  veiled : {summarize_array(v_arr)}")
                print(
                    f"  diff   : mean_abs_diff={diff.mean():.4f}, max_abs_diff={diff.max():.4f}"
                )
                print()

    print("Demo complete.")


if __name__ == "__main__":
    main()
