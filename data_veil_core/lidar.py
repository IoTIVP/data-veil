"""
LiDAR veiling – Sci-Fi / DARPA mode.

Supports two patterns:
    1) 1D distance array       -> N
    2) 2D point cloud (x,y,z)  -> (N, 3)

The goal is to:
    - inject ghost obstacles
    - erase or thin out real sectors
    - add range jitter
    - preserve overall "LiDAR-like" structure so it looks plausible at a glance
"""

import numpy as np
from .random_control import get_rng


def veil_lidar(lidar_data: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Veil LiDAR distances or point cloud in a sci-fi way.

    Args:
        lidar_data: numpy array
            - shape (N,)       distance values
            - or (N, 3)       x, y, z points
        strength: float
            intensity multiplier for distortion.

    Returns:
        veiled: numpy array of same shape.
    """
    arr = np.asarray(lidar_data).astype(np.float32)
    rng = get_rng()

    if arr.ndim == 1:
        return _veil_lidar_ranges(arr, strength=strength, rng=rng)
    elif arr.ndim == 2 and arr.shape[1] == 3:
        return _veil_lidar_points(arr, strength=strength, rng=rng)
    else:
        raise ValueError("veil_lidar expects shape (N,) or (N,3).")


def _veil_lidar_ranges(ranges: np.ndarray, strength: float, rng: np.random.Generator) -> np.ndarray:
    r = ranges.copy()
    n = r.shape[0]

    if n == 0:
        return r

    # Basic stats
    r_min = float(np.min(r))
    r_max = float(np.max(r))
    span = max(r_max - r_min, 1e-3)

    # --- 1) Add ghost returns (very close obstacles) ---
    ghost_count = int(6 * strength)
    for _ in range(ghost_count):
        idx = rng.integers(0, n)
        span_len = rng.integers(2, max(3, int(8 * strength)))
        end = min(n, idx + span_len)
        r[idx:end] = r_min + 0.05 * span  # extremely close phantom wedge

    # --- 2) Erase some real sectors (force to max) ---
    erase_count = int(4 * strength)
    for _ in range(erase_count):
        idx = rng.integers(0, n)
        span_len = rng.integers(4, max(5, int(10 * strength)))
        end = min(n, idx + span_len)
        r[idx:end] = r_max  # missing data / no returns

    # --- 3) Jitter remaining points ---
    jitter = rng.normal(loc=0.0, scale=0.03 * span * strength, size=r.shape)
    r = np.clip(r + jitter, r_min, r_max)

    return r


def _veil_lidar_points(points: np.ndarray, strength: float, rng: np.random.Generator) -> np.ndarray:
    pts = points.copy()
    n = pts.shape[0]
    if n == 0:
        return pts

    # Compute radial distance
    d = np.linalg.norm(pts[:, :2], axis=1)
    d_min = float(np.min(d))
    d_max = float(np.max(d))
    span = max(d_max - d_min, 1e-3)

    # --- 1) Ghost clouds (fake clusters) ---
    ghost_count = int(5 * strength)
    for _ in range(ghost_count):
        # pick a random existing point as seed
        idx = rng.integers(0, n)
        center = pts[idx]

        # create a small swarm around it
        swarm_size = rng.integers(10, 30)
        offsets = rng.normal(
            loc=0.0,
            scale=0.05 * span * strength,
            size=(swarm_size, 3),
        )
        ghost_swarm = center + offsets

        # optionally force them closer or farther
        scale_factor = rng.uniform(0.6, 1.4)
        ghost_swarm[:, :2] *= scale_factor

        pts = np.vstack([pts, ghost_swarm])

    # --- 2) Erase sectors (e.g., wedge in angle space) ---
    angles = np.arctan2(pts[:, 1], pts[:, 0])  # -pi..pi
    sector_count = int(3 * strength)
    mask = np.ones(pts.shape[0], dtype=bool)
    for _ in range(sector_count):
        center_angle = rng.uniform(-np.pi, np.pi)
        width = rng.uniform(0.1, 0.4) * strength
        sector = np.abs(np.angle(np.exp(1j * (angles - center_angle)))) < width
        # drop some of these
        drop_mask = sector & (rng.random(pts.shape[0]) < 0.5)
        mask[drop_mask] = False

    pts = pts[mask]

    # --- 3) Add jitter to remaining ---

    jitter = rng.normal(
        loc=0.0,
        scale=0.02 * span * strength,
        size=pts.shape,
    )
    pts += jitter

    return pts
