"""
DATA VEIL v0.3 – Temporal Ghosting / Flicker Demo

This demo extends the depth-field engine into TIME:

- Generates a short sequence of trusted depth frames.
- Generates a veiled sequence with temporal anomalies:
  - ghost frames
  - flicker
  - sudden jumps
  - inconsistent warping

Outputs:
  - examples/temporal_trusted_strip.png
  - examples/temporal_veiled_strip.png
  - examples/temporal_trusted_vs_hacker.png
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

from run_demo import (
    generate_depth_field,
    apply_data_veil,
    depth_to_image,
)


# -------- 1. Trusted sequence generator -------- #

def generate_trusted_sequence(num_frames: int = 6) -> list[np.ndarray]:
    """
    Generate a short sequence of trusted depth fields.

    We simulate small, realistic changes over time:
      - slight noise
      - small shifts in objects
      - minor environment variation
    """
    base = generate_depth_field()
    h, w = base.shape

    frames: list[np.ndarray] = []
    for i in range(num_frames):
        # Small temporal variation
        noise = np.random.normal(loc=0.0, scale=0.02, size=(h, w))
        frame = base + noise

        # Optional small "drift" of one of the blobs (simulated by translation)
        shift_x = int((i - num_frames // 2) * 0.5)
        shift_y = int((i - num_frames // 2) * 0.3)

        yy, xx = np.mgrid[0:h, 0:w]
        sx = np.clip(xx - shift_x, 0, w - 1)
        sy = np.clip(yy - shift_y, 0, h - 1)
        frame = frame[sy, sx]

        frame = np.clip(frame, 0.0, 1.0)
        frames.append(frame)

    return frames


# -------- 2. Veiled sequence with temporal anomalies -------- #

def generate_veiled_sequence(trusted_frames: list[np.ndarray]) -> list[np.ndarray]:
    """
    Apply Data Veil over time and inject temporal anomalies:

    We simulate:
      - ghost frames (reusing old frames)
      - flicker (extra-strong veil)
      - partial frame corruption
    """
    veiled_frames: list[np.ndarray] = []

    num_frames = len(trusted_frames)
    for i, frame in enumerate(trusted_frames):
        # Base veiling (spatial)
        veiled = apply_data_veil(frame)

        # Temporal anomalies:
        #  - every 3rd frame: extra corruption (hard veil)
        #  - sometimes reuse an earlier frame (ghost / time jump)
        if i % 3 == 2:
            # Stronger warp by re-veiling
            veiled = apply_data_veil(veiled)

        # Ghost frame: reuse frame 0 or previous frame occasionally
        if i in (num_frames - 2,):
            # Force a ghost frame from earlier in the sequence
            ghost_idx = max(0, i - 4)
            veiled = veiled_frames[ghost_idx]

        veiled_frames.append(veiled)

    return veiled_frames


# -------- 3. Sequence visualization -------- #

def sequence_to_strip(frames: list[np.ndarray], label: str) -> Image.Image:
    """
    Convert a sequence of depth frames to a horizontal strip image
    with a label at the top.
    """
    imgs = [depth_to_image(f) for f in frames]

    # Normalize heights
    height = min(img.height for img in imgs)
    resized = [
        img.resize(
            (int(img.width * height / img.height), height),
            Image.Resampling.LANCZOS,
        )
        for img in imgs
    ]

    total_width = sum(img.width for img in resized)
    label_height = 40

    strip = Image.new("RGB", (total_width, height + label_height), (0, 0, 0))

    x = 0
    for img in resized:
        strip.paste(img, (x, label_height))
        x += img.width

    draw = ImageDraw.Draw(strip)
    draw.text((20, 10), label, fill=(220, 220, 220))

    return strip


def make_temporal_side_by_side(
    trusted_frames: list[np.ndarray],
    veiled_frames: list[np.ndarray],
    out_path: str,
) -> None:
    """
    Create a 2-row comparison:

      Row 1 (top): Trusted sequence
      Row 2 (bottom): Veiled sequence
    """
    strip_trusted = sequence_to_strip(trusted_frames, "Trusted depth sequence")
    strip_veiled = sequence_to_strip(veiled_frames, "Veiled depth sequence")

    width = max(strip_trusted.width, strip_veiled.width)
    # Pad to same width
    def pad_to_width(img: Image.Image, w: int) -> Image.Image:
        if img.width == w:
            return img
        padded = Image.new("RGB", (w, img.height), (0, 0, 0))
        padded.paste(img, (0, 0))
        return padded

    strip_trusted = pad_to_width(strip_trusted, width)
    strip_veiled = pad_to_width(strip_veiled, width)

    total_height = strip_trusted.height + strip_veiled.height
    combined = Image.new("RGB", (width, total_height), (0, 0, 0))
    combined.paste(strip_trusted, (0, 0))
    combined.paste(strip_veiled, (0, strip_trusted.height))

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(out_path)


# -------- 4. DEMO ENTRY POINT -------- #

def demo_temporal() -> None:
    """
    End-to-end temporal ghosting demo:
      1. Generate a trusted sequence of depth frames.
      2. Generate a veiled sequence with temporal anomalies.
      3. Save:
         - temporal_trusted_strip.png
         - temporal_veiled_strip.png
         - temporal_trusted_vs_hacker.png
    """
    trusted_frames = generate_trusted_sequence(num_frames=6)
    veiled_frames = generate_veiled_sequence(trusted_frames)

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    strip_trusted = sequence_to_strip(trusted_frames, "Trusted depth sequence")
    strip_veiled = sequence_to_strip(veiled_frames, "Veiled depth sequence")

    strip_trusted.save(out_dir / "temporal_trusted_strip.png")
    strip_veiled.save(out_dir / "temporal_veiled_strip.png")

    make_temporal_side_by_side(
        trusted_frames,
        veiled_frames,
        out_dir / "temporal_trusted_vs_hacker.png",
    )

    print("✅ Temporal ghosting demo complete.")
    print(f"  - {out_dir / 'temporal_trusted_strip.png'}")
    print(f"  - {out_dir / 'temporal_veiled_strip.png'}")
    print(f"  - {out_dir / 'temporal_trusted_vs_hacker.png'}")


if __name__ == "__main__":
    demo_temporal()
