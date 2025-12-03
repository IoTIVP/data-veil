# DATA VEIL – Project Roadmap

This roadmap describes where Data Veil is today and where it is going next.

---

## 0.4.x – Current Capabilities

Status: Implemented

- Multi-sensor synthetic veiling:
  - Depth maps
  - LiDAR ranges
  - Radar range–Doppler maps
  - Thermal / IR
  - RF intensity fields
  - IMU (gyro + accel)
  - Ultrasonic rings
  - Temporal "ghosting" sequences
- Trusted vs veiled image demos for multiple sensors.
- Integrated Python core (`data_veil_core`) with:
  - Distortion functions per sensor type
  - Randomness control (`random_control`) with seeding
  - YAML-backed profiles via `config/profiles.yaml`
- Policy configuration via `config/policies.yaml`.
- Fusion and stats demos showing:
  - Differences between trusted and veiled streams
  - How multiple sensors are affected together
- Realtime depth viewer:
  - Trusted vs veiled split-screen
  - Live profile switching (1=light, 2=privacy, 3=ghost, 4=chaos)

---

## 0.5.x – Short-Term Targets

Goal: Make Data Veil more practical and easier to integrate.

Planned items:

1. Multi-sensor profile demo (script)
   - Apply multiple profiles to a bundle of synthetic sensors.
   - Print summary stats (mean abs diff, max diff) per sensor and profile.
   - Show how to route different sensors through different profiles.

2. Simple integration examples
   - Example: "veil before logging":
     - Trusted arrays used for decision-making.
     - Veiled arrays sent to logs or external consumers.
   - Example: "veil for synthetic dataset export":
     - Trusted dataset for internal training.
     - Veiled dataset for sharing.

3. Realtime improvements
   - Optional: add keyboard controls to pause/resume.
   - Optional: add basic performance timing to frame updates.

4. Documentation polish
   - Expand README with more code snippets.
   - Add diagrams for trusted vs veiled paths.
   - Clarify threat model and constraints.

---

## 1.0.0 – First Stable Release

Goal: Turn Data Veil into a cleanly installable, well-documented toolkit.

Planned items:

1. Packaging and distribution
   - Publish to PyPI:
     - `pip install data-veil`
   - Clean `setup.cfg` / `pyproject.toml`.
   - Versioned releases (0.5.x, 0.9.x, 1.0.0).

2. API surface
   - Stable top-level imports:
     - `from data_veil_core import veil_depth, veil_lidar, ...`
   - Documented arguments, expected shapes, and return types.
   - Clear error messages for invalid inputs.

3. Profiles and policies
   - Document YAML formats under `config/`.
   - Examples of:
     - light / privacy / ghost / chaos profiles.
     - policy-based enabling/disabling of veils per sensor.

4. Integration recipes
   - Example: wrapping sensors before a logging/telemetry layer.
   - Example: using Data Veil inside a robotics or simulation loop.
   - Example: using Data Veil to generate synthetic "safe-to-share" datasets.

5. Test coverage and CI (optional)
   - Basic unit tests for:
     - Each sensor veiling function.
     - Profile lookup logic.
     - Randomness control.
   - Optional GitHub Actions workflow for linting/tests.

---

## Long-Term Ideas (Post-1.0)

These are future directions, not promises.

- Additional sensor modalities:
  - Magnetometer
  - GPS-like coordinates
  - Audio-based distance or classification streams
- More advanced distortion modes:
  - Temporally coherent ghosting for sequences.
  - Spatially structured patterns for RF/Radar fields.
- Interface integrations:
  - Web-based demo (e.g. Streamlit) for interactive exploration.
  - Example adapters for ROS2 or MQTT.

---

This roadmap is intentionally flexible. The main focus is:

- Keep Data Veil simple to understand.
- Make it easy to plug into existing pipelines.
- Make it a useful tool for research, simulation, and privacy-preserving sensor experimentation.
