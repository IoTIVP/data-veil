"""
DATA VEIL v0.1 – LiDAR Sweep Sensor Deception Demo

This demo treats a LiDAR scan as a 1D NUMPY ARRAY of ranges (0..1),
then generates a veiled version of that scan to show what an attacker
would see if they tap the exposed LiDAR stream.

- Trusted system  -> real LiDAR ranges
- Attacker/client -> veiled LiDAR ranges

Images are just visualizations of those arrays.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


# -------- 1. Synthetic LiDAR GENERATOR (Trusted Scan) -------- #

def generate_lidar_scan(num_beams: int = 360) -> np.ndarray:
    """
    Generate a synthetic 360° LiDAR scan.

    Values are normalized distances in [0, 1]:
      0.0 = very close
      1.0 = far
    """
    angles = np.linspace(0, 2 * np.pi, num_beams, endpoint=False)

    # Base environment: slightly wavy distance field
    base = 0.6 + 0.2 * np.sin(2 * angles) + 0.1 * np.cos(3 * angles)

    scan = base.copy()

    # Add a few "closer" obstacles (distance dips)
    def add_obstacle(center_angle_deg: float, width_deg: float, depth: float) -> None:
        center = np.deg2rad(center_angle_deg)
        width = np.deg2rad(width_deg)
        diff = np.angle(np.exp(1j * (angles - center)))  # wrap to [-pi, pi]
        mask = np.abs(diff) < width / 2
        scan[mask] -= depth * (1 - np.abs(diff[mask]) / (width / 2))

    add_obstacle(45, 25, 0.3)
    add_obstacle(160, 35, 0.25)
    add_obstacle(260, 40, 0.28)

    scan = np.clip(scan, 0.1, 1.0)  # keep it reasonable
    return scan


# -------- 2. DATA VEIL – Veiling / Deception on the LiDAR Scan -------- #

def warp_lidar_scan(scan: np.ndarray, strength: float = 0.2) -> np.ndarray:
    """
    Apply multiplicative noise to ranges to simulate:
      - wrong distance readings
      - slightly warped environment
    """
    num_beams = scan.shape[0]
    noise = np.random.normal(loc=1.0, scale=strength, size=num_beams)
    warped = scan * noise
    return np.clip(warped, 0.05, 1.2)


def inject_lidar_voids_and_ghosts(
    scan: np.ndarray,
    void_count: int = 4,
    ghost_count: int = 5,
    max_span_deg: float = 25.0,
) -> np.ndarray:
    """
    Carve voids (no return / max distance) and add ghost returns
    (fake close objects) into the LiDAR scan.
    """
    out = scan.copy()
    num_beams = scan.shape[0]

    def span_to_indices(center_idx: int, span_beams: int) -> np.ndarray:
        half = span_beams // 2
        idx = (np.arange(center_idx - half, center_idx + half + 1) + num_beams) % num_beams
        return idx

    # Voids – missing returns or interference
    for _ in range(void_count):
        center_idx = np.random.randint(0, num_beams)
        span_beams = np.random.randint(5, int(num_beams * (max_span_deg / 360.0)))
        idx = span_to_indices(center_idx, span_beams)
        out[idx] = 1.2  # beyond max range

    # Ghosts – fake close obstacles
    for _ in range(ghost_count):
        center_idx = np.random.randint(0, num_beams)
        span_beams = np.random.randint(3, int(num_beams * (max_span_deg / 360.0)))
        idx = span_to_indices(center_idx, span_beams)
        ghost_range = np.random.uniform(0.1, 0.35)
        out[idx] = ghost_range

    return np.clip(out, 0.05, 1.2)


def apply_data_veil_lidar(scan: np.ndarray) -> np.ndarray:
    """
    Trusted LiDAR scan IN -> Veiled LiDAR scan OUT
    (what the attacker / untrusted client would see).
    """
    warped = warp_lidar_scan(scan, strength=0.22)
    veiled = inject_lidar_voids_and_ghosts(
        warped,
        void_count=5,
        ghost_count=6,
        max_span_deg=30.0,
    )
    return veiled


# -------- 3. VISUALIZATION – Polar Plot of the Scan -------- #

def lidar_to_image(scan: np.ndarray, size: int = 512) -> Image.Image:
    """
    Visualize a LiDAR scan as a simple polar plot:
      - center = sensor
      - rays = distances
    """
    num_beams = scan.shape[0]
    img = Image.new("RGB", (size, size), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = cy = size // 2
    max_radius = size // 2 - 10

    # Normalize scan to [0, 1] for drawing radius
    s = np.clip(scan, 0.0, 1.2)
    s = (s - s.min()) / (s.max() - s.min() + 1e-8)

    for i in range(num_beams):
        angle = 2 * np.pi * i / num_beams
        r = s[i] * max_radius
        x = cx + r * np.cos(angle)
        y = cy + r * np.sin(angle)

        # draw a small point or short line at the end of the ray
        draw.line((cx, cy, x, y), fill=(40, 120, 240), width=1)

    # Draw sensor center
    draw.ellipse(
        (cx - 4, cy - 4, cx + 4, cy + 4),
        fill=(255, 255, 255),
        outline=(255, 255, 255),
    )

    return img


def make_side_by_side_images(left: Image.Image, right: Image.Image, out_path: str) -> None:
    """
    Combine two images side by side with labels at the top.
    """
    h = min(left.height, right.height)
    left = left.resize(
        (int(left.width * h / left.height), h),
        Image.Resampling.LANCZOS,
    )
    right = right.resize(
        (int(right.width * h / right.height), h),
        Image.Resampling.LANCZOS,
    )

    label_height = 40
    total_width = left.width + right.width

    combined = Image.new("RGB", (total_width, h + label_height), (0, 0, 0))
    combined.paste(left, (0, label_height))
    combined.paste(right, (left.width, label_height))

    draw = ImageDraw.Draw(combined)
    draw.text((20, 10), "Trusted LiDAR scan", fill=(200, 200, 200))
    draw.text((left.width + 20, 10), "Veiled LiDAR scan", fill=(200, 200, 200))

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(out_path)


# -------- 4. DEMO ENTRY POINT -------- #

def demo_lidar() -> None:
    """
    End-to-end LiDAR demo:
      1. Generate a trusted LiDAR scan.
      2. Apply Data Veil to produce a veiled scan.
      3. Save:
         - lidar_trusted.png
         - lidar_veiled.png
         - lidar_trusted_vs_hacker.png
    """
    scan = generate_lidar_scan()
    veiled_scan = apply_data_veil_lidar(scan)

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    img_trusted = lidar_to_image(scan)
    img_veiled = lidar_to_image(veiled_scan)

    img_trusted.save(out_dir / "lidar_trusted.png")
    img_veiled.save(out_dir / "lidar_veiled.png")
    make_side_by_side_images(
        img_trusted,
        img_veiled,
        out_dir / "lidar_trusted_vs_hacker.png",
    )

    print("✅ LiDAR demo complete.")
    print(f"  - {out_dir / 'lidar_trusted.png'}")
    print(f"  - {out_dir / 'lidar_veiled.png'}")
    print(f"  - {out_dir / 'lidar_trusted_vs_hacker.png'}")


if __name__ == "__main__":
    demo_lidar()
