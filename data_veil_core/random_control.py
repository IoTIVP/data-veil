"""
Randomness Control Utilities for Data Veil

Provides consistent seeding so trusted and veiled outputs
can be reproduced exactly (if desired).

Exposed functions:
    - set_seed(seed_value=None): set global seed
    - get_rng(): get a shared numpy Generator
    - reseed(): reapply DATA_VEIL_SEED (or default)
"""

import os
import random
from typing import Optional

import numpy as np

# Module-level RNG instance
_RNG: Optional[np.random.Generator] = None


def _init_rng(seed_value: int) -> np.random.Generator:
    """
    Initialize and return a new numpy Generator with the given seed.
    """
    global _RNG
    _RNG = np.random.default_rng(seed_value)
    return _RNG


def set_seed(seed_value: int | None = None) -> int:
    """
    Set the global seed for numpy and Python's random module, and reset
    the shared RNG used by Data Veil.

    Args:
        seed_value (int or None):
            If None, the function will look for the
            DATA_VEIL_SEED environment variable. If that is also
            missing, a default seed of 42 is used.

    Returns:
        The final seed value that was applied.
    """
    if seed_value is None:
        env_seed = os.getenv("DATA_VEIL_SEED")
        seed_value = int(env_seed) if env_seed is not None else 42

    random.seed(seed_value)
    np.random.seed(seed_value)
    _init_rng(seed_value)

    return seed_value


def get_rng() -> np.random.Generator:
    """
    Get the shared numpy Generator used by Data Veil.

    If it has not been initialized yet, it will call set_seed(None),
    which uses DATA_VEIL_SEED or a default value.
    """
    global _RNG
    if _RNG is None:
        set_seed(None)
    return _RNG  # type: ignore[return-value]


def reseed():
    """
    Force-reset random states using the DATA_VEIL_SEED environment variable.

    Useful if a script modifies RNG states and needs them restored
    to a known baseline.
    """
    set_seed(None)
