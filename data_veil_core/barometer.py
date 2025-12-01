"""
Barometer veiling – fake altitude / pressure anomalies (hardened).

Input format:
    baro: dict with keys:
        "t":        (N,) time
        "pressure": (N,) pressure values (e.g., hPa)

Output:
    new dict with:
        - multi-frequency drift (weather + sensor bias)
        - transient altitude illusions and pressure spikes
        - adaptive noise relative to signal span

Goal:
    Make altitude/pressure reconstruction from external logs unreliable,
    while keeping the series physically plausible.
"""

from typing import Dict
import numpy as np
from .random_control import get_rng


def veil_barometer(baro: Dict[str, np.ndarray], strength: float = 1.0) -> Dict[str, np.ndarray]:
    """
    Veil barometric pressure data with drift and anomalies.

    Args:
        baro: dict with keys "t", "pressure"
        strength: distortion intensity (0.5 .. 2.0 typical)

    Returns:
        new dict with same keys.
    """
    required = {"t", "pressure"}
    missing = required - set(baro.keys())
    if missing:
        raise ValueError(f"veil_barometer missing keys: {missing}")

    veiled = {k: np.asarray(v, dtype=np.float32).copy() for k, v in baro.items()}
    t = veiled["t"]
    p = veiled["pressure"]
    n = t.shape[0]

    if n == 0:
        return veiled

    rng = get_rng()

    p_min = float(p.min())
    p_max = float(p.max())
    span = max(p_max - p_min, 1e-3)
    std = float(p.std())
    std = max(std, 1e-3)

    # Normalize time 0..1
    t_norm = (t - t[0]) / max(t[-1] - t[0], 1e-6)

    # --- 1) Multi-frequency drift ---

    # Combine several low-frequency sin/cos curves with random phases.
    freqs = np.array([0.1, 0.25, 0.45], dtype=np.float32) * strength
    phases = rng.uniform(0.0, 2.0 * np.pi, size=freqs.shape[0])

    drift = np.zeros_like(t_norm, dtype=np.float32)

    for i, f in enumerate(freqs):
        angle = 2.0 * np.pi * f * t_norm + phases[i]
        # Slightly different contributions: sin, cos, skewed
        if i == 0:
            drift += 0.6 * np.sin(angle)
        elif i == 1:
            drift += 0.4 * np.cos(angle)
        else:
            drift += 0.3 * np.sin(angle + 0.7) * np.cos(0.5 * angle)

    # History-dependent cumulative drift
    step_sigma = 0.002 * strength
    steps = rng.normal(0.0, step_sigma, size=n).astype(np.float32)
    cumulative = np.cumsum(steps)

    drift += cumulative

    # Scale drift relative to span
    drift_scale = 0.03 * span  # about 3% of range at full strength
    p += drift_scale * drift

    # --- 2) Transient anomalies (altitude illusions, spikes) ---

    anomaly_count = int(3 * strength) + rng.integers(0, 3)
    anomaly_count = max(anomaly_count, 1)

    for _ in range(anomaly_count):
        center = rng.integers(5, max(6, n - 5))
        span_len = rng.integers(15, 60)
        end = min(n, center + span_len)
        if end <= center:
            continue

        window_len = end - center
        base = np.linspace(0.0, 1.0, window_len, dtype=np.float32)

        shape_type = rng.choice(["bump", "dip", "tilted"])
        if shape_type == "bump":
            shape = base * (1.0 - base) * 4.0
        elif shape_type == "dip":
            shape = -base * (1.0 - base) * 4.0
        else:  # tilted
            shape = (base - 0.5) * 2.0

        # Altitude illusions: amplitude scaled to std and strength
        amp = (0.5 + 0.8 * rng.random()) * std * strength
        p[center:end] += amp * shape

    # --- 3) Adaptive noise ---

    noise_sigma = 0.01 * span * strength
    # modulate noise by a slow envelope so variance is not constant
    env = 0.5 + 0.5 * np.sin(2.0 * np.pi * 0.05 * t_norm + rng.uniform(0.0, 2.0 * np.pi))
    p += rng.normal(0.0, noise_sigma * env, size=n)

    veiled["pressure"] = p

    return veiled
