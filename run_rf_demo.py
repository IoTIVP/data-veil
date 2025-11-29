"""
DATA VEIL v0.4 – RF Field / Electromagnetic Deception Demo

This demo simulates an RF (radio frequency) intensity field, such as:
- WiFi / BLE coverage
- radar / UWB field strength
- general EM environment intensity

Trusted system:
  - sees a realistic RF intensity map with a few emitters + shadows.

Attacker:
  - sees a veiled RF map with:
      - warped lobes
      - interference blooms
      - dead zones / RF nulls
      - fake sources

All math is NUMPY ARRAY based. Images are only for human visualization.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


# -------- 1. Synthetic RF FIELD GENERATOR (Trusted View) -------- #

def generate_rf_field(width: int = 256, height: int = 256) -> np.ndarray:
    """
    Generate a synthetic RF intensity field in [0, 1].

    Simulates:
      - a few RF emitters (access points, beacons)
      - gradual attenuation with distance
      - mild global noise
    """
    yy, xx = np.mgrid[0:height, 0:width]

    field = np.zeros((height, width), dtype=float)

    def add_emitter(cx: float, cy: float, power: float, spread: float) -> None:
        """
        Add an RF emitter at normalized position (cx, cy),
        with power and spread controlling intensity and range.
        """
        cx_px = int(cx * width)
        cy_px = int(cy * height)
        dist2 = (xx - cx_px) ** 2 + (yy - cy_px) ** 2
        # simple gaussian-like dropoff
        contrib = power * np.exp(-dist2 / (2 * (spread ** 2)))
        nonlocal field
        field += contrib

    # A few main emitters (e.g., WiFi APs / beacons)
    add_emitter(0.25, 0.3, power=1.0, spread=120.0)
    add_emitter(0.75, 0.4, power=0.9, spread=100.0)
    add_emitter(0.5, 0.8, power=0.8, spread=110.0)

    # Mild global noise
    noise = np.random.normal(loc=0.0, scale=0.03, size=(height, width))
    field += noise

    # Normalize to [0,1]
    field = field - field.min()
    if field.max() > 0:
        field = field / field.max()

    return np.clip(field, 0.0, 1.0)


# -------- 2. DATA VEIL – RF Deception -------- #

def warp_rf_field(field: np.ndarray, strength: float = 0.25) -> np.ndarray:
    """
    Apply spatial warping to simulate:
      - multipath weirdness
      - bent lobes
      - propagation anomalies
    """
    h, w = field.shape
    yy, xx = np.mgrid[0:h, 0:w]

    # Low-frequency noise for displacement
    noise_x = np.random.normal(loc=0.0, scale=1.0, size=(h, w))
    noise_y = np.random.normal(loc=0.0, scale=1.0, size=(h, w))

    factor = 8
    small_x = noise_x[::factor, ::factor]
    small_y = noise_y[::factor, ::factor]

    up_x = np.repeat(np.repeat(small_x, factor, axis=0), factor, axis=1)
    up_y = np.repeat(np.repeat(small_y, factor, axis=0), factor, axis=1)
    up_x = up_x[:h, :w]
    up_y = up_y[:h, :w]

    disp_x = up_x * strength * 12.0
    disp_y = up_y * strength * 12.0

    map_x = np.clip(xx + disp_x, 0, w - 1).astype(int)
    map_y = np.clip(yy + disp_y, 0, h - 1).astype(int)

    warped = field.copy()
    warped[yy, xx] = field[map_y, map_x]
    return warped


def inject_rf_anomalies(
    field: np.ndarray,
    interference_blooms: int = 4,
    dead_zones: int = 3,
    radius_frac_range=(0.08, 0.18),
    bloom_strength_range=(0.4, 0.8),
    dead_strength_range=(0.5, 0.9),
) -> np.ndarray:
    """
    Insert RF anomalies:
      - interference_blooms: unusually strong RF intensity regions
      - dead_zones: RF nulls / shadows
    """
    h, w = field.shape
    out = field.copy()

    def random_bloom(is_dead: bool) -> None:
        cx = np.random.uniform(0.1, 0.9)
        cy = np.random.uniform(0.1, 0.9)
        radius_frac = np.random.uniform(*radius_frac_range)

        strength = np.random.uniform(
            *(dead_strength_range if is_dead else bloom_strength_range)
        )

        yy, xx = np.mgrid[0:h, 0:w]
        cx_px = int(cx * w)
        cy_px = int(cy * h)
        radius = int(radius_frac * min(w, h))

        dist = np.sqrt((xx - cx_px) ** 2 + (yy - cy_px) ** 2)
        mask = dist < radius

        if is_dead:
            # carve intensity down
            out[mask] -= strength * (1 - dist[mask] / radius)
        else:
            # spike intensity up
            out[mask] += strength * (1 - dist[mask] / radius)

    for _ in range(interference_blooms):
        random_bloom(is_dead=False)

    for _ in range(dead_zones):
        random_bloom(is_dead=True)

    # Re-normalize but keep some extremes
    out = np.clip(out, 0.0, 1.0)
    return out


def apply_data_veil_rf(field: np.ndarray) -> np.ndarray:
    """
    Trusted RF field IN -> Veiled RF field OUT.
    """
    warped = warp_rf_field(field, strength=0.22)
    veiled = inject_rf_anomalies(
        warped,
        interference_blooms=4,
        dead_zones=3,
        radius_frac_range=(0.07, 0.2),
    )
    return veiled


# -------- 3. VISUALIZATION -------- #

def rf_to_image(field: np.ndarray) -> Image.Image:
    """
    Map RF intensity field (0..1) to a pseudo-color image.

    Design:
      - low intensity: dark / near-black
      - medium: purple/blue
      - high: magenta/white
    """
    f = np.clip(field, 0.0, 1.0)

    # Build RGB via simple color ramp
    # Red increases with intensity
    red = f * 255.0
    # Blue also increases with intensity but with different curve
    blue = np.sqrt(f) * 255.0
    # Green is modest / mid-range
    green = (f ** 0.5) * 120.0

    rgb = np.stack([red, green, blue], axis=-1).astype("uint8")
    return Image.fromarray(rgb, mode="RGB")


def make_side_by_side_rf(trusted: np.ndarray, veiled: np.ndarray, out_path: str) -> None:
    """
    Side-by-side RF intensity maps:
      LEFT  = Trusted RF field
      RIGHT = Veiled RF field
    """
    img_left = rf_to_image(trusted)
    img_right = rf_to_image(veiled)

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
    draw.text((20, 10), "Trusted RF field", fill=(230, 230, 230))
    draw.text((img_left.width + 20, 10), "Veiled RF field", fill=(230, 230, 230))

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(out_path)


# -------- 4. DEMO ENTRY POINT -------- #

def demo_rf() -> None:
    """
    End-to-end RF deception demo:
      1. Generate a trusted RF field.
      2. Apply Data Veil RF to produce a veiled field.
      3. Save:
         - rf_trusted.png
         - rf_veiled.png
         - rf_trusted_vs_hacker.png
    """
    field = generate_rf_field()
    veiled_field = apply_data_veil_rf(field)

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    rf_to_image(field).save(out_dir / "rf_trusted.png")
    rf_to_image(veiled_field).save(out_dir / "rf_veiled.png")
    make_side_by_side_rf(field, veiled_field, out_dir / "rf_trusted_vs_hacker.png")

    print("✅ RF demo complete.")
    print(f"  - {out_dir / 'rf_trusted.png'}")
    print(f"  - {out_dir / 'rf_veiled.png'}")
    print(f"  - {out_dir / 'rf_trusted_vs_hacker.png'}")


if __name__ == "__main__":
    demo_rf()
