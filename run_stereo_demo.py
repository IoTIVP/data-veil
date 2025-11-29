"""
DATA VEIL – Stereo Vision Deception Demo

Simulates a simple stereo camera pair (left/right) from a base scene,
then applies a veiled version that introduces:

- disparity errors
- local horizontal jitters
- extra noise

Trusted:
  - left and right images with a consistent small horizontal offset

Veiled:
  - mismatched offsets
  - band-wise shifts
  - noise

Outputs:
  - examples/stereo_trusted_pair.png   (left/right pair)
  - examples/stereo_veiled_pair.png    (left/right pair)
  - examples/stereo_trusted_vs_veiled.png (4-panel comparison)
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def generate_base_scene(width: int = 320, height: int = 240) -> Image.Image:
    """
    Create a synthetic grayscale base scene that could represent
    a simple environment for stereo imaging.
    """
    # Gradient background
    img = Image.new("L", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            t = (x / (width - 1)) * 0.6 + (y / (height - 1)) * 0.4
            val = int(40 + 160 * t)
            pixels[x, y] = val

    draw = ImageDraw.Draw(img)

    # Add a few shapes (walls / boxes)
    draw.rectangle((40, 90, 110, 210), fill=180)
    draw.rectangle((200, 60, 290, 200), fill=120)
    draw.rectangle((135, 120, 185, 220), fill=200)

    # Some small "details"
    draw.ellipse((30, 30, 50, 50), fill=220)
    draw.ellipse((260, 30, 280, 50), fill=220)

    return img


def make_stereo_pair(base: Image.Image, disparity_px: int = 6) -> tuple[Image.Image, Image.Image]:
    """
    Generate a left/right stereo pair by shifting the base image
    slightly in opposite directions.
    """
    w, h = base.size

    # Left image: shift right a bit
    left = Image.new("L", (w, h), color=0)
    left.paste(base.crop((0, 0, w - disparity_px, h)), (disparity_px, 0))

    # Right image: shift left a bit
    right = Image.new("L", (w, h), color=0)
    right.paste(base.crop((disparity_px, 0, w, h)), (0, 0))

    return left, right


def apply_stereo_veil(left: Image.Image, right: Image.Image) -> tuple[Image.Image, Image.Image]:
    """
    Apply veiling to stereo pair:
      - introduce band-wise horizontal jitter
      - add small random disparity errors
      - overlay noise
    """
    def jitter_image(img: Image.Image) -> Image.Image:
        w, h = img.size
        arr = np.array(img).astype(np.float32)

        band_height = 16
        jittered = np.zeros_like(arr)

        for y in range(0, h, band_height):
            band_end = min(y + band_height, h)
            offset = np.random.randint(-3, 4)  # -3..+3 pixels
            if offset >= 0:
                jittered[y:band_end, offset:] = arr[y:band_end, : w - offset]
            else:
                off = -offset
                jittered[y:band_end, : w - off] = arr[y:band_end, off:]

        # Add noise
        noise = np.random.normal(loc=0.0, scale=5.0, size=arr.shape)
        jittered = jittered + noise
        jittered = np.clip(jittered, 0, 255).astype(np.uint8)

        return Image.fromarray(jittered, mode="L")

    veiled_left = jitter_image(left)
    veiled_right = jitter_image(right)

    return veiled_left, veiled_right


def to_rgb(img: Image.Image) -> Image.Image:
    """
    Convert a single-channel L image to RGB for consistency in outputs.
    """
    return img.convert("RGB")


def make_pair_panel(left: Image.Image, right: Image.Image, label: str) -> Image.Image:
    """
    Create a horizontal panel:
      [left] [right]
    with a label bar above.
    """
    left_rgb = to_rgb(left)
    right_rgb = to_rgb(right)

    # Normalize heights
    h = min(left_rgb.height, right_rgb.height)
    def resize_keep_aspect(im: Image.Image) -> Image.Image:
        return im.resize(
            (int(im.width * h / im.height), h),
            Image.Resampling.LANCZOS,
        )

    left_r = resize_keep_aspect(left_rgb)
    right_r = resize_keep_aspect(right_rgb)

    label_height = 30
    total_width = left_r.width + right_r.width
    panel = Image.new("RGB", (total_width, h + label_height), (0, 0, 0))
    draw = ImageDraw.Draw(panel)

    panel.paste(left_r, (0, label_height))
    panel.paste(right_r, (left_r.width, label_height))

    draw.text((10, 7), f"{label} – LEFT", fill=(230, 230, 230))
    draw.text((left_r.width + 10, 7), f"{label} – RIGHT", fill=(230, 230, 230))

    return panel


def make_stereo_comparison(
    left_trusted: Image.Image,
    right_trusted: Image.Image,
    left_veiled: Image.Image,
    right_veiled: Image.Image,
    out_path: Path,
) -> None:
    """
    Build a 4-panel comparison image:

      Row 1: Trusted left / Trusted right
      Row 2: Veiled left  / Veiled right
    """
    trusted_panel = make_pair_panel(left_trusted, right_trusted, "Trusted")
    veiled_panel = make_pair_panel(left_veiled, right_veiled, "Veiled")

    total_width = max(trusted_panel.width, veiled_panel.width)
    total_height = trusted_panel.height + veiled_panel.height + 40

    img = Image.new("RGB", (total_width, total_height), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    title = "Stereo Vision – Trusted vs Veiled"
    draw.text((10, 10), title, fill=(250, 250, 250))

    y = 40
    img.paste(trusted_panel, (0, y))
    y += trusted_panel.height
    img.paste(veiled_panel, (0, y))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def demo_stereo() -> None:
    """
    End-to-end stereo deception demo.
    """
    base = generate_base_scene()
    left_trusted, right_trusted = make_stereo_pair(base, disparity_px=6)
    left_veiled, right_veiled = apply_stereo_veil(left_trusted, right_trusted)

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    left_trusted_path = out_dir / "stereo_left_trusted.png"
    right_trusted_path = out_dir / "stereo_right_trusted.png"
    left_veiled_path = out_dir / "stereo_left_veiled.png"
    right_veiled_path = out_dir / "stereo_right_veiled.png"
    comparison_path = out_dir / "stereo_trusted_vs_veiled.png"

    left_trusted.save(left_trusted_path)
    right_trusted.save(right_trusted_path)
    left_veiled.save(left_veiled_path)
    right_veiled.save(right_veiled_path)
    make_stereo_comparison(
        left_trusted,
        right_trusted,
        left_veiled,
        right_veiled,
        comparison_path,
    )

    print("✅ Stereo demo complete.")
    print(f"  - {left_trusted_path}")
    print(f"  - {right_trusted_path}")
    print(f"  - {left_veiled_path}")
    print(f"  - {right_veiled_path}")
    print(f"  - {comparison_path}")


if __name__ == "__main__":
    demo_stereo()
