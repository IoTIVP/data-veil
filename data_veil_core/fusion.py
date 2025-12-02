"""
Fusion-level veiling for aligned 1D time-series sensors.

This module provides a simple but powerful "fusion veil" that applies
correlated distortions across multiple sensor streams at once.

Input:
    sensors: dict[str, np.ndarray] where each value is a 1D array of shape (N,)

Assumptions:
    - All series represent the same timeline (aligned index 0..N-1).
    - Lengths may differ slightly; we will truncate to the shortest length.

Output:
    new dict[str, np.ndarray] with veiled series.

Design:
    - Shared latent processes (random walk, sinusoid, noise) generate
      time-varying factors.
    - Each sensor gets its own mixture of these latents, scaled by its own
      statistics (std, span) and the global "strength".
    - The result is:
        * Cross-sensor correlations that make the veil feel "environmental"
        * Very hard to invert or remove from logs
"""

from typing import Dict
import numpy as np
from .random_control import get_rng


def veil_fusion_timeseries(
    sensors: Dict[str, np.ndarray],
    strength: float = 1.0,
) -> Dict[str, np.ndarray]:
    """
    Apply a correlated fusion veil to aligned 1D time-series sensors.

    Args:
        sensors: mapping sensor_name -> 1D numpy array (length N)
        strength: distortion intensity (0.5 .. 2.0 typical)

    Returns:
        new mapping sensor_name -> veiled 1D numpy array (length N_shortest)
    """
    if not sensors:
        raise ValueError("veil_fusion_timeseries: sensors dict is empty.")

    # Convert to float32 arrays and find common length
    arrays = {}
    lengths = []
    for name, arr in sensors.items():
        a = np.asarray(arr, dtype=np.float32)
        if a.ndim != 1:
            raise ValueError(f"veil_fusion_timeseries: sensor '{name}' is not 1D.")
        arrays[name] = a
        lengths.append(a.shape[0])

    n = min(lengths)
    if n == 0:
        return {name: arr.copy()[:0] for name, arr in arrays.items()}

    # Truncate all to the shortest length
    for name in arrays:
        arrays[name] = arrays[name][:n]

    rng = get_rng()

    # Build shared latent processes over time index 0..n-1
    t = np.linspace(0.0, 1.0, n, dtype=np.float32)

    # Latent 1: random walk (slow drift)
    step_sigma = 0.05 * strength
    steps = rng.normal(0.0, step_sigma, size=n).astype(np.float32)
    latent1 = np.cumsum(steps)

    # Latent 2: multi-frequency sinusoid
    freq1 = 0.3 * strength
    freq2 = 0.8 * strength
    phase1 = rng.uniform(0.0, 2.0 * np.pi)
    phase2 = rng.uniform(0.0, 2.0 * np.pi)
    latent2 = (
        0.7 * np.sin(2.0 * np.pi * freq1 * t + phase1)
        + 0.5 * np.cos(2.0 * np.pi * freq2 * t + phase2)
    )

    # Latent 3: band-limited noise envelope
    noise_raw = rng.normal(0.0, 1.0, size=n).astype(np.float32)
    # Smooth the noise a bit with a simple moving average
    kernel_size = 5
    kernel = np.ones(kernel_size, dtype=np.float32) / float(kernel_size)
    noise_smoothed = np.convolve(noise_raw, kernel, mode="same")
    latent3 = noise_smoothed

    veiled: Dict[str, np.ndarray] = {}

    for name, base in arrays.items():
        base = base.copy()
        span = float(base.max() - base.min())
        std = float(base.std())
        span = max(span, 1e-3)
        std = max(std, 1e-3)

        # Each sensor gets its own mixture weights
        w = rng.normal(0.0, 1.0, size=3).astype(np.float32)
        # Normalize weights so they are not huge
        w /= max(np.linalg.norm(w), 1e-6)

        # Combined latent for this sensor
        latent = w[0] * latent1 + w[1] * latent2 + w[2] * latent3

        # Scale relative to sensor stats and global strength
        # Use a mix of span and std so flat signals still get some distortion.
        scale = (0.2 * span + 0.8 * std) * strength

        distorted = base + scale * latent

        veiled[name] = distorted

    return veiled
