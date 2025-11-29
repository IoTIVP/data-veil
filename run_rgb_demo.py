"""
DATA VEIL – RGB Camera Deception Demo

Simulates a simple RGB camera "scene" and then applies a veiled
version that an attacker / external system would see.

Trusted:
  - clean synthetic scene (background gradient + shapes)

Veiled:
  - blur
  - color warp
  - edge jitter
  - noise

Outputs:
  - examples/rgb_trusted.png
  - examples/rgb_veiled.png
  - examples/rgb_trusted_vs_veiled.png
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def generate_rgb_scene(width: int = 320, height: int = 240) -> Image.Image:
    """
    Create a synthetic RGB "camera frame":
      - vertical gradient background
      - a few colored rectangles / circles
      - feels like a simple robotics camera view
    """
    # Background gradient
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    for y in range(height):
        t = y / (height - 1)
        r = int(40 + 80 * t)
        g = int(40 + 60 * t)
        b = int(60 + 120 * t)
        for x in range(width):
            pixels[x, y] = (r, g, b)

    draw = ImageDraw.Draw(img)

    # "Floor" strip
    draw.rectangle(
        (0, int(height * 0.75), width, height),
        fill=(50, 50, 60),
    )

    # Some blocks (like boxes / obstacles)
    draw.rectangle(
        (40, 130, 120, 220),
        fill=(180, 110, 80),
    )
    draw.rectangle(
        (200, 140, 290, 215),
        fill=(80, 160, 110),
    )

    # A "pillar" or tall object
    draw.rectangle(
        (150, 80, 180, 220),
        fill=(130, 130, 150),
    )

    # A "light" or sensor
    draw.ellipse(
        (30, 40, 70, 80),
        fill=(220, 220, 120),
    )

    return img


def apply_rgb_veil(trusted_img: Image.Image) -> Image.Image:
    """
    Apply a set of distortions to simulate a veiled camera view:
      - slight perspective-ish warp (via jittered columns)
      - blur
      - color shifts
      - noise overlays
    """
    w, h = trusted_img.size

    # Convert to numpy for color ops
    arr = np.array(trusted_img).astype(np.float32)

    # Color warp: shift channels in a way that feels "off"
    # Slight green boost, red attenuation, blue variance
    arr[..., 0] *= 0.9   # red
    arr[..., 1] *= 1.1   # green
    arr[..., 2] *= 1.05  # blue

    # Clip back to [0,255]
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, mode="RGB")

    # Add a mild blur
    img = img.filter(ImageFilter.GaussianBlur(radius=1.4))

    # Jitter vertical strips (simulate edge misalignment / rolling shutter weirdness)
    jittered = Image.new("RGB", (w, h))
    strip_width = 8
    for x in range(0, w, strip_width):
        strip = img.crop((x, 0, min(x + strip_width, w), h))
        offset = int(np.random.randint(-2, 3))  # -2 to +2 pixels
        jittered.paste(strip, (x, offset if offset > 0 else 0))
    img = jittered

    # Add noise overlay
    noise = np.random.normal(loc=0.0, scale=10.0, size=(h, w, 3))
    arr = np.array(img).astype(np.float32)
    arr += noise
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, mode="RGB")

    return img


def make_rgb_side_by_side(trusted: Image.Image, veiled: Image.Image, out_path: Path) -> None:
    """
    Build a side-by-side comparison:
      LEFT  = trusted RGB
      RIGHT = veiled RGB
    """
    h = min(trusted.height, veiled.height)
    def resize_keep_aspect(im: Image.Image) -> Image.Image:
        return im.resize(
            (int(im.width * h / im.height), h),
            Image.Resampling.LANCZOS,
        )

    left = resize_keep_aspect(trusted)
    right = resize_keep_aspect(veiled)

    label_height = 40
    total_width = left.width + right.width
    combined = Image.new("RGB", (total_width, h + label_height), (0, 0, 0))
    draw = ImageDraw.Draw(combined)

    combined.paste(left, (0, label_height))
    combined.paste(right, (left.width, label_height))

    draw.text((10, 10), "Trusted RGB camera", fill=(230, 230, 230))
    draw.text((left.width + 10, 10), "Veiled RGB camera", fill=(230, 230, 230))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(out_path)


def demo_rgb() -> None:
    """
    End-to-end RGB deception demo:
      1. Generate a trusted RGB camera scene.
      2. Apply Data Veil to create a veiled RGB frame.
      3. Save trusted, veiled, and side-by-side images.
    """
    trusted = generate_rgb_scene()
    veiled = apply_rgb_veil(trusted)

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    trusted_path = out_dir / "rgb_trusted.png"
    veiled_path = out_dir / "rgb_veiled.png"
    side_path = out_dir / "rgb_trusted_vs_veiled.png"

    trusted.save(trusted_path)
    veiled.save(veiled_path)
    make_rgb_side_by_side(trusted, veiled, side_path)

    print("✅ RGB demo complete.")
    print(f"  - {trusted_path}")
    print(f"  - {veiled_path}")
    print(f"  - {side_path}")


if __name__ == "__main__":
    demo_rgb()
