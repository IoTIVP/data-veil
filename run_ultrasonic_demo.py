"""
DATA VEIL – Ultrasonic Sensor Deception Demo

Simulates a simple ring of ultrasonic distance readings (like a
robot with a ring of proximity sensors) and then applies a veiled
version with:

- phantom obstacles (shorter distances than reality)
- missing obstacles (longer distances than reality)
- noisy jitter

Trusted:
  - smooth-ish distance profile around the robot

Veiled:
  - injected fake "spikes" (phantom walls)
  - hollowed-out dips (missing walls)
  - noise

Outputs:
  - examples/ultrasonic_trusted.png
  - examples/ultrasonic_veiled.png
  - examples/ultrasonic_trusted_vs_veiled.png
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def generate_ultrasonic_ring(num_sensors: int = 64) -> np.ndarray:
    """
    Create a 1D array of distances representing an ultrasonic ring
    around a robot. Units are arbitrary (normalized).
    """
    angles = np.linspace(0, 2 * np.pi, num_sensors, endpoint=False)

    # Base distance: somewhat circular with a "wall" in front
    base = 0.8 * np.ones_like(angles)

    # Add a closer wall in the front (±30 degrees)
    front_mask = (angles < np.deg2rad(30)) | (angles > np.deg2rad(330))
    base[front_mask] = 0.3

    # Add a side obstacle
    side_mask = (angles > np.deg2rad(110)) & (angles < np.deg2rad(150))
    base[side_mask] = 0.5

    # Slight random variation to feel more natural
    noise = np.random.normal(loc=0.0, scale=0.02, size=base.shape)
    base = np.clip(base + noise, 0.1, 1.0)

    return base


def apply_ultrasonic_veil(distances: np.ndarray) -> np.ndarray:
    """
    Veil the ultrasonic distances:
      - inject strong phantom obstacles (very close)
      - remove real obstacles (flatten them to far)
      - add stronger noise
    """
    veiled = distances.copy()
    n = veiled.shape[0]

    # Phantom obstacles: pick several random sectors and force them VERY close
    for _ in range(4):
        idx = np.random.randint(0, n)
        span = np.random.randint(2, 6)
        end = min(n, idx + span)
        veiled[idx:end] = 0.08  # very close "fake wall"

    # Remove real obstacles: flatten some regions to far distances
    for _ in range(3):
        idx = np.random.randint(0, n)
        span = np.random.randint(4, 10)
        end = min(n, idx + span)
        veiled[idx:end] = 0.9  # fake "no obstacle"

    # Stronger global noise
    noise = np.random.normal(loc=0.0, scale=0.06, size=veiled.shape)
    veiled = np.clip(veiled + noise, 0.05, 1.0)

    return veiled


def render_ultrasonic(
    distances: np.ndarray,
    title: str,
    out_path: Path,
    bar_color=(80, 180, 220),
) -> None:
    """
    Render the ring of distances as a bar-like strip:
    x-axis = sensor index
    y-axis = distance (inverted so closer = taller bar).

    bar_color controls the bar tint (e.g. blue for trusted, red for veiled).
    """
    num = distances.shape[0]
    width = 640
    height = 240
    margin = 40

    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.text((10, 10), title, fill=(230, 230, 230))

    plot_w = width - 2 * margin
    plot_h = height - 2 * margin

    x0 = margin
    y0 = height - margin  # bottom
    bar_w = plot_w / num

    # distances in [0,1], invert so 0 => max height, 1 => small bar
    for i, d in enumerate(distances):
        x_start = x0 + i * bar_w
        x_end = x_start + bar_w * 0.8

        bar_height = (1.0 - d) * plot_h
        y_top = y0 - bar_height

        draw.rectangle(
            (x_start, y_top, x_end, y0),
            fill=bar_color,
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def make_ultrasonic_comparison(trusted: np.ndarray, veiled: np.ndarray, out_path: Path) -> None:
    """
    Make a vertical comparison image:
      Top: trusted (blue)
      Bottom: veiled (red)
    """
    tmp_dir = Path("examples")
    tmp_dir.mkdir(exist_ok=True)

    trusted_tmp = tmp_dir / "ultrasonic_trusted_tmp.png"
    veiled_tmp = tmp_dir / "ultrasonic_veiled_tmp.png"

    render_ultrasonic(
        trusted,
        "Ultrasonic – Trusted distances",
        trusted_tmp,
        bar_color=(80, 180, 220),   # blue-ish
    )
    render_ultrasonic(
        veiled,
        "Ultrasonic – Veiled distances",
        veiled_tmp,
        bar_color=(220, 80, 80),    # red-ish
    )

    trusted_img = Image.open(trusted_tmp).convert("RGB")
    veiled_img = Image.open(veiled_tmp).convert("RGB")

    w = max(trusted_img.width, veiled_img.width)
    h = trusted_img.height + veiled_img.height

    combined = Image.new("RGB", (w, h), (0, 0, 0))
    combined.paste(trusted_img, (0, 0))
    combined.paste(veiled_img, (0, trusted_img.height))

    combined.save(out_path)

    # Cleanup temp files
    trusted_tmp.unlink(missing_ok=True)
    veiled_tmp.unlink(missing_ok=True)


def demo_ultrasonic() -> None:
    trusted = generate_ultrasonic_ring()
    veiled = apply_ultrasonic_veil(trusted)

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    trusted_path = out_dir / "ultrasonic_trusted.png"
    veiled_path = out_dir / "ultrasonic_veiled.png"
    combo_path = out_dir / "ultrasonic_trusted_vs_veiled.png"

    render_ultrasonic(
        trusted,
        "Ultrasonic – Trusted distances",
        trusted_path,
        bar_color=(80, 180, 220),   # blue-ish
    )
    render_ultrasonic(
        veiled,
        "Ultrasonic – Veiled distances",
        veiled_path,
        bar_color=(220, 80, 80),    # red-ish
    )
    make_ultrasonic_comparison(trusted, veiled, combo_path)

    print("✅ Ultrasonic demo complete.")
    print(f"  - {trusted_path}")
    print(f"  - {veiled_path}")
    print(f"  - {combo_path}")


if __name__ == "__main__":
    demo_ultrasonic()
