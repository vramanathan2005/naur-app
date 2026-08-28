"""Build labeled contact sheets for private local photo review."""

import argparse

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREVIEW_DIR = PROJECT_ROOT / "data" / "photo_thumbs"
DEFAULT_OUTPUT_DIR = Path("/private/tmp/neenaur_photo_review")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_PREVIEW_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--cols", type=int, default=5)
    parser.add_argument("--rows", type=int, default=4)
    parser.add_argument("--cell-width", type=int, default=260)
    parser.add_argument("--cell-height", type=int, default=220)
    parser.add_argument("--image-height", type=int, default=178)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    previews = sorted(args.input.glob("*.jpg"))
    font = ImageFont.load_default(size=15)

    page_size = args.cols * args.rows
    for sheet_index in range(0, len(previews), page_size):
        batch = previews[sheet_index : sheet_index + page_size]
        sheet = Image.new(
            "RGB",
            (args.cols * args.cell_width, args.rows * args.cell_height),
            "#f2eee8",
        )
        draw = ImageDraw.Draw(sheet)

        for offset, path in enumerate(batch):
            global_index = sheet_index + offset
            col = offset % args.cols
            row = offset // args.cols
            x = col * args.cell_width
            y = row * args.cell_height
            with Image.open(path) as image:
                thumb = ImageOps.contain(
                    image.convert("RGB"),
                    (args.cell_width - 12, args.image_height),
                )
            image_x = x + (args.cell_width - thumb.width) // 2
            image_y = y + 4
            sheet.paste(thumb, (image_x, image_y))
            label = path.stem
            draw.rectangle(
                (x, y + args.image_height + 5, x + args.cell_width, y + args.cell_height),
                fill="#f2eee8",
            )
            draw.text((x + 7, y + args.image_height + 12), label, fill="#282321", font=font)

        output = args.output / f"sheet-{sheet_index // page_size + 1}.jpg"
        sheet.save(output, quality=92)
        print(output)


if __name__ == "__main__":
    main()
