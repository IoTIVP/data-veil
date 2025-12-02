"""
Global RNG control for Data Veil.

If DATA_VEIL_SEED is set (env var), all veiling functions will share
a single deterministic RNG instance. Otherwise, a random seed is used.
"""

import os
import numpy as np

_SEED_ENV = os.getenv("DATA_VEIL_SEED")
_SEED = None

if _SEED_ENV is not None:
    try:
        _SEED = int(_SEED_ENV)
    except ValueError:
        _SEED = None

if _SEED is not None:
    _RNG = np.random.default_rng(_SEED)
else:
    _RNG = np.random.default_rng()


def get_rng() -> np.random.Generator:
    return _RNG
