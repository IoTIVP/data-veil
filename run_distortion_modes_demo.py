"""
DATA VEIL – Distortion Modes Demo (Depth Example)

Shows how the same trusted depth field can be veiled with different
"intensity profiles":

- STEALTH: light, subtle veiling (almost real)
- DEFAULT: current standard veiling
- AGGRESSIVE: heavier distortion
- SCI-FI: extreme, glitchy distortion

Output:
  - examples/depth_distortion_modes.png
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

from run_demo import generate_depth_field, apply_data_veil, depth_to_image


def apply_mode(field: np.ndarray, mode: str) -> np.ndarray:
    """
    Take a trusted depth field and return a veiled version
    according to the chosen mode.
    """
    base = field

    if mode == "stealth":
        # Mostly real, slightly veiled
        veiled = apply_data_veil(base)
        combined = 0.75 * base + 0.25 * veiled
        return np.clip(combined, 0.0, 1.0)

    elif mode == "default":
        # Current standard veiling
        return np.clip(apply_data_veil(base), 0.0, 1.0)

    elif mode == "aggressive":
        # Apply veiling twice for stronger distortion
        v1 = apply_data_veil(base)
        v2 = apply_data_veil(v1)
        return np.clip(v2, 0.0, 1.0)

    elif mode == "sci_fi":
        # Double veil + extra noise for a glitchy, sci-fi effect
        v1 = apply_data_veil(base)
        v2 = apply_data_veil(v1)
        noise = np.random.normal(loc=0.0, scale=0.08, size=base.shape)
        out = v2 + noise
        return np.clip(out, 0.0, 1.0)

    else:
        raise ValueError(f"Unknown mode: {mode}")


def make_modes_strip(field: np.ndarray, out_path: Path) -> None:
    """
    Build a horizontal strip:
      [Trusted] [Stealth] [Default] [Aggressive] [Sci-Fi]
    """
    modes = ["trusted", "stealth", "default", "aggressive", "sci_fi"]

    images = []
    labels = []

    # Trusted (no veiling)
    images.append(depth_to_image(field))
    labels.append("Trusted")

    # Each veiled mode
    for mode in modes[1:]:
        veiled = apply_mode(field, mode)
        images.append(depth_to_image(veiled))
        pretty = mode.replace("_", "-").title()
        labels.append(pretty)

    # Normalize heights
    target_height = 200
    resized = []
    for img in images:
        resized_img = img.resize(
            (int(img.width * target_height / img.height), target_height),
            Image.Resampling.LANCZOS,
        )
        resized.append(resized_img)

    label_height = 40
    total_width = sum(img.width for img in resized)
    total_height = target_height + label_height

    strip = Image.new("RGB", (total_width, total_height), (0, 0, 0))
    draw = ImageDraw.Draw(strip)

    x = 0
    for img, label in zip(resized, labels):
        strip.paste(img, (x, label_height))
        draw.text((x + 10, 10), label, fill=(230, 230, 230))
        x += img.width

    out_path.parent.mkdir(parents=True, exist_ok=True)
    strip.save(out_path)


def demo_distortion_modes() -> None:
    """
    Generate a single trusted depth field and render it across multiple
    distortion modes for comparison.
    """
    depth_field = generate_depth_field()
    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    out_path = out_dir / "depth_distortion_modes.png"
    make_modes_strip(depth_field, out_path)

    print("✅ Distortion modes demo complete.")
    print(f"  - {out_path}")


if __name__ == "__main__":
    demo_distortion_modes()
