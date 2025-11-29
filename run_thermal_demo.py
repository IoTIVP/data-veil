"""
DATA VEIL v0.2 – Thermal / IR Sensor Deception Demo

This demo simulates a thermal (infrared) sensor:
- Trusted system sees a realistic heat map: warm objects, cooler background.
- Attacker tapping exposed thermal data sees a veiled, misleading heat map.

All operations are on NUMPY ARRAYS. Images are for visualization only.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


# -------- 1. Synthetic THERMAL GENERATOR (Trusted Heat Map) -------- #

def generate_thermal_field(width: int = 256, height: int = 256) -> np.ndarray:
    """
    Generate a synthetic thermal field (0..1), where:
      0.0 = very cold
      1.0 = very hot

    We simulate:
      - a warm background gradient
      - a few hot objects (machines, people)
      - a cooler region (vent, window, cold air)
    """
    y = np.linspace(0, 1, height).reshape(height, 1)
    x = np.linspace(0, 1, width).reshape(1, width)

    # Base: slightly warmer toward the center, cooler at edges
    center_bias = np.exp(-(((x - 0.5) ** 2 + (y - 0.5) ** 2) * 4.0))
    base = 0.3 + 0.3 * center_bias  # 0.3 .. 0.6

    field = base.copy()

    def add_hot_spot(cx: float, cy: float, radius_frac: float, strength: float) -> None:
        yy, xx = np.mgrid[0:height, 0:width]
        cx_px = int(cx * width)
        cy_px = int(cy * height)
        radius = int(radius_frac * min(width, height))

        dist = np.sqrt((xx - cx_px) ** 2 + (yy - cy_px) ** 2)
        mask = dist < radius

        field[mask] += strength * (1 - dist[mask] / radius)

    def add_cold_spot(cx: float, cy: float, radius_frac: float, strength: float) -> None:
        yy, xx = np.mgrid[0:height, 0:width]
        cx_px = int(cx * width)
        cy_px = int(cy * height)
        radius = int(radius_frac * min(width, height))

        dist = np.sqrt((xx - cx_px) ** 2 + (yy - cy_px) ** 2)
        mask = dist < radius

        field[mask] -= strength * (1 - dist[mask] / radius)

    # Add a few hot machines/people
    add_hot_spot(0.25, 0.35, 0.12, 0.35)
    add_hot_spot(0.7, 0.6, 0.14, 0.40)
    add_hot_spot(0.55, 0.25, 0.10, 0.30)

    # Add a colder region (vent/window)
    add_cold_spot(0.85, 0.15, 0.18, 0.25)

    field = np.clip(field, 0.0, 1.0)
    return field


# -------- 2. DATA VEIL – Thermal Deception -------- #

def warp_thermal_field(field: np.ndarray, strength: float = 0.25) -> np.ndarray:
    """
    Apply smooth distortions to simulate:
      - heat bleed
      - smeared hotspots
      - subtle spatial warping of temperatures
    """
    h, w = field.shape
    yy, xx = np.mgrid[0:h, 0:w]

    # Small, smooth displacement fields based on low-frequency noise
    noise_x = np.random.normal(loc=0.0, scale=1.0, size=(h, w))
    noise_y = np.random.normal(loc=0.0, scale=1.0, size=(h, w))

    # Smooth them by simple downsample/upsample trick
    factor = 8
    small_x = noise_x[::factor, ::factor]
    small_y = noise_y[::factor, ::factor]

    # Upsample back to full size (nearest neighbor is fine for distortion)
    up_x = np.repeat(np.repeat(small_x, factor, axis=0), factor, axis=1)
    up_y = np.repeat(np.repeat(small_y, factor, axis=0), factor, axis=1)
    up_x = up_x[:h, :w]
    up_y = up_y[:h, :w]

    disp_x = up_x * strength * 10.0
    disp_y = up_y * strength * 10.0

    map_x = np.clip(xx + disp_x, 0, w - 1).astype(int)
    map_y = np.clip(yy + disp_y, 0, h - 1).astype(int)

    warped = field.copy()
    warped[yy, xx] = field[map_y, map_x]
    return warped


def inject_thermal_anomalies(
    field: np.ndarray,
    hot_ghosts: int = 3,
    cold_ghosts: int = 3,
    radius_frac_range=(0.05, 0.12),
    hot_strength_range=(0.3, 0.6),
    cold_strength_range=(0.25, 0.5),
) -> np.ndarray:
    """
    Insert ghost hot and cold spots:
      - hot ghosts: fake heat sources (phantom people/machines)
      - cold ghosts: fake cold zones (fake vents, leaks)
    """
    h, w = field.shape
    out = field.copy()

    def random_spot(is_hot: bool) -> None:
        cx = np.random.uniform(0.1, 0.9)
        cy = np.random.uniform(0.1, 0.9)
        radius_frac = np.random.uniform(*radius_frac_range)
        strength = np.random.uniform(
            *(hot_strength_range if is_hot else cold_strength_range)
        )

        yy, xx = np.mgrid[0:h, 0:w]
        cx_px = int(cx * w)
        cy_px = int(cy * h)
        radius = int(radius_frac * min(w, h))

        dist = np.sqrt((xx - cx_px) ** 2 + (yy - cy_px) ** 2)
        mask = dist < radius

        if is_hot:
            out[mask] += strength * (1 - dist[mask] / radius)
        else:
            out[mask] -= strength * (1 - dist[mask] / radius)

    for _ in range(hot_ghosts):
        random_spot(is_hot=True)

    for _ in range(cold_ghosts):
        random_spot(is_hot=False)

    return np.clip(out, 0.0, 1.0)


def apply_data_veil_thermal(field: np.ndarray) -> np.ndarray:
    """
    Trusted thermal field IN -> Veiled thermal field OUT.
    """
    warped = warp_thermal_field(field, strength=0.22)
    veiled = inject_thermal_anomalies(
        warped,
        hot_ghosts=4,
        cold_ghosts=4,
        radius_frac_range=(0.04, 0.13),
    )
    return veiled


# -------- 3. VISUALIZATION – Thermal Color Map -------- #

def thermal_to_image(field: np.ndarray) -> Image.Image:
    """
    Map thermal field (0..1) to a simple pseudo-color heatmap.

    - Cold: dark blue
    - Medium: green/yellow
    - Hot: orange/red
    """
    f = np.clip(field, 0.0, 1.0)
    # Build simple RGB channels
    # Blue channel strongest at cold
    blue = (1.0 - f) * 255.0
    # Red strongest at hot
    red = f * 255.0
    # Green peaks in the middle
    green = (1.0 - np.abs(f - 0.5) * 2.0) * 255.0
    green = np.clip(green, 0.0, 255.0)

    rgb = np.stack([red, green, blue], axis=-1).astype("uint8")
    img = Image.fromarray(rgb, mode="RGB")
    return img


def make_side_by_side_thermal(trusted: np.ndarray, veiled: np.ndarray, out_path: str) -> None:
    """
    Create a side-by-side thermal image:
      LEFT  = Trusted thermal map
      RIGHT = Veiled thermal map
    """
    img_left = thermal_to_image(trusted)
    img_right = thermal_to_image(veiled)

    h = min(img_left.height, img_right.height)
    img_left = img_left.resize(
        (int(img_left.width * h / img_left.height), h),
        Image.Resampling.LANCZOS,
    )
    img_right = img_right.resize(
        (int(img_right.width * h / img_right.height), h),
        Image.Resampling.LANCZOS,
    )

    label_height = 40
    total_width = img_left.width + img_right.width

    combined = Image.new("RGB", (total_width, h + label_height), (0, 0, 0))
    combined.paste(img_left, (0, label_height))
    combined.paste(img_right, (img_left.width, label_height))

    draw = ImageDraw.Draw(combined)
    draw.text((20, 10), "Trusted thermal map", fill=(220, 220, 220))
    draw.text((img_left.width + 20, 10), "Veiled thermal map", fill=(220, 220, 220))

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(out_path)


# -------- 4. DEMO ENTRY POINT -------- #

def demo_thermal() -> None:
    """
    End-to-end thermal demo:
      1. Generate a trusted thermal map.
      2. Apply Data Veil to generate a veiled thermal map.
      3. Save:
         - thermal_trusted.png
         - thermal_veiled.png
         - thermal_trusted_vs_hacker.png
    """
    field = generate_thermal_field()
    veiled_field = apply_data_veil_thermal(field)

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    thermal_to_image(field).save(out_dir / "thermal_trusted.png")
    thermal_to_image(veiled_field).save(out_dir / "thermal_veiled.png")
    make_side_by_side_thermal(field, veiled_field, out_dir / "thermal_trusted_vs_hacker.png")

    print("✅ Thermal demo complete.")
    print(f"  - {out_dir / 'thermal_trusted.png'}")
    print(f"  - {out_dir / 'thermal_veiled.png'}")
    print(f"  - {out_dir / 'thermal_trusted_vs_hacker.png'}")


if __name__ == "__main__":
    demo_thermal()
