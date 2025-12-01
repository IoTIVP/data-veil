"""
Barometer veiling – fake altitude / pressure anomalies.

Input format:
    baro: dict with keys:
        "t":        (N,) time
        "pressure": (N,) pressure values (e.g., hPa or Pa)

Output:
    new dict with:
        - slow drift (simulated weather or sensor bias)
        - transient anomalies (fake altitude changes, pressure spikes)
        - random noise

Goal:
    Keep series plausible for casual inspection, but unreliable
    for external altitude estimation.
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

    # --- 1) Slow drift over time (weather or sensor bias) ---

    t_norm = (t - t[0]) / max(t[-1] - t[0], 1e-6)  # 0..1
    # Simple smooth curve: small up-down shift
    drift = (t_norm - 0.5) * (2.0 * strength)  # -strength..+strength
    # Scale drift relative to dynamic range of pressure
    p_min = float(p.min())
    p_max = float(p.max())
    span = max(p_max - p_min, 1e-3)

    drift_scale = 0.01 * span  # about 1% of span
    veiled["pressure"] += drift * drift_scale

    # --- 2) Transient anomalies (fake altitude changes or spikes) ---

    anomaly_count = int(3 * strength)
    for _ in range(anomaly_count):
        center = rng.integers(5, max(6, n - 5))
        span_len = rng.integers(10, 40)
        end = min(n, center + span_len)

        # Decide if we simulate a sudden climb or descent
        direction = rng.choice([-1.0, 1.0])
        amp = (0.02 + 0.03 * rng.random()) * span * strength  # 2-5% of span

        window_len = end - center
        window = np.linspace(0.0, 1.0, window_len, dtype=np.float32)
        shape = window * (1.0 - window) * 4.0  # peak in middle

        veiled["pressure"][center:end] += direction * amp * shape

    # --- 3) Noise on top (sensor jitter / turbulence) ---

    noise_sigma = 0.002 * span * strength
    veiled["pressure"] += rng.normal(0.0, noise_sigma, size=n)

    return veiled
