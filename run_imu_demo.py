"""
DATA VEIL – IMU (Gyro + Accelerometer) Deception Demo

Simulates a short time series of IMU readings:

  - Gyroscope:  gx, gy, gz  (rad/s)
  - Accelerometer: ax, ay, az (m/s^2)

Trusted:
  - smooth rotation profile + gravity on Z
  - small noise

Veiled:
  - injected drift
  - sudden spikes (fake jolts)
  - jitter

Outputs:
  - examples/imu_trusted.png
  - examples/imu_veiled.png
  - examples/imu_trusted_vs_veiled.png
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def generate_imu_series(n: int = 200, dt: float = 0.01) -> dict:
    """
    Generate synthetic IMU time series for a simple motion:
      - slow rotation around Z
      - small tilt oscillation
      - gravity mostly on -Z axis
    Returns a dict with keys: t, gx, gy, gz, ax, ay, az
    """
    t = np.linspace(0, (n - 1) * dt, n)

    # Gyro: mostly rotation around Z
    gz = 0.4 * np.sin(2 * np.pi * 0.5 * t)      # swinging yaw rate
    gx = 0.05 * np.sin(2 * np.pi * 0.2 * t)     # tiny roll rate
    gy = 0.03 * np.cos(2 * np.pi * 0.3 * t)     # tiny pitch rate

    # Accelerometer: mostly gravity on -Z plus small motion
    g = 9.81
    ax = 0.2 * np.sin(2 * np.pi * 0.7 * t)
    ay = 0.3 * np.cos(2 * np.pi * 0.4 * t)
    az = -g + 0.1 * np.sin(2 * np.pi * 0.6 * t)

    # Add small measurement noise
    gx += np.random.normal(0, 0.005, size=n)
    gy += np.random.normal(0, 0.005, size=n)
    gz += np.random.normal(0, 0.01, size=n)

    ax += np.random.normal(0, 0.02, size=n)
    ay += np.random.normal(0, 0.02, size=n)
    az += np.random.normal(0, 0.02, size=n)

    return {
        "t": t,
        "gx": gx,
        "gy": gy,
        "gz": gz,
        "ax": ax,
        "ay": ay,
        "az": az,
    }


def apply_imu_veil(imu: dict) -> dict:
    """
    Apply veiling to IMU series:
      - drift on gyro & accel
      - short spikes (fake jolts / impacts)
      - extra noise
    """
    veiled = {k: np.copy(v) for k, v in imu.items()}

    n = veiled["t"].shape[0]

    # Slow drift on gyro Z and accelerometer X/Y
    drift_gz = np.linspace(0.0, 0.25, n)
    drift_ax = np.linspace(0.0, 0.6, n)
    drift_ay = np.linspace(0.0, -0.4, n)

    veiled["gz"] += drift_gz
    veiled["ax"] += drift_ax
    veiled["ay"] += drift_ay

    # Inject spikes: fake jolts
    for _ in range(5):
        idx = np.random.randint(10, n - 10)
        span = np.random.randint(3, 8)
        end = min(n, idx + span)

        # spike in gyro
        veiled["gx"][idx:end] += np.random.choice([-1.5, 1.5])
        veiled["gy"][idx:end] += np.random.choice([-1.0, 1.0])

        # spike in accel (fake impact)
        veiled["ax"][idx:end] += np.random.choice([-3.0, 3.0])
        veiled["ay"][idx:end] += np.random.choice([-2.0, 2.0])
        veiled["az"][idx:end] += np.random.choice([-4.0, 4.0])

    # Extra noise on all channels
    for key in ["gx", "gy", "gz", "ax", "ay", "az"]:
        veiled[key] += np.random.normal(0, 0.03 if key.startswith("g") else 0.1, size=n)

    return veiled


def _plot_series_panel(
    t: np.ndarray,
    series_dict: dict,
    title: str,
    height: int = 180,
    width: int = 800,
    bg=(0, 0, 0),
) -> Image.Image:
    """
    Render a multi-channel time series (gx, gy, gz or ax, ay, az) in one panel.
    """
    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    margin_left = 50
    margin_right = 10
    margin_top = 25
    margin_bottom = 25

    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    x0 = margin_left
    y0 = margin_top

    # Draw title
    draw.text((10, 5), title, fill=(230, 230, 230))

    # Determine global min/max among all channels
    values = np.concatenate([series_dict[k] for k in series_dict])
    vmin, vmax = values.min(), values.max()
    if abs(vmax - vmin) < 1e-6:
        vmax = vmin + 1.0  # avoid division by zero

    def to_xy(idx, value):
        x = x0 + (idx / (len(t) - 1)) * plot_w
        # invert y for plotting (higher value => higher on image)
        normalized = (value - vmin) / (vmax - vmin)
        y = y0 + (1.0 - normalized) * plot_h
        return x, y

    # Colors per channel
    colors = {
        "gx": (200, 80, 80),
        "gy": (80, 200, 80),
        "gz": (80, 80, 220),
        "ax": (200, 120, 80),
        "ay": (120, 200, 200),
        "az": (220, 220, 80),
    }

    # Draw axes baseline
    draw.rectangle((x0, y0, x0 + plot_w, y0 + plot_h), outline=(100, 100, 100), width=1)

    # Draw each series
    for key, series in series_dict.items():
        color = colors.get(key, (180, 180, 180))
        prev_xy = None
        for i, val in enumerate(series):
            x, y = to_xy(i, val)
            if prev_xy is not None:
                draw.line((prev_xy[0], prev_xy[1], x, y), fill=color, width=1)
            prev_xy = (x, y)

    # Add legend (top-right)
    legend_y = margin_top
    legend_x = width - 150
    for key in series_dict.keys():
        color = colors.get(key, (180, 180, 180))
        draw.rectangle((legend_x, legend_y, legend_x + 10, legend_y + 10), fill=color)
        draw.text((legend_x + 14, legend_y - 2), key, fill=(220, 220, 220))
        legend_y += 14

    return img


def render_imu_trusted(imu: dict, out_path: Path) -> None:
    t = imu["t"]
    gyro_panel = _plot_series_panel(
        t,
        {"gx": imu["gx"], "gy": imu["gy"], "gz": imu["gz"]},
        title="IMU – Gyro (Trusted)",
    )
    accel_panel = _plot_series_panel(
        t,
        {"ax": imu["ax"], "ay": imu["ay"], "az": imu["az"]},
        title="IMU – Accelerometer (Trusted)",
    )

    width = max(gyro_panel.width, accel_panel.width)
    height = gyro_panel.height + accel_panel.height
    img = Image.new("RGB", (width, height), (0, 0, 0))
    img.paste(gyro_panel, (0, 0))
    img.paste(accel_panel, (0, gyro_panel.height))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def render_imu_veiled(imu: dict, out_path: Path) -> None:
    t = imu["t"]
    gyro_panel = _plot_series_panel(
        t,
        {"gx": imu["gx"], "gy": imu["gy"], "gz": imu["gz"]},
        title="IMU – Gyro (Veiled)",
    )
    accel_panel = _plot_series_panel(
        t,
        {"ax": imu["ax"], "ay": imu["ay"], "az": imu["az"]},
        title="IMU – Accelerometer (Veiled)",
    )

    width = max(gyro_panel.width, accel_panel.width)
    height = gyro_panel.height + accel_panel.height
    img = Image.new("RGB", (width, height), (0, 0, 0))
    img.paste(gyro_panel, (0, 0))
    img.paste(accel_panel, (0, gyro_panel.height))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def make_imu_comparison(trusted: dict, veiled: dict, out_path: Path) -> None:
    tmp_dir = Path("examples")
    tmp_dir.mkdir(exist_ok=True)

    trusted_tmp = tmp_dir / "imu_trusted_tmp.png"
    veiled_tmp = tmp_dir / "imu_veiled_tmp.png"

    render_imu_trusted(trusted, trusted_tmp)
    render_imu_veiled(veiled, veiled_tmp)

    trusted_img = Image.open(trusted_tmp).convert("RGB")
    veiled_img = Image.open(veiled_tmp).convert("RGB")

    width = max(trusted_img.width, veiled_img.width)
    height = trusted_img.height + veiled_img.height + 30

    combined = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(combined)
    draw.text((10, 5), "IMU – Trusted vs Veiled", fill=(240, 240, 240))

    combined.paste(trusted_img, (0, 30))
    combined.paste(veiled_img, (0, 30 + trusted_img.height))

    combined.save(out_path)

    trusted_tmp.unlink(missing_ok=True)
    veiled_tmp.unlink(missing_ok=True)


def demo_imu() -> None:
    trusted = generate_imu_series()
    veiled = apply_imu_veil(trusted)

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    trusted_path = out_dir / "imu_trusted.png"
    veiled_path = out_dir / "imu_veiled.png"
    combo_path = out_dir / "imu_trusted_vs_veiled.png"

    render_imu_trusted(trusted, trusted_path)
    render_imu_veiled(veiled, veiled_path)
    make_imu_comparison(trusted, veiled, combo_path)

    print("✅ IMU demo complete.")
    print(f"  - {trusted_path}")
    print(f"  - {veiled_path}")
    print(f"  - {combo_path}")


if __name__ == "__main__":
    demo_imu()
