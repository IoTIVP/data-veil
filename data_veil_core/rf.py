"""
RF power veiling – fake interference and RF ghost pockets.

Input format:
    rf: dict with keys:
        "t":      (N,) time
        "power":  (N,) RF power level (e.g. dBm or arbitrary units)

Output:
    new dict with:
        - multi-frequency baseline warping
        - intermittent interference bursts (jamming, ghost signals)
        - adaptive noise whose variance changes over time

Goal:
    Make RF logs from untrusted interfaces unreliable for:
      - localization
      - interference analysis
      - environment reconstruction
    while remaining plausible to a casual or even expert observer.
"""

from typing import Dict
import numpy as np
from .random_control import get_rng


def veil_rf(rf: Dict[str, np.ndarray], strength: float = 1.0) -> Dict[str, np.ndarray]:
    """
    Veil RF power time series.

    Args:
        rf: dict with keys "t", "power"
        strength: distortion intensity (0.5 .. 2.0 typical)

    Returns:
        new dict with same keys.
    """
    required = {"t", "power"}
    missing = required - set(rf.keys())
    if missing:
        raise ValueError(f"veil_rf missing keys: {missing}")

    veiled = {k: np.asarray(v, dtype=np.float32).copy() for k, v in rf.items()}
    t = veiled["t"]
    power = veiled["power"]
    n = t.shape[0]

    if n == 0:
        return veiled

    rng = get_rng()

    p_min = float(power.min())
    p_max = float(power.max())
    span = max(p_max - p_min, 1e-3)
    std = float(power.std())
    std = max(std, 1e-3)

    # Normalize time 0..1
    t_norm = (t - t[0]) / max(t[-1] - t[0], 1e-6)

    # --- 1) Multi-frequency baseline warping ---

    freqs = np.array([0.15, 0.4, 0.8], dtype=np.float32) * strength
    phases = rng.uniform(0.0, 2.0 * np.pi, size=freqs.shape[0])

    baseline_warp = np.zeros_like(t_norm, dtype=np.float32)
    for i, f in enumerate(freqs):
        angle = 2.0 * np.pi * f * t_norm + phases[i]
        if i == 0:
            baseline_warp += 0.7 * np.sin(angle)
        elif i == 1:
            baseline_warp += 0.5 * np.cos(angle)
        else:
            baseline_warp += 0.4 * np.sin(angle + 0.6) * np.cos(0.4 * angle)

    # Add slow cumulative drift so pattern cannot be modeled as pure sinusoids
    step_sigma = 0.01 * strength
    steps = rng.normal(0.0, step_sigma, size=n).astype(np.float32)
    cumulative = np.cumsum(steps)

    baseline_warp += cumulative

    # Scale relative to span
    warp_scale = 0.2 * span  # up to 20% of RF range
    power += warp_scale * baseline_warp

    # --- 2) Interference bursts / RF ghost pockets ---

    burst_count = int(3 * strength) + rng.integers(0, 4)
    burst_count = max(burst_count, 1)

    for _ in range(burst_count):
        center = rng.integers(5, max(6, n - 5))
        span_len = rng.integers(15, 80)
        end = min(n, center + span_len)
        if end <= center:
            continue

        window_len = end - center
        base = np.linspace(0.0, 1.0, window_len, dtype=np.float32)

        # Different interference patterns
        shape_type = rng.choice(["spike_train", "jam_block", "notch"])
        if shape_type == "spike_train":
            # rapid pulsing, like intermittent interference
            spikes = (rng.random(size=window_len) > 0.6).astype(np.float32)
            # smooth edges
            envelope = base * (1.0 - base) * 4.0
            shape = spikes * envelope
        elif shape_type == "jam_block":
            # full-on jamming plateau with soft edges
            shape = base * (1.0 - base) * 4.0
        else:  # "notch" – signal drop / shadow
            shape = -base * (1.0 - base) * 4.0

        # amplitude relative to std and strength
        amp = (1.0 + 1.5 * rng.random()) * std * strength
        power[center:end] += amp * shape

    # --- 3) Adaptive noise (time-varying variance) ---

    noise_sigma = 0.05 * span * strength
    # envelope modulates noise intensity, creating "breathing" RF noise
    env_phase = rng.uniform(0.0, 2.0 * np.pi)
    env = 0.4 + 0.6 * np.abs(np.sin(2.0 * np.pi * 0.07 * t_norm + env_phase))
    power += rng.normal(0.0, noise_sigma * env, size=n)

    veiled["power"] = power

    return veiled
