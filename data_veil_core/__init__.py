"""
data_veil_core

Sci-Fi / DARPA-mode veiling functions for multi-sensor deception.

These functions operate on NumPy arrays or simple Python structures and
can be used directly in simulations, robotics stacks, or security tests.
"""

from .depth import veil_depth
from .lidar import veil_lidar
from .thermal import veil_thermal
from .radar import veil_radar
from .imu import veil_imu

__all__ = [
    "veil_depth",
    "veil_lidar",
    "veil_thermal",
    "veil_radar",
    "veil_imu",
]
