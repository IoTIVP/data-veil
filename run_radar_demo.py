"""
DATA VEIL – Radar (Range–Doppler) Deception Demo

Simulates a simple radar range–Doppler map (targets at different
ranges and relative velocities), then applies a veiled version that:

- injects ghost targets
- removes real targets
- adds structured noise

Trusted:
  - a few clean target blobs in range–velocity space

Veiled:
  - extra ghost blobs
  - some real targets erased or weakened
  - noise

Outputs:
  - examples/radar_trusted.png
  - examples/radar_veiled.png
  - examples/radar_trusted_vs_veiled.png
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw


def gaussian_blob(grid_x, grid_y, cx, cy, sx, sy, amplitude=1.0):
    """
    Create a 2D Gaussian blob centered at (cx, cy) with std devs (sx, sy).
    """
    return amplitude * np.exp(
        -(((grid_x - cx) ** 2) / (2 * sx ** 2) + ((grid_y - cy) ** 2) / (2 * sy ** 2))
    )


def generate_radar_map(
    range_bins: int = 64,
    velocity_bins: int = 32,
) -> np.ndarray:
    """
    Generate a synthetic radar range–Doppler map:
      rows    = range bins (near to far)
      columns = velocity bins (negative to positive)

    Returns a 2D array of "intensity" values in [0,1].
    """
    r = np.linspace(0, 1, range_bins)
    v = np.linspace(-1, 1, velocity_bins)
    grid_r, grid_v = np.meshgrid(r, v, indexing="ij")  # shape (range_bins, velocity_bins)

    # Base noise floor
    base = 0.05 * np.ones_like(grid_r)

    # Add a few clean targets (blobs)
    # Target 1: mid-range, slightly positive velocity
    base += gaussian_blob(grid_r, grid_v, cx=0.4, cy=0.3, sx=0.04, sy=0.12, amplitude=0.7)

    # Target 2: far range, negative velocity
    base += gaussian_blob(grid_r, grid_v, cx=0.8, cy=-0.4, sx=0.05, sy=0.08, amplitude=0.9)

    # Target 3: near range, zero-ish velocity
    base += gaussian_blob(grid_r, grid_v, cx=0.2, cy=0.0, sx=0.03, sy=0.10, amplitude=0.6)

    # Small random noise
    noise = np.random.normal(loc=0.0, scale=0.01, size=base.shape)
    out = np.clip(base + noise, 0.0, 1.0)

    return out


def apply_radar_veil(radar_map: np.ndarray) -> np.ndarray:
    """
    Veil the radar range–Doppler map:
      - inject ghost targets
      - remove or weaken some real targets
      - add stronger structured noise
    """
    veiled = radar_map.copy()
    rows, cols = veiled.shape

    # Add ghost blobs
    ghost_count = 3
    for _ in range(ghost_count):
        cx = np.random.uniform(0.1, 0.9)
        cy = np.random.uniform(-0.8, 0.8)
        sx = np.random.uniform(0.03, 0.09)
        sy = np.random.uniform(0.05, 0.15)
        amp = np.random.uniform(0.4, 0.9)

        r = np.linspace(0, 1, rows)
        v = np.linspace(-1, 1, cols)
        grid_r, grid_v = np.meshgrid(r, v, indexing="ij")
        veiled += gaussian_blob(grid_r, grid_v, cx=cx, cy=cy, sx=sx, sy=sy, amplitude=amp)

    # Remove/weaken some real targets by zeroing random patches
    patch_count = 4
    for _ in range(patch_count):
        r0 = np.random.randint(0, rows - 8)
        c0 = np.random.randint(0, cols - 6)
        r1 = min(rows, r0 + np.random.randint(4, 12))
        c1 = min(cols, c0 + np.random.randint(3, 8))
        veiled[r0:r1, c0:c1] *= 0.2  # strongly attenuate

    # Structured noise: mild ripple pattern + random noise
    ripple = 0.03 * np.sin(np.linspace(0, 4 * np.pi, rows))[:, None]
    veiled += ripple
    rand_noise = np.random.normal(loc=0.0, scale=0.03, size=veiled.shape)
    veiled += rand_noise

    veiled = np.clip(veiled, 0.0, 1.0)
    return veiled


def radar_to_image(
    radar_map: np.ndarray,
    tint: str = "trusted",
    scale: int = 4,
) -> Image.Image:
    """
    Convert a radar map in [0,1] to a tinted RGB image.

    tint:
      - "trusted": bluish
      - "veiled":  reddish
    """
    norm = np.clip(radar_map, 0.0, 1.0)
    gray = (norm * 255).astype(np.uint8)

    h, w = gray.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)

    if tint == "trusted":
        # bluish tint
        rgb[..., 0] = (gray * 0.6).astype(np.uint8)  # R
        rgb[..., 1] = (gray * 0.8).astype(np.uint8)  # G
        rgb[..., 2] = gray                           # B
    else:
        # veiled: reddish tint
        rgb[..., 0] = gray                           # R
        rgb[..., 1] = (gray * 0.5).astype(np.uint8)  # G
        rgb[..., 2] = (gray * 0.5).astype(np.uint8)  # B

    img = Image.fromarray(rgb, mode="RGB")

    if scale != 1:
        img = img.resize((w * scale, h * scale), Image.Resampling.NEAREST)

    return img


def make_radar_comparison(trusted_map: np.ndarray, veiled_map: np.ndarray, out_path: Path) -> None:
    """
    Build a side-by-side comparison image:
      LEFT  = trusted radar map
      RIGHT = veiled radar map
    """
    trusted_img = radar_to_image(trusted_map, tint="trusted", scale=4)
    veiled_img = radar_to_image(veiled_map, tint="veiled", scale=4)

    h = max(trusted_img.height, veiled_img.height)
    w_total = trusted_img.width + veiled_img.width
    label_height = 40

    combined = Image.new("RGB", (w_total, h + label_height), (0, 0, 0))
    draw = ImageDraw.Draw(combined)

    combined.paste(trusted_img, (0, label_height))
    combined.paste(veiled_img, (trusted_img.width, label_height))

    draw.text((10, 10), "Radar – Trusted", fill=(230, 230, 230))
    draw.text((trusted_img.width + 10, 10), "Radar – Veiled", fill=(230, 230, 230))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(out_path)


def demo_radar() -> None:
    """
    End-to-end radar deception demo.
    """
    trusted = generate_radar_map()
    veiled = apply_radar_veil(trusted)

    out_dir = Path("examples")
    out_dir.mkdir(exist_ok=True)

    trusted_path = out_dir / "radar_trusted.png"
    veiled_path = out_dir / "radar_veiled.png"
    combo_path = out_dir / "radar_trusted_vs_veiled.png"

    radar_to_image(trusted, tint="trusted", scale=4).save(trusted_path)
    radar_to_image(veiled, tint="veiled", scale=4).save(veiled_path)
    make_radar_comparison(trusted, veiled, combo_path)

    print("✅ Radar demo complete.")
    print(f"  - {trusted_path}")
    print(f"  - {veiled_path}")
    print(f"  - {combo_path}")


if __name__ == "__main__":
    demo_radar()
