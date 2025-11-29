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



