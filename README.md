# 📡 **DATA VEIL – Synthetic Sensor Deception Engine**

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

## 🛰 Supported Sensors & Demos

(See full details in the repository.)

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

Data Veil includes a modular, Sci-Fi / High-distortion mode sensor veiling core:

```python
from data_veil_core import (
    veil_depth,
    veil_lidar,
    veil_radar,
    veil_thermal,
    veil_imu,
)
```

### Example

```python
import numpy as np
from data_veil_core import veil_depth

depth = np.random.rand(64, 96).astype(np.float32)
veiled = veil_depth(depth, strength=1.3)

print("trusted:", depth.min(), depth.max())
print("veiled:", veiled.min(), veiled.max())
```

### API Functions

| Function       | Input Type                    | Output                                  |
|----------------|-------------------------------|------------------------------------------|
| `veil_depth`   | 2D depth (H×W)                | warped depth, voids, fake surfaces       |
| `veil_lidar`   | 1D ranges or Nx3 points       | ghost obstacles, erased sectors          |
| `veil_radar`   | 2D range–Doppler              | phantom targets, ripples, structured noise |
| `veil_thermal` | 2D thermal image              | smeared patches, heat/cold spoofing      |
| `veil_imu`     | dict of IMU arrays            | drift, jitter, impact hallucinations     |

See `examples/integration_example.py` for a full hands-on demonstration.

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

## 📦 Coming Soon (v1.0 Release)

- pip package (`pip install data-veil`)  
- Core API module expansion  
- Integration examples for robotics / cloud pipelines  
- Untrusted-access filter templates (copy-paste ready)  

---

## 📜 License

MIT License (added for open-source use)

---

## 🤝 Contributing

Pull requests are welcome from:

- robotics engineers  
- cybersecurity analysts  
- red-team researchers  
- OSINT analysts  
- simulation experts  

---

## 🎉 Thank You

Explore, remix, collaborate, and build on Data Veil.  
The project is open-source and designed for creativity, research, and future experimentation.
