"""
Simple plugin registry for Data Veil.

Allows registering custom veiling functions by sensor name, e.g.:

    from data_veil_core.plugins import register_sensor, get_veil

    def veil_custom_sensor(data, strength=1.0):
        ...

    register_sensor("custom_sensor", veil_custom_sensor)

Then, elsewhere:

    fn = get_veil("custom_sensor")
    veiled = fn(data, strength=0.8)
"""

from typing import Callable, Dict, List, Optional, Any

# Registry maps sensor name -> veiling function
# Expected callable signature: fn(data, strength: float = 1.0) -> Any
_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register_sensor(name: str, fn: Callable[..., Any]) -> None:
    """
    Register a custom veiling function under a given sensor name.

    Args:
        name: sensor identifier, e.g. "depth", "lidar_front", "thermal_cam".
        fn:   callable taking (data, strength=1.0) and returning veiled data.
    """
    key = str(name).strip()
    if not key:
        raise ValueError("Sensor name must be a non-empty string.")
    if not callable(fn):
        raise ValueError("fn must be callable.")

    _REGISTRY[key] = fn


def get_veil(name: str) -> Optional[Callable[..., Any]]:
    """
    Look up a veiling function by sensor name.

    Args:
        name: sensor identifier string.

    Returns:
        callable or None if not found.
    """
    return _REGISTRY.get(str(name).strip())


def list_sensors() -> List[str]:
    """
    List all registered sensor names.
    """
    return sorted(_REGISTRY.keys())
