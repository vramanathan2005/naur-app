"""Crop iCloud's viewer chrome from sequential browser captures."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "work" / "icloud_032CGJZh2LxT0bNa17YzmCJ2w"
OUTPUT_DIR = PROJECT_ROOT / "data" / "photo_thumbs_icloud"


def photo_bounds(image: Image.Image) -> tuple[int, int, int, int]:
    """Find the centered photo rectangle inside the fixed iCloud viewer."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    top = 88
    bottom = min(660, height)
    background = rgb.getpixel((10, min(200, height - 1)))
    sample_rows = range(top, bottom, 4)

    scores: list[float] = []
    for x in range(width):
        changed = 0
        for y in sample_rows:
            pixel = rgb.getpixel((x, y))
            distance = sum(abs(pixel[channel] - background[channel]) for channel in range(3))
            if distance > 36:
                changed += 1
        scores.append(changed / len(sample_rows))

    active = [score > 0.18 for score in scores]
    center = width // 2
    if not active[center]:
        raise ValueError("Could not locate the centered photo")

    left = center
    while left > 0 and active[left - 1]:
        left -= 1
    right = center
    while right + 1 < width and active[right + 1]:
        right += 1

    return left, top, right + 1, bottom


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = sorted(SOURCE_DIR.glob("screen_*.png"))
    for index, source in enumerate(sources, start=1):
        target = OUTPUT_DIR / f"icloud_{index:04d}.jpg"
        if target.exists():
            continue
        with Image.open(source) as image:
            try:
                bounds = photo_bounds(image)
            except ValueError:
                print(f"[{index:03d}/{len(sources)}] skipped {source.name} (no still image)")
                continue
            crop = image.crop(bounds).convert("RGB")
            crop.save(target, format="JPEG", quality=88, optimize=True)
        print(f"[{index:03d}/{len(sources)}] {target.name}")

    print(f"Cropped {len(sources)} photos into {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
