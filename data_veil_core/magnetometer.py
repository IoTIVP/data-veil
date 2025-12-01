"""
Magnetometer veiling – soft-iron distortion and magnetic "ghosts" (hardened).

Input format:
    mag: dict with keys:
        "t":  (N,) time
        "mx": (N,) magnetic field X
        "my": (N,) magnetic field Y
        "mz": (N,) magnetic field Z

Output:
    new dict with:
        - multi-frequency bias drift (simulated soft-iron / hard-iron changes)
        - local anomalies with varying shapes (fake machinery, cables, motors)
        - adaptive random jitter based on signal magnitude

Design goals:
    - Plausible for external observers.
    - Very difficult to invert or "subtract out" statistically.
"""

from typing import Dict
import numpy as np
from .random_control import get_rng


def veil_magnetometer(mag: Dict[str, np.ndarray], strength: float = 1.0) -> Dict[str, np.ndarray]:
    """
    Veil magnetometer data with drift and magnetic ghosts.

    Args:
        mag: dict with keys "t", "mx", "my", "mz"
        strength: distortion intensity (typical range 0.5 .. 2.0)

    Returns:
        new dict with same keys.
    """
    required = {"t", "mx", "my", "mz"}
    missing = required - set(mag.keys())
    if missing:
        raise ValueError(f"veil_magnetometer missing keys: {missing}")

    veiled = {k: np.asarray(v, dtype=np.float32).copy() for k, v in mag.items()}
    t = veiled["t"]
    n = t.shape[0]
    if n == 0:
        return veiled

    rng = get_rng()

    mx = veiled["mx"]
    my = veiled["my"]
    mz = veiled["mz"]

    # Basic stats for scaling
    stacked = np.vstack([mx, my, mz])
    span = float(stacked.max() - stacked.min())
    span = max(span, 1e-3)
    std = float(stacked.std())
    std = max(std, 1e-3)

    # Normalize time to 0..1
    t_norm = (t - t[0]) / max(t[-1] - t[0], 1e-6)

    # --- 1) Multi-frequency bias drift (history-dependent) ---

    # Several sinusoidal components with random phases and frequencies
    # This creates a complex, non-trivial drift that depends on full series.
    freqs = np.array([0.3, 0.7, 1.3], dtype=np.float32) * strength
    phases = rng.uniform(0.0, 2.0 * np.pi, size=freqs.shape[0])

    drift_x = np.zeros_like(t_norm, dtype=np.float32)
    drift_y = np.zeros_like(t_norm, dtype=np.float32)
    drift_z = np.zeros_like(t_norm, dtype=np.float32)

    for i, f in enumerate(freqs):
        angle = 2.0 * np.pi * f * t_norm + phases[i]
        # Axis-specific weights
        w = rng.normal(0.0, 1.0, size=3)
        w /= max(np.linalg.norm(w), 1e-6)

        drift_x += w[0] * np.sin(angle)
        drift_y += w[1] * np.cos(angle)
        drift_z += w[2] * np.sin(angle + 0.5)

    # History-dependent cumulative component
    # Integrate a small random step to create drift that cannot be modeled
    # with simple sinusoids alone.
    step_scale = 0.01 * strength
    random_steps = rng.normal(0.0, step_scale, size=(n, 3)).astype(np.float32)
    cumulative = np.cumsum(random_steps, axis=0)

    drift_x += cumulative[:, 0]
    drift_y += cumulative[:, 1]
    drift_z += cumulative[:, 2]

    # Scale relative to span
    drift_scale = 0.05 * span  # 5% of range at full strength
    mx += drift_scale * drift_x
    my += drift_scale * drift_y
    mz += drift_scale * drift_z

    # --- 2) Local anomalies with varying shapes ---

    # Each anomaly has:
    #  - random center and duration
    #  - random shape type (bump, ramp, asymmetric)
    #  - random direction in 3D field space
    anomaly_count = int(4 * strength) + rng.integers(0, 3)
    anomaly_count = max(anomaly_count, 1)

    for _ in range(anomaly_count):
        center = rng.integers(5, max(6, n - 5))
        span_len = rng.integers(8, 40)
        end = min(n, center + span_len)
        if end <= center:
            continue

        window_len = end - center
        base = np.linspace(0.0, 1.0, window_len, dtype=np.float32)

        shape_type = rng.choice(["bump", "ramp", "asym_bump"])
        if shape_type == "bump":
            shape = base * (1.0 - base) * 4.0  # symmetric
        elif shape_type == "ramp":
            shape = base
        else:  # asym_bump
            shape = base * np.exp(-2.0 * base)

        # Random direction and amplitude
        direction = rng.normal(0.0, 1.0, size=3)
        direction /= max(np.linalg.norm(direction), 1e-6)

        # Amplitude scaled from std and strength
        amp = (0.5 + 0.5 * rng.random()) * std * strength

        mx[center:end] += direction[0] * amp * shape
        my[center:end] += direction[1] * amp * shape
        mz[center:end] += direction[2] * amp * shape

    # --- 3) Adaptive high-frequency jitter ---

    # Use std to scale jitter; add slightly different characteristics per axis.
    jitter_base = 0.05 * std * strength
    mx += rng.normal(0.0, jitter_base, size=n)
    my += rng.normal(0.0, jitter_base * 1.2, size=n)
    mz += rng.normal(0.0, jitter_base * 0.8, size=n)

    veiled["mx"] = mx
    veiled["my"] = my
    veiled["mz"] = mz

    return veiled
