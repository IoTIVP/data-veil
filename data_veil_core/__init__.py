"""
data_veil_core

Sci-Fi / DARPA-mode veiling functions for multi-sensor deception.
"""

from .depth import veil_depth
from .lidar import veil_lidar
from .thermal import veil_thermal
from .radar import veil_radar
from .imu import veil_imu
from .magnetometer import veil_magnetometer
from .barometer import veil_barometer
from .rf import veil_rf
from .plugins import register_sensor, get_veil, list_sensors

__all__ = [
    "veil_depth",
    "veil_lidar",
    "veil_thermal",
    "veil_radar",
    "veil_imu",
    "veil_magnetometer",
    "veil_barometer",
    "veil_rf",
    "register_sensor",
    "get_veil",
    "list_sensors",
]
