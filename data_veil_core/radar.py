"""
Radar range–Doppler veiling – Sci-Fi / DARPA mode.

Input:
    radar_map: 2D numpy array (range_bins, velocity_bins)

Output:
    veiled map with:
      - ghost targets
      - attenuated/erased returns
      - structured ripple noise
"""

from __future__ import annotations
import numpy as np


def veil_radar(radar_map: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Apply sci-fi veiling to a radar range–Doppler intensity map.

    Args:
        radar_map: 2D numpy array in arbitrary units.
        strength: distortion intensity.

    Returns:
        2D numpy array of same shape.
    """
    if radar_map.ndim != 2:
        raise ValueError("veil_radar expects a 2D array.")

    rng = np.random.default_rng()
    m = radar_map.astype(np.float32).copy()
    rows, cols = m.shape

    # Normalize to [0,1]
    v_min = float(np.min(m))
    v_max = float(np.max(m))
    span = max(v_max - v_min, 1e-6)
    norm = (m - v_min) / span

    # --- 1) Ghost targets (random blobs) ---
    ghost_count = int(5 * strength)
    r_lin = np.linspace(0, 1, rows)
    v_lin = np.linspace(-1, 1, cols)
    grid_r, grid_v = np.meshgrid(r_lin, v_lin, indexing="ij")

    def gaussian(cx, cy, sx, sy, amp):
        return amp * np.exp(
            -(((grid_r - cx) ** 2) / (2 * sx ** 2)
              + ((grid_v - cy) ** 2) / (2 * sy ** 2))
        )

    for _ in range(ghost_count):
        cx = rng.uniform(0.05, 0.95)
        cy = rng.uniform(-0.9, 0.9)
        sx = rng.uniform(0.02, 0.1)
        sy = rng.uniform(0.05, 0.2)
        amp = rng.uniform(0.3, 1.0) * strength

        norm += gaussian(cx, cy, sx, sy, amp)

    # --- 2) Attenuate real patches (erase lanes) ---
    patch_count = int(4 * strength)
    for _ in range(patch_count):
        r0 = rng.integers(0, max(1, rows - 6))
        c0 = rng.integers(0, max(1, cols - 4))
        r1 = min(rows, r0 + rng.integers(3, 12))
        c1 = min(cols, c0 + rng.integers(3, 8))
        norm[r0:r1, c0:c1] *= rng.uniform(0.0, 0.3)  # almost wiped

    # --- 3) Structured ripple + random noise ---
    ripple_row = 0.04 * strength * np.sin(
        np.linspace(0, 3 * np.pi, rows)
    )[:, None]
    ripple_col = 0.04 * strength * np.cos(
        np.linspace(0, 4 * np.pi, cols)
    )[None, :]

    norm += ripple_row
    norm += ripple_col

    noise = rng.normal(loc=0.0, scale=0.04 * strength, size=norm.shape)
    norm += noise

    norm = np.clip(norm, 0.0, 1.0)
    veiled = norm * span + v_min
    return veiled
