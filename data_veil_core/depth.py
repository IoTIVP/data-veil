"""
Depth veiling – Sci-Fi / DARPA mode.

Input:
    depth_map: 2D numpy array of floats (depth values, any units).

Output:
    veiled_depth: 2D numpy array with:
      - local warping
      - punched holes
      - fake foreground “walls”
      - jittered noise

This is designed to look like a corrupted / adversarial depth field
that still feels geometrically plausible to a naive consumer.
"""

from __future__ import annotations
import numpy as np


def veil_depth(depth_map: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Apply a sci-fi distortion field to a depth map.

    Args:
        depth_map: 2D numpy array of depth values (H, W).
        strength:  overall veiling intensity multiplier (0.5 .. 2.0 recommended).

    Returns:
        veiled_depth: 2D numpy array of same shape.
    """
    if depth_map.ndim != 2:
        raise ValueError("veil_depth expects a 2D depth map array.")

    depth = depth_map.astype(np.float32).copy()
    h, w = depth.shape

    # Normalize to [0,1] for manipulation
    d_min = np.min(depth)
    d_max = np.max(depth)
    if d_max - d_min < 1e-6:
        # Flat depth (degenerate), just add structured noise
        d_norm = np.zeros_like(depth)
    else:
        d_norm = (depth - d_min) / (d_max - d_min)

    # --- 1) Smooth “warp” field (like a gravitational lensing effect) ---

    yy, xx = np.mgrid[0:h, 0:w]
    yy_norm = yy / max(h - 1, 1)
    xx_norm = xx / max(w - 1, 1)

    # Low-frequency sinusoidal offset patterns
    warp_y = 0.03 * strength * np.sin(2 * np.pi * (xx_norm * 1.3 + yy_norm * 0.7))
    warp_x = 0.03 * strength * np.cos(2 * np.pi * (xx_norm * 0.9 - yy_norm * 1.1))

    # Compute warped coordinates
    yy_warp = np.clip(yy + warp_y * h, 0, h - 1)
    xx_warp = np.clip(xx + warp_x * w, 0, w - 1)

    # Bilinear-ish sampling
    y0 = np.floor(yy_warp).astype(int)
    x0 = np.floor(xx_warp).astype(int)
    y1 = np.clip(y0 + 1, 0, h - 1)
    x1 = np.clip(x0 + 1, 0, w - 1)

    wy = yy_warp - y0
    wx = xx_warp - x0

    top_left = d_norm[y0, x0]
    top_right = d_norm[y0, x1]
    bot_left = d_norm[y1, x0]
    bot_right = d_norm[y1, x1]

    warped = (
        top_left * (1 - wy) * (1 - wx)
        + top_right * (1 - wy) * wx
        + bot_left * wy * (1 - wx)
        + bot_right * wy * wx
    )

    d_veiled = warped

    # --- 2) Punch “voids” and fake walls ---

    rng = np.random.default_rng()

    # Voids: patches forced to maximum depth (holes / missing surfaces)
    for _ in range(int(5 * strength)):
        cy = rng.integers(0, h)
        cx = rng.integers(0, w)
        ry = rng.integers(h // 20, h // 8 + 1)
        rx = rng.integers(w // 20, w // 8 + 1)
        y0 = max(cy - ry, 0)
        y1 = min(cy + ry, h)
        x0 = max(cx - rx, 0)
        x1 = min(cx + rx, w)
        d_veiled[y0:y1, x0:x1] = 1.0  # “infinite” depth

    # Fake walls: narrow bands forced closer than surroundings
    for _ in range(int(4 * strength)):
        cy = rng.integers(int(h * 0.2), int(h * 0.9))
        thickness = rng.integers(1, max(2, h // 40))
        x0 = rng.integers(0, w // 2)
        x1 = rng.integers(w // 2, w)
        band = d_veiled[cy:cy + thickness, x0:x1]
        band = np.clip(band - (0.3 + 0.3 * rng.random()), 0.0, 1.0)  # closer
        d_veiled[cy:cy + thickness, x0:x1] = band

    # --- 3) Edge noise & quantization ---

    # Add light high-frequency noise
    noise = rng.normal(loc=0.0, scale=0.02 * strength, size=d_veiled.shape)
    d_veiled = np.clip(d_veiled + noise, 0.0, 1.0)

    # Slight quantization to create banding (bad depth discretization effect)
    levels = int(32 * strength)
    levels = max(8, min(levels, 64))
    d_veiled = np.round(d_veiled * levels) / levels

    # Map back to original depth range
    veiled_depth = d_veiled * (d_max - d_min) + d_min

    return veiled_depth
