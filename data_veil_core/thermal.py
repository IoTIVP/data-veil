"""
Thermal / IR veiling – Sci-Fi / DARPA mode.

Input:
    thermal: 2D numpy array (H, W) with arbitrary units (e.g., °C or normalized).

Output:
    veiled thermal map with:
      - hot/cold spot spoofing
      - smeared gradients
      - thermal "ghosts" and wiped regions
"""

from __future__ import annotations
import numpy as np


def veil_thermal(thermal: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Veil thermal data with phantom heat / cold signatures.

    Args:
        thermal: 2D numpy array
        strength: intensity of veiling

    Returns:
        2D numpy array of same shape.
    """
    if thermal.ndim != 2:
        raise ValueError("veil_thermal expects a 2D array.")

    t = thermal.astype(np.float32).copy()
    h, w = t.shape
    rng = np.random.default_rng()

    t_min = float(np.min(t))
    t_max = float(np.max(t))
    span = max(t_max - t_min, 1e-3)

    # Normalize
    norm = (t - t_min) / span

    # --- 1) Phantom hot/cold spots ---

    spot_count = int(6 * strength)
    for _ in range(spot_count):
        cy = rng.integers(0, h)
        cx = rng.integers(0, w)
        ry = rng.integers(h // 20, h // 8 + 1)
        rx = rng.integers(w // 20, w // 8 + 1)
        y0 = max(cy - ry, 0)
        y1 = min(cy + ry, h)
        x0 = max(cx - rx, 0)
        x1 = min(cx + rx, w)

        # Randomly choose hot or cold
        if rng.random() < 0.5:
            # Hot patch
            norm[y0:y1, x0:x1] = np.clip(norm[y0:y1, x0:x1] + 0.4 * strength, 0.0, 1.0)
        else:
            # Cold patch
            norm[y0:y1, x0:x1] = np.clip(norm[y0:y1, x0:x1] - 0.4 * strength, 0.0, 1.0)

    # --- 2) Directional smear (simulated conduction / blur streaks) ---

    yy, xx = np.mgrid[0:h, 0:w]
    angle = rng.uniform(0, 2 * np.pi)
    dir_y = np.sin(angle)
    dir_x = np.cos(angle)

    # create a ramp aligned with the chosen direction
    ramp = (yy * dir_y + xx * dir_x) / max(h, w)
    smear = 0.15 * strength * ramp
    norm = np.clip(norm + smear, 0.0, 1.0)

    # --- 3) Erase some structure (flat dead zones) ---

    zone_count = int(3 * strength)
    for _ in range(zone_count):
        cy = rng.integers(0, h)
        cx = rng.integers(0, w)
        ry = rng.integers(h // 10, h // 5 + 1)
        rx = rng.integers(w // 10, w // 5 + 1)
        y0 = max(cy - ry, 0)
        y1 = min(cy + ry, h)
        x0 = max(cx - rx, 0)
        x1 = min(cx + rx, w)

        # flatten to mean
        region = norm[y0:y1, x0:x1]
        norm[y0:y1, x0:x1] = float(np.mean(region))

    # --- 4) Add noise ---

    noise = rng.normal(loc=0.0, scale=0.05 * strength, size=norm.shape)
    norm = np.clip(norm + noise, 0.0, 1.0)

    veiled = norm * span + t_min
    return veiled
