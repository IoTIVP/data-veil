"""
DATA VEIL – Real-time-ish Depth Playback Demo

Generates a short sequence of synthetic depth frames, applies veil_depth
to each, and saves them under:

  examples/realtime_depth/trusted_###.png
  examples/realtime_depth/veiled_###.png
"""

import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# Make project root importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_veil_core import veil_depth


def synth_depth_frame(t: float, h: int = 64, w: int = 96) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w]
    yy_norm = yy / max(h - 1, 1)
    xx_norm = xx / max(w - 1, 1)

    # moving wavefront + gradient (toy scene)
    wave = 0.4 * np.sin(2 * np.pi * (xx_norm * 1.2 + t * 0.6))
    base = 1.0 + 2.0 * yy_norm + wave
    noise = np.random.normal(0.0, 0.03, size=base.shape)
    return base + noise


def depth_to_image(depth: np.ndarray) -> Image.Image:
    d_min = float(depth.min())
    d_max = float(depth.max())
    span = max(d_max - d_min, 1e-6)
    norm = (depth - d_min) / span
    arr = (norm * 255.0).clip(0, 255).astype("uint8")
    return Image.fromarray(arr, mode="L")


def main(num_frames: int = 30):
    out_dir = Path(PROJECT_ROOT) / "examples" / "realtime_depth"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Saving frames to:", out_dir)

    for i in range(num_frames):
        t = i / max(num_frames - 1, 1)
        depth = synth_depth_frame(t)
        veiled = veil_depth(depth, strength=1.2)

        trusted_img = depth_to_image(depth)
        veiled_img = depth_to_image(veiled)

        trusted_path = out_dir / f"trusted_{i:03d}.png"
        veiled_path = out_dir / f"veiled_{i:03d}.png"

        trusted_img.save(trusted_path)
        veiled_img.save(veiled_path)

        print(f"Frame {i:03d}: {trusted_path.name}, {veiled_path.name}")

    print("\n✅ Real-time-ish depth demo complete.")
    print("Open the PNG sequence to see how the scene + veiling evolve over time.")


if __name__ == "__main__":
    main()
