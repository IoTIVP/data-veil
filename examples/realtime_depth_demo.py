"""
Realtime-ish Depth Simulation + Data Veil Demonstration
-------------------------------------------------------

Opens a live window that updates depth frames continuously
and shows:

LEFT  = Trusted depth map (internal view)
RIGHT = Veiled depth map (untrusted external view)

Features:
- Live depth evolution
- Live veiling using Data Veil
- Keyboard profile switching:

    1 = light
    2 = privacy
    3 = ghost
    4 = chaos

Profiles are loaded from config/profiles.yaml (if present),
or from built-in defaults otherwise.
"""

import matplotlib
matplotlib.use("TkAgg")  # Force GUI backend on Windows

import matplotlib.pyplot as plt
import numpy as np
import time
import os
import sys

# Make sure we can import data_veil_core when running from examples/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import veil_depth
from data_veil_core.random_control import set_seed
from data_veil_core.profiles import get_profile_strength, list_profiles


# ----------------------------------------
# Generate synthetic depth frames
# ----------------------------------------

def generate_depth_frame(t: float) -> np.ndarray:
    """
    Create a synthetic depth map that evolves over time.
    """
    x = np.linspace(0, 4 * np.pi, 96)
    y = np.linspace(0, 2 * np.pi, 64)
    X, Y = np.meshgrid(x, y)

    # Time-evolving wave pattern
    depth = 2.5 + 1.0 * np.sin(X + t * 0.3) * np.cos(Y + t * 0.5)
    depth += 0.2 * np.random.randn(64, 96)

    # Ensure positive depth
    return np.abs(depth).astype(np.float32)


# ----------------------------------------
# Main realtime loop with profile switching
# ----------------------------------------

def main():
    print("Starting realtime depth demo with live profiles...")

    set_seed(42)

    # Initial time and frame
    t = 0.0
    depth = generate_depth_frame(t)

    # Default profile
    profiles_available = list_profiles()
    print("Available profiles:", profiles_available)

    current_profile = "privacy" if "privacy" in profiles_available else "light"
    print(f"Starting with profile: {current_profile}")

    def current_strength() -> float:
        # 'depth' as the sensor name for profile lookup
        return float(get_profile_strength(current_profile, "depth"))

    veiled = veil_depth(depth, strength=current_strength())

    # Setup plot
    plt.ion()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    fig.suptitle("Realtime Depth Simulation — Trusted vs Veiled", fontsize=14)

    ax_t = axes[0]
    ax_v = axes[1]

    im_t = ax_t.imshow(depth, cmap="viridis", vmin=0, vmax=5)
    ax_t.set_title("Trusted Depth")
    ax_t.axis("off")

    im_v = ax_v.imshow(veiled, cmap="inferno", vmin=0, vmax=5)
    ax_v.set_title(f"Veiled Depth (profile: {current_profile})")
    ax_v.axis("off")

    # HUD text for profile + strength
    hud_text = fig.text(
        0.5,
        0.02,
        f"Profile: {current_profile}  |  strength={current_strength():.2f}  (keys: 1=light, 2=privacy, 3=ghost, 4=chaos)",
        ha="center",
        va="bottom",
        fontsize=9,
    )

    plt.show(block=False)

    # Key → profile mapping
    key_to_profile = {
        "1": "light",
        "2": "privacy",
        "3": "ghost",
        "4": "chaos",
    }

    def on_key(event):
        nonlocal current_profile
        key = event.key
        if key in key_to_profile:
            new_profile = key_to_profile[key]
            if new_profile in profiles_available:
                current_profile = new_profile
                print(f"Switched profile to: {current_profile}")
            else:
                print(f"Profile '{new_profile}' not available (not in YAML/built-ins).")

    fig.canvas.mpl_connect("key_press_event", on_key)

    try:
        # Realtime update loop
        while plt.fignum_exists(fig.number):
            t += 0.2

            # Generate new frames
            depth = generate_depth_frame(t)
            veiled = veil_depth(depth, strength=current_strength())

            # Update plots
            im_t.set_data(depth)
            im_v.set_data(veiled)
            ax_v.set_title(f"Veiled Depth (profile: {current_profile})")

            hud_text.set_text(
                f"Profile: {current_profile}  |  strength={current_strength():.2f}  (keys: 1=light, 2=privacy, 3=ghost, 4=chaos)"
            )

            fig.canvas.draw()
            fig.canvas.flush_events()

            # Small delay to control update rate
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Interrupted by user.")

    print("Window closed. Demo ending.")


if __name__ == "__main__":
    main()
