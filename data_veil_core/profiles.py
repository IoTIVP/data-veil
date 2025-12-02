"""
Veil profiles for Data Veil.

This module provides named profiles that map to numeric strengths
for different sensor types. It supports:

1) Built-in defaults (hard-coded in Python)
2) Optional overrides via config/profiles.yaml

YAML format example:

profiles:
  privacy:
    base: 1.0
    sensors:
      default: 1.0
      lidar: 1.1
      rf: 1.1
"""

from typing import Dict
import os

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # Graceful fallback to built-in profiles if missing.


# --- Built-in base profile multipliers (generic) ---

_BASE_PROFILES = {
    "light": 0.5,
    "privacy": 1.0,
    "ghost": 1.5,
    "chaos": 2.0,
}

# --- Optional built-in per-sensor tweaks (multipliers on top of base) ---

_SENSOR_PROFILE_TWEAKS: Dict[str, Dict[str, float]] = {
    # LiDAR can handle slightly stronger distortions visually.
    "lidar": {
        "ghost": 1.2,
        "chaos": 1.3,
    },
    # RF can also tolerate more chaos.
    "rf": {
        "ghost": 1.1,
        "chaos": 1.3,
    },
    # Ultrasonic may be more sensitive.
    "ultrasonic": {
        "chaos": 0.9,
    },
}

# --- YAML-backed profiles cache ---

_YAML_PROFILES: Dict[str, Dict] | None = None


def _profiles_yaml_path() -> str:
    """
    Resolve the path to config/profiles.yaml relative to project root.
    """
    here = os.path.dirname(os.path.abspath(__file__))  # .../data_veil_core
    root = os.path.dirname(here)  # project root
    return os.path.join(root, "config", "profiles.yaml")


def _load_profiles_from_yaml() -> Dict[str, Dict]:
    """
    Load profiles from config/profiles.yaml if available.

    Returns:
        dict mapping profile_name -> profile_config
        (or {} if file missing / yaml unavailable / parse error)
    """
    global _YAML_PROFILES

    if _YAML_PROFILES is not None:
        return _YAML_PROFILES

    if yaml is None:
        _YAML_PROFILES = {}
        return _YAML_PROFILES

    path = _profiles_yaml_path()
    if not os.path.exists(path):
        _YAML_PROFILES = {}
        return _YAML_PROFILES

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        _YAML_PROFILES = {}
        return _YAML_PROFILES

    profiles = data.get("profiles", {})
    if not isinstance(profiles, dict):
        profiles = {}

    _YAML_PROFILES = profiles
    return _YAML_PROFILES


def list_profiles():
    """
    Return a sorted list of supported profile names (union of built-in and YAML).
    """
    built_in = set(_BASE_PROFILES.keys())
    yaml_profiles = set(_load_profiles_from_yaml().keys())
    all_profiles = built_in | yaml_profiles
    return sorted(all_profiles)


def get_profile_strength(profile: str, sensor_name: str) -> float:
    """
    Compute a numeric strength for a given profile and sensor.

    Order of precedence:
      1) config/profiles.yaml (if exists and defines the profile)
      2) Built-in base profiles + built-in tweaks

    Args:
        profile: profile name (e.g. "light", "privacy", "ghost", "chaos")
        sensor_name: sensor type (e.g. "lidar", "rf", "ultrasonic", "depth")

    Returns:
        float strength suitable for passing to veil_* functions.

    Raises:
        KeyError if profile is unknown in both YAML and built-ins.
    """
    p_raw = profile.strip()
    s_raw = sensor_name.strip()

    p = p_raw.lower()
    s = s_raw.lower()

    yaml_profiles = _load_profiles_from_yaml()

    # 1) Check YAML overrides
    if p in yaml_profiles:
        cfg = yaml_profiles[p] or {}
        base = float(cfg.get("base", _BASE_PROFILES.get(p, 1.0)))
        sensors_cfg = cfg.get("sensors", {}) or {}
        # sensor-specific factor, or fall back to "default", or 1.0
        factor = float(
            sensors_cfg.get(s, sensors_cfg.get("default", 1.0))
        )
        return base * factor

    # 2) Fall back to built-in
    if p not in _BASE_PROFILES:
        raise KeyError(
            f"Unknown profile '{profile}'. "
            f"Valid built-ins: {list(_BASE_PROFILES.keys())} "
            f"and any in config/profiles.yaml."
        )

    base = _BASE_PROFILES[p]
    tweak_table = _SENSOR_PROFILE_TWEAKS.get(s)
    if tweak_table is not None:
        factor = tweak_table.get(p, 1.0)
    else:
        factor = 1.0

    return base * factor
