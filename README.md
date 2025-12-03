# 📡 DATA VEIL – Synthetic Sensor Deception Engine

*A research-friendly toolkit for generating trusted vs veiled sensor streams.*

---

## 🧠 Overview

**Data Veil** is a multi-sensor deception engine that simulates how autonomous robots, drones, and IoT devices can present:

- **Trusted internal data** for navigation, autonomy, and safety  
- **Veiled external data** for logs, cloud exports, or attacker-visible channels  

The result is a synthetic **dual-reality boundary** where the system sees truth and outsiders see distortion.

---

## 🚀 Quick Start

```bash
git clone https://github.com/IoTIVP/data-veil
cd data-veil
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run any demo:

```bash
python run_lidar_demo.py
```

More demos available in the repo (depth, radar, IMU, thermal, RF, stereo, ghosting, etc).

---

## 🛰 Supported Sensors & Synthetic Profiles

Data Veil currently supports synthetic veiling for:

- Depth maps  
- LiDAR ranges / point clouds  
- Thermal / IR  
- RF field intensities  
- Radar range–Doppler  
- RGB camera  
- Stereo vision  
- Ultrasonic rings  
- IMU (gyro + acceleration)  
- Temporal “ghosting” sequences  
- Multi-sensor dashboards  

Each demo produces:

- **trusted_*** (internal system view)  
- **veiled_*** (external attacker view)  
- **trusted_vs_hacker.png** (side-by-side panel)  

---

## 🎯 Threat Model & Scope

Data Veil is a **simulation-only** synthetic deception engine.

It is designed to distinguish between:

- **Trusted internal perception** (robot uses this)
- **Veiled external attacker-facing perception** (attackers, logs, cloud exports)

### Attacker Model

We assume attackers may access:

- logs  
- cloud telemetry  
- debug/mirror feeds  
- exported recordings  

Data Veil ensures **attackers only see distorted sensor data**, not the true internal environment.

### What Data Veil is NOT

- Not a replacement for authentication  
- Not cryptographic security  
- Not firmware hardening  
- Not to be deployed blindly in safety-critical production  

It is a **research tool**, not a compliance-grade security layer.

---

## 🐍 Python API (data_veil_core)

Data Veil includes a modular high-distortion sensor veiling core:

```python
from data_veil_core import (
    veil_depth,
    veil_lidar,
    veil_radar,
    veil_thermal,
    veil_imu,
)
```

Example:

```python
import numpy as np
from data_veil_core import veil_depth

depth = np.random.rand(64, 96).astype(np.float32)
veiled = veil_depth(depth, strength=1.3)

print("trusted:", depth.min(), depth.max())
print("veiled:", veiled.min(), veiled.max())
```

---

## 🔧 Architecture

```
Sensors → Trusted Pipeline → Autonomy
              ↓
          Data Veil
              ↓
    External / Untrusted Consumers
```

Trusted stays internal.  
Veiled leaves the system.

---

## 🟣 Realtime Viewer

For a live, animated view of trusted vs veiled depth:

```bash
python examples/realtime_depth_demo.py
```

Features:

- Trusted vs veiled split-screen  
- Synthetic depth evolving over time  
- Live profile switching:  
  - **1 = light**  
  - **2 = privacy**  
  - **3 = ghost**  
  - **4 = chaos**  

Profiles are loaded from `config/profiles.yaml`.

---

## 🟠 Multi-Sensor + Profiles Demo

To see how different profiles affect multiple sensors in one shot:

```bash
python examples/multi_sensor_profiles_demo.py
```

This script:

- Generates synthetic data for:  
  - depth  
  - lidar  
  - radar  
  - thermal  
  - IMU (t, gx, gy, gz, ax, ay, az)  
- Applies profiles (`light`, `privacy`, `ghost`, `chaos`)  
- Prints summary statistics:  
  - trusted stats  
  - veiled stats  
  - mean and max absolute difference  

---

## 📦 Coming Soon (v1.0 Release)

- pip package (`pip install data-veil`)  
- Core API expansion  
- Integration examples for robotics / cloud pipelines  
- Untrusted-access filter templates  

---

## 📜 License

MIT License

---

## 🤝 Contributing

Pull requests welcome from:

- robotics engineers  
- cybersecurity analysts  
- red-team researchers  
- OSINT analysts  
- simulation experts  

---

## 🎉 Thank You

Explore, remix, collaborate, and build on Data Veil.  
Designed for creativity, research, and future experimentation.
