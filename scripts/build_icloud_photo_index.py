"""Build the mood index for the reviewed iCloud Link collection."""

from __future__ import annotations

import json
from pathlib import Path

from prepare_photos import extract_features


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PREVIEW_DIR = PROJECT_ROOT / "data" / "photo_thumbs_icloud"
FEATURES_PATH = PROJECT_ROOT / "data" / "photo_features_icloud.json"

# Manual contact-sheet review: every selectable frame must visibly include
# Neenaur. Exclude guy-only, food-only, scenery/object-only, and unclear frames.
# Item 362 is an unrendered video frame.
EXCLUDED_IDS = {
    10, 11, 29, 30,
    12, 13, 14, 15, 16, 19, 20, 31,
    45, 46, 47, 76, 77, 78, 79, 80,
    81, 82, 83,
    106, 117, 118, 119, 120,
    133, 134, 148, 149, 150, 151, 152, 153, 154, 155,
    168, 175, 176,
    180, 181, 184, 185,
    211, 212, 219, 224, 225, 226, 229, 230, 231, 232, 233,
    238, 239, 240, 241, 247, 248, 249, 250,
    273, 274, 275, 280, 282, 291, 314,
    322, 323, 324, 333, 334, 346,
    340, 362, 372, 375, 376, 377,
}


def main() -> None:
    features = []
    for path in sorted(PREVIEW_DIR.glob("icloud_*.jpg")):
        item_id = int(path.stem.rsplit("_", 1)[1])
        if item_id in EXCLUDED_IDS:
            continue
        features.append(
            {
                "source_name": path.name,
                "preview": path.name,
                **extract_features(path),
            }
        )

    FEATURES_PATH.write_text(json.dumps(features, indent=2) + "\n")
    print(f"Indexed {len(features)} approved photos; excluded {len(EXCLUDED_IDS)} items")


if __name__ == "__main__":
    main()
