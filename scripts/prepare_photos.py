"""Create browser-friendly photo previews and lightweight visual features."""

from __future__ import annotations

import colorsys
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps, ImageStat
from pillow_heif import register_heif_opener


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "data" / "photos"
PREVIEW_DIR = PROJECT_ROOT / "data" / "photo_thumbs"
FEATURES_PATH = PROJECT_ROOT / "data" / "photo_features.json"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".heic"}
register_heif_opener()


def preview_name(source: Path) -> str:
    fingerprint = hashlib.sha1(source.name.encode("utf-8")).hexdigest()[:10]
    return f"{source.stem}-{fingerprint}.jpg"


def extract_features(path: Path) -> dict[str, float]:
    with Image.open(path) as image:
        sample = image.convert("RGB")
        sample.thumbnail((96, 96))
        red, green, blue = ImageStat.Stat(sample).mean

    hue, saturation, brightness = colorsys.rgb_to_hsv(
        red / 255,
        green / 255,
        blue / 255,
    )
    return {
        "hue": round(hue * 360, 3),
        "saturation": round(saturation, 4),
        "brightness": round(brightness, 4),
    }


def main() -> None:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    sources = sorted(
        path
        for path in SOURCE_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    features = []

    for index, source in enumerate(sources, start=1):
        preview = PREVIEW_DIR / preview_name(source)
        with Image.open(source) as image:
            rendered = ImageOps.exif_transpose(image).convert("RGB")
            rendered.thumbnail((1400, 1400))
            rendered.save(preview, format="JPEG", quality=82, optimize=True)

        features.append(
            {
                "source_name": source.name,
                "preview": preview.name,
                **extract_features(preview),
            }
        )
        print(f"[{index:02d}/{len(sources)}] {source.name}")

    FEATURES_PATH.write_text(json.dumps(features, indent=2) + "\n")
    print(f"Prepared {len(features)} photos in {PREVIEW_DIR}")


if __name__ == "__main__":
    main()
