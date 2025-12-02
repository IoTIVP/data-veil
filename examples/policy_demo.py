"""
DATA VEIL – Policy Demo

Shows how a system could choose veiling strength / modes based on a
simple YAML policy file.

This does NOT enforce anything itself – it just loads and prints the
decision logic that *would* be used at the exposure boundary.
"""

import os
import sys
import yaml

# Ensure project root is importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import veil_depth  # just to prove we can mix policy + core
import numpy as np


CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "policies.yaml")


def load_policies(path: str = CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def choose_profile(policies: dict, profile_name: str):
    profiles = policies.get("profiles", {})
    if profile_name not in profiles:
        raise KeyError(f"Profile '{profile_name}' not found in policies.")
    default = policies.get("default", {})
    profile = profiles[profile_name]

    # simple merge: profile overrides default
    merged = {
        "description": profile.get("description", default.get("description", "")),
        "strength_multiplier": profile.get(
            "strength_multiplier", default.get("strength_multiplier", 1.0)
        ),
        "modes": {**default.get("modes", {}), **profile.get("modes", {})},
    }
    return merged


def demo_policy_application():
    policies = load_policies()
    print("Loaded policies from:", CONFIG_PATH)

    for name in ["external_logs", "cloud_export", "internal_debug", "red_team"]:
        profile = choose_profile(policies, name)
        print(f"\n=== Profile: {name} ===")
        print(" description:", profile["description"])
        print(" strength_multiplier:", profile["strength_multiplier"])
        print(" modes:", profile["modes"])

    # Minimal “see it in action” example with depth:
    depth = np.random.rand(32, 48).astype(np.float32)
    print("\nDepth example (baseline vs red_team):")
    base_veiled = veil_depth(depth, strength=1.0)
    red_profile = choose_profile(policies, "red_team")
    red_strength = 1.0 * float(red_profile["strength_multiplier"])
    red_veiled = veil_depth(depth, strength=red_strength)

    print("  trusted  min..max:", float(depth.min()), "..", float(depth.max()))
    print("  base     min..max:", float(base_veiled.min()), "..", float(base_veiled.max()))
    print("  red_team min..max:", float(red_veiled.min()), "..", float(red_veiled.max()))


if __name__ == "__main__":
    demo_policy_application()
