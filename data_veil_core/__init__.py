"""
data_veil_core

Sensor veiling functions for multi-sensor deception / obfuscation.
This is the main public API surface for the core engine.
"""

from .depth import veil_depth
from .lidar import veil_lidar
from .thermal import veil_thermal
from .radar import veil_radar
from .imu import veil_imu
from .magnetometer import veil_magnetometer
from .barometer import veil_barometer
from .rf import veil_rf
from .ultrasonic import veil_ultrasonic
from .fusion import veil_fusion_timeseries
from .plugins import register_sensor, get_veil, list_sensors
from .profiles import get_profile_strength, list_profiles

__all__ = [
    "veil_depth",
    "veil_lidar",
    "veil_thermal",
    "veil_radar",
    "veil_imu",
    "veil_magnetometer",
    "veil_barometer",
    "veil_rf",
    "veil_ultrasonic",
    "veil_fusion_timeseries",
    "register_sensor",
    "get_veil",
    "list_sensors",
    "get_profile_strength",
    "list_profiles",
]
