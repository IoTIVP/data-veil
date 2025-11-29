\# 🧠 DATA VEIL v0.1 – Depth-Field Sensor Deception Engine


![Trusted vs veiled depth field](https://github.com/IoTIVP/data-veil/blob/main/examples/trusted_vs_hacker.png?raw=true)


> \*“If an attacker taps your sensor stream, what if the environment could lie?”\*



\*\*Data Veil\*\* is a small, self-contained \*\*sensor deception simulator\*\*.



It treats a \*\*sensor flow\*\* as a numeric \*\*depth field\*\* (a 2D matrix of distances), then produces a \*\*veiled version\*\* of that field that represents what an attacker or untrusted client would see at an exposure boundary (API, gateway, cloud telemetry, etc.).



\- \*\*Trusted system\*\* → sees the \*\*real depth field\*\*  

\- \*\*Attacker / untrusted client\*\* → sees the \*\*veiled depth field\*\*



Images are only used to \*visualize\* those numeric arrays.



---



\## 🔍 What this demo does



This v0.1 demo focuses on a single sensor type:



\- \*\*Depth field\*\* – a synthetic 2D grid where each cell is a distance value between `0.0` (near) and `1.0` (far).



The pipeline:



1\. \*\*Generate a trusted depth field\*\*

&nbsp;  - Simulates a simple environment: sloped floor/wall + two closer “objects”.

2\. \*\*Apply Data Veil\*\*

&nbsp;  - Warps the depth field (non-linear spatial distortion)

&nbsp;  - Carves holes / noisy voids (missing returns, blind spots, interference)

3\. \*\*Visualize\*\*

&nbsp;  - Converts both trusted and veiled depth fields into grayscale images

&nbsp;  - Outputs a \*\*side-by-side\*\*: “Trusted depth field” vs “Veiled depth field”



The core logic is \*\*numeric\*\* (`numpy` arrays).  

PNG images are just for humans.



---



\## 🧱 Files



\- `run\_demo.py`  

&nbsp; - Contains:

&nbsp;   - Synthetic depth-field generator (`generate\_depth\_field`)

&nbsp;   - Data Veil transformation (`apply\_data\_veil`)

&nbsp;   - Visualization helpers (`depth\_to\_image`, `make\_side\_by\_side`)

&nbsp;   - `demo()` entry point



\- `requirements.txt`  

&nbsp; - Python dependencies:

&nbsp;   - `numpy` – array math

&nbsp;   - `Pillow` – image export for visualization



\- `examples/` (created by the demo)

&nbsp; - `trusted\_depth.png` – what the trusted system sees

&nbsp; - `veiled\_depth.png` – what an attacker sees at the exposure boundary

&nbsp; - `trusted\_vs\_hacker.png` – side-by-side comparison



---



\## 🚀 Quickstart



\### 1. Create and activate a virtual environment



```bash

python -m venv .venv

\# Windows PowerShell:

.venv\\Scripts\\activate



---

## 🌐 LiDAR Sweep Demo (v0.1 extension)

In addition to the depth-field demo, this repo also includes a **LiDAR sweep** sensor deception demo in `run_lidar_demo.py`.

### What it simulates

- A 360° LiDAR scan represented as a 1D array of ranges (`0.0 .. 1.0`)
- A base environment with a few real obstacles
- A veiled scan with:
  - warped ranges,
  - void sectors (no returns / max range),
  - and ghost obstacles (fake close returns)

### How to run it

From the project root, with your virtual environment activated:

```bash
python run_lidar_demo.py


---

## 🛣 Roadmap – Where Data Veil Could Go Next

This v0.1 release focuses on **depth fields** and a **single 360° LiDAR sweep**.  
Future versions could explore:

### 1. More Sensor Types
- **Thermal / IR maps** – deceive heat-based perception.
- **RF / signal-strength grids** – distort wireless field awareness.
- **IMU streams (accelerometer/gyro)** – simulate wobble, drift, and false tilt.
- **GPS / GNSS** – coordinate drift, jumps, and spoofed locations.

### 2. Temporal & Multi-Frame Effects
- Ghost frames and flicker (time-based anomalies).
- Gradual drift vs sudden jumps.
- “Calm then chaos” patterns for red-team testing.

### 3. Multi-Modal Deception
- Depth vs LiDAR vs GPS vs IMU disagree in controlled ways.
- Configurable policies:
  - trusted control loop → real sensors
  - external / untrusted consumers → veiled composites

### 4. Simulator & Robotics Integration
- Hooks for:
  - ROS/ROS2 topics
  - Gazebo / Webots / Isaac Sim style environments
- Run Data Veil as a **sidecar** that sits at the exposure boundary
  of a simulated robot, not inside the control loop.

### 5. Configuration & Policy Layer
- Simple YAML/JSON policies like:

  ```yaml
  policies:
    - name: internal_control_loop
      sensor_view: real
    - name: external_dashboard
      sensor_view: veiled
    - name: third_party_integration
      sensor_view: veiled

---

## 🧩 Policy Layer (v0.2 Foundation)

Data Veil now includes an early **policy engine** that determines which clients
receive *real* sensor data and which receive *veiled* (synthetic / distorted)
data at the exposure boundary.

Policies are stored in:  
`config/policy.yaml`

Example:

```yaml
policies:
  - client: internal_control_loop
    trust: trusted
    sensor_view: real

  - client: engineering_dashboard
    trust: semi_trusted
    sensor_view: veiled

  - client: vendor_integration
    trust: untrusted
    sensor_view: veiled


---

## 🔥 Thermal / IR Sensor Demo (v0.2)

Data Veil also includes a thermal/infrared simulation and deception module.
This generates a 2D thermal field representing:

- hot machinery
- people or heat sources
- cooler vents / airflow regions
- spatial heat gradients

### What the trusted system sees

- Smooth, realistic heat distribution  
- Hot spots, cold zones  
- Consistent thermal patterns  

### What an attacker sees (veiled)

- warped heat gradients  
- ghost hot sources  
- ghost cold zones  
- impossible patterns that break reconstruction attempts  

### Run the thermal demo

```bash
python run_thermal_demo.py


---

## ⏱️ Temporal Ghosting & Flicker Demo (v0.3)

Data Veil now includes a **temporal deception module** that operates on
sequences of depth frames. Instead of attacking a single frame, this mode
targets the *evolution* of sensor data over time.

### Trusted sequence
- smooth movement of objects  
- mild noise  
- slight drift  
- stable geometry over several frames  

### Veiled (attacker) sequence
- ghost frames (old frames replayed)
- flicker (over-strong veiling on periodic frames)
- sudden jumps or inconsistent motion
- breaks temporal coherence for perception models

### Run the temporal ghosting demo

```bash
python run_temporal_ghost_demo.py
