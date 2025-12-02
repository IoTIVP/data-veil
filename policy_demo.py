"""
DATA VEIL – Policy Layer Demonstration (v0.2 foundation)

This example loads config/policy.yaml and prints:
- which clients are trusted
- whether they get REAL or VEILED sensor data
- then shows how Data Veil would apply the policy
"""

import yaml
from pathlib import Path
import numpy as np

# Import your existing demo functions
from run_demo import generate_depth_field, apply_data_veil, depth_to_image
from run_lidar_demo import generate_lidar_scan, apply_data_veil_lidar, lidar_to_image


def load_policy(path="config/policy.yaml"):
    """
    Load YAML policy file.
    """
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_sensor_view(policy_entry: dict, sensor_type: str = "depth"):
    """
    Return either REAL or VEILED depending on policy.
    """
    view = policy_entry.get("sensor_view", "veiled")

    if sensor_type == "depth":
        data = generate_depth_field()

        if view == "real":
            return data, "REAL"
        else:
            return apply_data_veil(data), "VEILED"

    elif sensor_type == "lidar":
        data = generate_lidar_scan(360)

        if view == "real":
            return data, "REAL"
        else:
            return apply_data_veil_lidar(data), "VEILED"

    else:
        raise ValueError("Unknown sensor type")


def demo_policy():
    """
    Demonstrate Data Veil's logical policy layer.
    """
    policy = load_policy()

    print("\n📘 Loaded Policy:")
    for entry in policy["policies"]:
        print(f" - {entry['client']}: {entry['sensor_view']} ({entry['trust']})")

    print("\n📡 Running policy simulation for each client...\n")

    for entry in policy["policies"]:
        client = entry["client"]

        # Depth view
        depth_data, depth_view = get_sensor_view(entry, "depth")
        print(f"{client}: Depth View → {depth_view}")

        # LiDAR view
        lidar_data, lidar_view = get_sensor_view(entry, "lidar")
        print(f"{client}: LiDAR View → {lidar_view}\n")

    print("✔ Policy demo complete.\n")


if __name__ == "__main__":
    demo_policy()
