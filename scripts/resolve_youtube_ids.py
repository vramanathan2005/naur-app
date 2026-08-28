"""Resolve catalog tracks to public YouTube video metadata without downloading media."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "songs.json"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127 Safari/537.36"
)


def first_video(query: str) -> dict[str, str] | None:
    """Return the first normal video result from a YouTube search page."""
    url = "https://www.youtube.com/results?search_query=" + quote_plus(query)
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en"})
    with urlopen(request, timeout=25) as response:
        page = response.read().decode("utf-8", errors="replace")

    # Each videoRenderer contains the id, visible title, and owner in a compact JSON block.
    renderers = re.findall(r'"videoRenderer":\{(.{0,9000}?)\}\}\},', page)
    for renderer in renderers:
        id_match = re.search(r'"videoId":"([A-Za-z0-9_-]{11})"', renderer)
        title_match = re.search(
            r'"title":\{"runs":\[\{"text":"((?:\\.|[^"\\])*)"', renderer
        )
        owner_match = re.search(
            r'"ownerText":\{"runs":\[\{"text":"((?:\\.|[^"\\])*)"', renderer
        )
        if id_match and title_match:
            return {
                "youtube_id": id_match.group(1),
                "youtube_title": json.loads(f'"{title_match.group(1)}"'),
                "youtube_channel": (
                    json.loads(f'"{owner_match.group(1)}"') if owner_match else ""
                ),
            }

    # Fallback for changes in renderer nesting: the first video id is still embeddable.
    id_match = re.search(r'"videoId":"([A-Za-z0-9_-]{11})"', page)
    if id_match:
        return {"youtube_id": id_match.group(1), "youtube_title": "", "youtube_channel": ""}
    return None


def main() -> None:
    songs = json.loads(CATALOG_PATH.read_text())
    resolved = 0
    for index, song in enumerate(songs, start=1):
        if song.get("youtube_id"):
            resolved += 1
            continue

        query = f'{song["artist"]} {song["title"]} official audio'
        try:
            result = first_video(query)
        except Exception as exc:  # Keep a partial catalog if YouTube throttles a request.
            print(f"[{index:03}/{len(songs)}] ERROR {query}: {exc}")
            time.sleep(1.5)
            continue

        if result:
            song.update(result)
            resolved += 1
            # Persist after every match so an interrupted metadata pass can resume.
            CATALOG_PATH.write_text(
                json.dumps(songs, indent=2, ensure_ascii=False) + "\n"
            )
            print(
                f'[{index:03}/{len(songs)}] {song["artist"]} — {song["title"]} '
                f'-> {result["youtube_id"]} ({result["youtube_channel"]})'
            )
        else:
            print(f"[{index:03}/{len(songs)}] NO RESULT {query}")
        time.sleep(0.18)

    CATALOG_PATH.write_text(json.dumps(songs, indent=2, ensure_ascii=False) + "\n")
    print(f"Resolved {resolved}/{len(songs)} tracks")


if __name__ == "__main__":
    main()
