"""
DATA VEIL v0.1 – Depth-Field Sensor Deception Demo

Core idea:
- We treat a "sensor flow" as a NUMPY ARRAY (depth field: distance per pixel).
- The trusted system sees the REAL depth field.
- An attacker tapping the exposed stream sees a VEILED version of that field.

PNG images are ONLY for visualization of those arrays, not the core logic.
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


# -------- 1. Synthetic SENSOR GENERATOR (Trusted Depth Field) -------- #

def generate_depth_field(width: int = 256, height: int = 256) -> np.ndarray:
    """
    Generate a synthetic depth field (2D matrix of distances 0..1).
    This simulates what a depth sensor or LiDAR slice might see:
      - sloped floor / wall
      - a couple of "closer" objects popping out
    """
    # Base depth: smooth gradient (far at top, closer at bottom-right)
    y = np.linspace(0, 1, height).reshape(height, 1)
    x = np.linspace(0, 1, width).reshape(1, width)
    depth = 0.3 + 0.7 * (0.5 * y + 0.5 * (1 - x))  # 0.3..1.0

    field = depth.copy()

    def add_blob(cx: int, cy: int, radius: int, strength: float) -> None:
        yy, xx = np.mgrid[0:height, 0:width]
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        mask = dist < radius
        # Bring the depth closer (smaller values) inside the blob
        field[mask] -= strength * (1 - dist[mask] / radius)

    # Add two "objects" in the scene
    min_side = min(width, height)
    add_blob(int(width * 0.3), int(height * 0.6), int(min_side * 0.15), 0.25)
    add_blob(int(width * 0.7), int(height * 0.4), int(min_side * 0.12), 0.20)

    field = np.clip(field, 0.0, 1.0)
    return field


# -------- 2. DATA VEIL – Veiling / Deception on the Depth Field -------- #

def warp_depth_field(depth: np.ndarray, strength: float = 8.0, curve: float = 1.8) -> np.ndarray:
    """
    Apply a non-linear "warp" to the depth field to simulate:
      - distorted ranges
      - warped geometry

    This operates on the NUMPY ARRAY, not on an image.
    """
    d = np.clip(depth, 0.0, 1.0) ** curve
    h, w = d.shape

    yy, xx = np.mgrid[0:h, 0:w]

    # Displacement based on depth value (closer/farther shift differently)
    disp_x = (d - 0.5) * strength
    disp_y = (0.5 - d) * strength

    map_x = np.clip(xx + disp_x, 0, w - 1)
    map_y = np.clip(yy + disp_y, 0, h - 1)

    mx = map_x.astype(int)
    my = map_y.astype(int)

    warped = d.copy()
    warped[yy, xx] = d[my, mx]
    return warped


def carve_holes(
    depth: np.ndarray,
    count: int = 5,
    min_radius: int = 10,
    max_radius: int = 40,
    mode: str = "noise",
) -> np.ndarray:
    """
    Carve "voids" in the depth field to simulate:
      - missing returns
      - blind spots
      - noisy regions

    mode:
      - "far"   -> set those cells to max distance (1.0)
      - "near"  -> set those cells to min distance (0.0)
      - "noise" -> random distances in those regions
    """
    h, w = depth.shape
    out = depth.copy()
    yy, xx = np.mgrid[0:h, 0:w]

    for _ in range(count):
        r = np.random.randint(min_radius, max_radius)
        cx = np.random.randint(0, w)
        cy = np.random.randint(0, h)
        dist2 = (xx - cx) ** 2 + (yy - cy) ** 2
        mask = dist2 < r * r

        if mode == "far":
            out[mask] = 1.0
        elif mode == "near":
            out[mask] = 0.0
        else:  # "noise"
            out[mask] = np.random.uniform(0.0, 1.0, size=mask.sum())

    return out


def apply_data_veil(depth: np.ndarray) -> np.ndarray:
    """
    Trusted depth field IN -> Veiled depth field OUT.

    This function represents what an attacker or untrusted client would see
    when they tap the "sensor stream" at the exposure boundary
    (API, gateway, cloud telemetry, etc.).
    """
    warped = warp_depth_field(depth, strength=15.0, curve=2.0)
    veiled = carve_holes(
        warped,
        count=8,
        min_radius=15,
        max_radius=50,
        mode="noise",
    )
    veiled = np.clip(veiled, 0.0, 1.0)
    return veiled


# -------- 3. VISUALIZATION – Optional, for demo only -------- #

def depth_to_image(depth: np.ndarray) -> Image.Image:
    """
    Convert a depth field (0..1) to a grayscale RGB image for visualization.

    This is ONLY to see what the sensor arrays look like.
    The core logic remains numeric in the arrays.
    """
    d = np.clip(depth, 0.0, 1.0)
    arr = (d * 255).astype("uint8")
    img = Image.fromarray(arr, mode="L")
    return img.convert("RGB")


def make_side_by_side(trusted: np.ndarray, veiled: np.ndarray, out_path: str) -> None:
    """
    Build a side-by-side image:
      LEFT  = Trusted Sensor View (real depth field)
      RIGHT = Hacker / Veiled View (distorted depth field)
    """
    img_left = depth_to_image(trusted)
    img_right = depth_to_image(veiled)

    # Normalize heights
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
    draw.text((20, 10), "Trusted depth field", fill=(200, 200, 200))
    draw.text((img_left.width + 20, 10), "Veiled depth field", fill=(200, 200, 200))

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(out_path)


# -------- 4. DEMO ENTRY POINT -------- #

def demo() -> None:
    """
    End-to-end demo:
      1. Generate a synthetic depth field (trusted view).
      2. Apply Data Veil to get the veiled field (attacker view).
      3. Save:
         - trusted_depth.png
         - veiled_depth.png
         - trusted_vs_hacker.png
    """
    depth = generate_depth_field()
    veiled = apply_data_veil(depth)

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    # Save individual views
    depth_to_image(depth).save(out_dir / "trusted_depth.png")
    depth_to_image(veiled).save(out_dir / "veiled_depth.png")

    # Side-by-side hero image
    make_side_by_side(depth, veiled, out_dir / "trusted_vs_hacker.png")

    print("✅ Demo complete.")
    print(f"  - {out_dir / 'trusted_depth.png'}")
    print(f"  - {out_dir / 'veiled_depth.png'}")
    print(f"  - {out_dir / 'trusted_vs_hacker.png'}")


if __name__ == "__main__":
    demo()
