"""
Ultrasonic range veiling – fake reflections and blind zones.

Input format:
    us: dict with keys:
        "t":      (N,) time
        "range":  (N,) distance readings (e.g. meters)

Output:
    new dict with:
        - multi-frequency baseline warping (subtle bias)
        - dead zones (ranges forced to max or near-zero)
        - phantom obstacles (shorter ranges)
        - adaptive noise

Goal:
    Make exposed ultrasonic logs unreliable for mapping and replay,
    while still looking like valid sensor behavior.
"""

from typing import Dict
import numpy as np
from .random_control import get_rng


def veil_ultrasonic(us: Dict[str, np.ndarray], strength: float = 1.0) -> Dict[str, np.ndarray]:
    """
    Veil ultrasonic time series.

    Args:
        us: dict with keys "t", "range"
        strength: distortion intensity (0.5 .. 2.0 typical)

    Returns:
        new dict with same keys.
    """
    required = {"t", "range"}
    missing = required - set(us.keys())
    if missing:
        raise ValueError(f"veil_ultrasonic missing keys: {missing}")

    veiled = {k: np.asarray(v, dtype=np.float32).copy() for k, v in us.items()}
    t = veiled["t"]
    r = veiled["range"]
    n = t.shape[0]

    if n == 0:
        return veiled

    rng = get_rng()

    r_min = float(r.min())
    r_max = float(r.max())
    span = max(r_max - r_min, 1e-3)
    std = float(r.std())
    std = max(std, 1e-3)

    # Normalize time 0..1
    t_norm = (t - t[0]) / max(t[-1] - t[0], 1e-6)

    # --- 1) Baseline warping (slight bias over time) ---

    freqs = np.array([0.2, 0.5], dtype=np.float32) * strength
    phases = rng.uniform(0.0, 2.0 * np.pi, size=freqs.shape[0])

    baseline = np.zeros_like(t_norm, dtype=np.float32)
    for i, f in enumerate(freqs):
        angle = 2.0 * np.pi * f * t_norm + phases[i]
        if i == 0:
            baseline += 0.7 * np.sin(angle)
        else:
            baseline += 0.5 * np.cos(angle)

    # add small cumulative bias so it does not repeat perfectly
    step_sigma = 0.005 * strength
    steps = rng.normal(0.0, step_sigma, size=n).astype(np.float32)
    cumulative = np.cumsum(steps)

    baseline += cumulative

    baseline_scale = 0.1 * span  # up to 10% of range
    r += baseline_scale * baseline

    # --- 2) Dead zones and phantom obstacles ---

    # Dead zone = readings pinned near max or min for a while.
    # Phantom obstacle = sudden short ranges in a band.
    event_count = int(3 * strength) + rng.integers(0, 3)
    event_count = max(event_count, 1)

    for _ in range(event_count):
        center = rng.integers(5, max(6, n - 5))
        span_len = rng.integers(10, 60)
        end = min(n, center + span_len)
        if end <= center:
            continue

        window_len = end - center
        base = np.linspace(0.0, 1.0, window_len, dtype=np.float32)
        envelope = base * (1.0 - base) * 4.0

        event_type = rng.choice(["dead_max", "dead_min", "phantom"])
        if event_type == "dead_max":
            # push toward max range (like nothing detected)
            target = r_max + 0.1 * span
            r[center:end] = r[center:end] * (1.0 - envelope) + target * envelope
        elif event_type == "dead_min":
            # push toward very near obstacle
            target = max(r_min - 0.1 * span, 0.0)
            r[center:end] = r[center:end] * (1.0 - envelope) + target * envelope
        else:  # phantom
            # create a band of shorter ranges than usual
            target = r_min + 0.2 * span
            r[center:end] = r[center:end] * (1.0 - envelope) + target * envelope

    # --- 3) Adaptive jitter/noise ---

    noise_sigma = 0.02 * span * strength
    env_phase = rng.uniform(0.0, 2.0 * np.pi)
    env = 0.6 + 0.4 * np.sin(2.0 * np.pi * 0.08 * t_norm + env_phase)
    r += rng.normal(0.0, noise_sigma * env, size=n)

    # Keep within plausible bounds (no negative distances)
    r = np.clip(r, 0.0, r_max + 0.5 * span)

    veiled["range"] = r

    return veiled
