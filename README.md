# 📡 **DATA VEIL – Synthetic Sensor Distortion & Privacy Layer**

*A research toolkit for generating **trusted vs veiled sensor streams** in robotics, IoT, and simulation environments.*

---

## 🧠 Overview

Modern robots, drones, and IoT systems often expose sensor data to cloud services, logs, integrations, and external interfaces.  
**Data Veil** introduces a synthetic privacy boundary:

- **Trusted internal data** → used for perception, autonomy, safety  
- **Veiled external data** → exported to logs, cloud endpoints, or any non-privileged consumer  

This creates a **dual-reality layer** that protects internal perception while still providing usable (but intentionally distorted) external streams.

Think of it as **sensor redaction for machines**—the system sees truth, while external observers only see synthetic noise, distortion, or altered geometry.

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

More demos available in the `examples/` directory: depth, radar, IMU, thermal, RF, stereo, ghosting, etc.

---

## 🛰 Supported Sensors & Synthetic Profiles

**Data Veil currently simulates distortion for:**

- Depth maps  
- LiDAR (ranges & point clouds)  
- Thermal / IR frames  
- RF intensity fields  
- Radar (range–Doppler maps)  
- RGB camera  
- Stereo disparity  
- Ultrasonic rings  
- IMU (gyro + accel)  
- Temporal ghosting sequences  
- Multi-sensor dashboards  

Each demo produces:

- `trusted_*` — internal system truth  
- `veiled_*` — external/non-privileged output  
- `*_trusted_vs_veiled.png` — side-by-side comparison  

---

## 🎯 Threat Model & Scope

Data Veil is a **research-focused simulation tool**, intended for:

- Privacy-preserving telemetry  
- Synthetic data generation  
- Robotics robustness studies  
- Simulation redactions  
- Adversarial testing  
- Multi-sensor perception experiments  

### **Trusted vs Untrusted Paths**

**Internal (trusted):**

- High-accuracy sensor data  
- Used for autonomy & decision-making  

**External (untrusted):**

- Logs  
- Cloud exports  
- Monitoring dashboards  
- Third-party API consumers  

External consumers only receive **veil-modified data**, not the raw sensor truth.

### Data Veil is *not*:

- A replacement for cybersecurity controls  
- A cryptographic integrity system  
- A safety-critical isolation boundary  
- A hardware protection mechanism  

It’s a **synthetic signal transformation toolkit**, not a security product.

---

## 🐍 Python API (data_veil_core)

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
veiled = veil_depth(depth, strength=1.2)

print("trusted:", depth.min(), depth.max())
print("veiled:", veiled.min(), veiled.max())
```

### Function Overview

| Function         | Input                          | Output Description                           |
|------------------|--------------------------------|-----------------------------------------------|
| `veil_depth`     | 2D depth map                   | warped surfaces, voids, geometric shifts      |
| `veil_lidar`     | 1D ranges or Nx3 points        | ghost returns, erased slices, synthetic arcs  |
| `veil_radar`     | 2D range–Doppler               | ripples, phantom targets, structured noise    |
| `veil_thermal`   | 2D thermal frame               | heat smears, synthetic outliers               |
| `veil_imu`       | accel/gyro arrays              | drift, jitter, controlled perturbations       |

See `examples/integration_example.py` for a full multi-sensor demo.

---

## 🔧 Architecture

```txt
   ┌──────────────┐
   │  Sensors      │
   └──────┬────────┘
          │
     (Trusted Path)
          │
   ┌──────────────┐
   │  Autonomy     │
   │  Navigation   │
   └──────┬────────┘
          │
     (Veil Layer)
          │
   ┌──────────────┐
   │ External /    │
   │ Untrusted     │
   │ Consumers     │
   └──────────────┘
```

---

## 📦 Roadmap Toward v1.0 Release

- ✔ pip-installable package (`pip install data-veil`)  
- ✔ Unified `data_veil_core` module  
- ✔ Plugin registry for new sensor types  
- ✔ Consistent distortion modes  
- ✔ Policy-based veiling profiles  
- — Real-time demos and GIF exporters  
- — Cloud integration example (MQTT / ROS2 / REST)  
- — Sensor fusion example (multiple modalities together)  
- — Advanced distortion modes (high-intensity / structured)  

---

## 🧩 Use Cases

- Robotics simulation  
- Privacy-preserving logs & telemetry  
- Synthetic dataset generation  
- ML robustness testing  
- Sensor-fault simulation  
- Educational tools for perception systems  
- Redaction of sensitive spatial data  

---

## 📜 License

MIT License  
Fully open source for research and experimentation.

---

## 🤝 Contributing

Contributions are welcome from:

- Robotics engineers  
- ML / CV researchers  
- IoT developers  
- Simulation specialists  
- Students & hobbyists  

---

## 🎉 Thanks for Exploring Data Veil

This toolkit aims to make sensor research more expressive, safer to share, and more fun to experiment with.  
Build something cool on top of it.
