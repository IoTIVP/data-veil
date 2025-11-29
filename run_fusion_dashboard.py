"""
DATA VEIL – Multi-Sensor Fusion Dashboard

Creates a single image showing all current sensor modes:

Row 1: Depth (trusted vs veiled)
Row 2: LiDAR (trusted vs veiled)
Row 3: Thermal (trusted vs veiled)
Row 4: RF (trusted vs veiled)

Output:
  - examples/fusion_dashboard.png
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


EXAMPLES_DIR = Path("examples")


def load_image(path: Path, fallback_color=(20, 20, 20)) -> Image.Image:
    """
    Try to load an image. If missing, create a placeholder.
    """
    if path.exists():
        return Image.open(path).convert("RGB")
    # Fallback placeholder
    img = Image.new("RGB", (256, 256), fallback_color)
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), f"Missing:\n{path.name}", fill=(200, 200, 200))
    return img


def make_pair(trusted_name: str, veiled_name: str, label: str, target_height=220) -> Image.Image:
    """
    Load trusted & veiled images and place them side-by-side with a row label.
    """
    trusted_path = EXAMPLES_DIR / trusted_name
    veiled_path = EXAMPLES_DIR / veiled_name

    img_trusted = load_image(trusted_path)
    img_veiled = load_image(veiled_path)

    # Normalize heights
    h_t = img_trusted.height
    h_v = img_veiled.height
    h = min(h_t, h_v, target_height)

    def resize_keep_aspect(img: Image.Image, h_target: int) -> Image.Image:
        return img.resize(
            (int(img.width * h_target / img.height), h_target),
            Image.Resampling.LANCZOS,
        )

    img_trusted = resize_keep_aspect(img_trusted, h)
    img_veiled = resize_keep_aspect(img_veiled, h)

    # Row height includes a small label band above
    label_height = 30
    row_height = h + label_height
    row_width = img_trusted.width + img_veiled.width

    row = Image.new("RGB", (row_width, row_height), (0, 0, 0))
    draw = ImageDraw.Draw(row)

    # Paste images
    row.paste(img_trusted, (0, label_height))
    row.paste(img_veiled, (img_trusted.width, label_height))

    # Labels
    draw.text((10, 5), f"{label} – trusted", fill=(230, 230, 230))
    draw.text(
        (img_trusted.width + 10, 5),
        f"{label} – veiled",
        fill=(230, 230, 230),
    )

    return row


def make_fusion_dashboard(out_path: Path) -> None:
    """
    Build the 4-row fusion dashboard.
    """
    # Each row: (trusted_filename, veiled_filename, label)
    rows_config = [
        ("trusted_depth.png", "veiled_depth.png", "Depth"),
        ("lidar_trusted.png", "lidar_veiled.png", "LiDAR"),
        ("thermal_trusted.png", "thermal_veiled.png", "Thermal / IR"),
        ("rf_trusted.png", "rf_veiled.png", "RF Field"),
    ]

    rows = [make_pair(t, v, label) for (t, v, label) in rows_config]

    # Normalize widths (pad with black if needed)
    max_width = max(row.width for row in rows)

    def pad_to_width(img: Image.Image, w: int) -> Image.Image:
        if img.width == w:
            return img
        padded = Image.new("RGB", (w, img.height), (0, 0, 0))
        padded.paste(img, (0, 0))
        return padded

    rows = [pad_to_width(r, max_width) for r in rows]

    total_height = sum(r.height for r in rows) + 60  # extra for global title
    dashboard = Image.new("RGB", (max_width, total_height), (0, 0, 0))
    draw = ImageDraw.Draw(dashboard)

    # Global title
    title = "Data Veil – Multi-Sensor Trusted vs Veiled Dashboard"
    draw.text((10, 10), title, fill=(250, 250, 250))

    y = 60
    for r in rows:
        dashboard.paste(r, (0, y))
        y += r.height

    out_path.parent.mkdir(exist_ok=True, parents=True)
    dashboard.save(out_path)


def main():
    out_path = EXAMPLES_DIR / "fusion_dashboard.png"
    make_fusion_dashboard(out_path)
    print("✅ Fusion dashboard created:")
    print(f"  - {out_path}")


if __name__ == "__main__":
    main()
