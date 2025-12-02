"""
DATA VEIL – Veil Profiles Demo (RF Power)

Demonstrates how to use named profiles:
    "light", "privacy", "ghost", "chaos"

We synthesize a simple RF power time series and then apply
veil_rf under different profiles, using get_profile_strength.
"""

import os
import sys
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import veil_rf, get_profile_strength, list_profiles
from data_veil_core.random_control import get_rng


def synth_rf(n: int = 300, dt: float = 0.05):
    rng = get_rng()
    t = np.linspace(0, (n - 1) * dt, n, dtype=np.float32)

    base_level = -65.0
    slow_fade = 2.0 * np.sin(2.0 * np.pi * 0.01 * t)
    noise = rng.normal(0.0, 0.8, size=n)

    power = base_level + slow_fade + noise

    return t, power


def main():
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is required for this demo. Install with:")
        print("    pip install matplotlib")
        return

    t, rf_power = synth_rf()

    profiles = list_profiles()
    profiles = sorted(profiles)

    veiled_by_profile = {}
    for p in profiles:
        strength = get_profile_strength(p, "rf")
        veiled = veil_rf({"t": t, "power": rf_power}, strength=strength)
        veiled_by_profile[p] = veiled["power"]

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(t, rf_power, label="trusted", linewidth=2.0)

    for p in profiles:
        ax.plot(t, veiled_by_profile[p], label=f"profile: {p}")

    ax.set_title("DATA VEIL – RF Power Veil Profiles")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("RF power (dB)")
    ax.grid(True, linestyle="--", linewidth=0.3)
    ax.legend()

    out_path = os.path.join(CURRENT_DIR, "rf_profiles_demo.png")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print("Saved RF profiles demo to:")
    print(f"  {out_path}")


if __name__ == "__main__":
    main()
