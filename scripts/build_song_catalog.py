"""Create the curated, song-level mood catalog used by the Streamlit app."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "songs.json"


def tracks(*items: tuple[str, str, float, float]) -> list[dict]:
    return [
        {
            "title": title,
            "moods": moods.split(),
            "valence": valence,
            "energy": energy,
        }
        for title, moods, valence, energy in items
    ]


ALBUMS = [
    {
        "album": "emails i can't send fwd:",
        "artist": "Sabrina Carpenter",
        "edition": "deluxe",
        "tracks": tracks(
            ("emails i can't send", "vulnerable sad reflective family", 0.18, 0.24),
            ("Vicious", "angry bitter cathartic defiant", 0.24, 0.78),
            ("Read your Mind", "playful romantic confident energetic", 0.72, 0.72),
            ("Tornado Warnings", "anxious romantic bittersweet self-aware", 0.38, 0.56),
            ("because i liked a boy", "hurt angry vulnerable cathartic", 0.27, 0.72),
            ("Already Over", "conflicted romantic bittersweet restless", 0.42, 0.64),
            ("how many things", "heartbroken vulnerable longing reflective", 0.16, 0.28),
            ("bet u wanna", "flirty confident sensual playful", 0.70, 0.65),
            ("Nonsense", "flirty playful joyful energetic", 0.84, 0.76),
            ("Fast Times", "carefree playful impulsive energetic", 0.75, 0.78),
            ("skinny dipping", "nostalgic healing bittersweet hopeful", 0.52, 0.42),
            ("Bad for Business", "romantic playful conflicted dreamy", 0.64, 0.55),
            ("decode", "reflective vulnerable heartbroken healing", 0.30, 0.32),
            ("opposite", "insecure heartbroken jealous vulnerable", 0.19, 0.35),
            ("Feather", "confident liberated playful energetic", 0.86, 0.79),
            ("Lonesome", "lonely heartbroken bitter vulnerable", 0.14, 0.30),
            ("things i wish you said", "longing sad intimate reflective", 0.17, 0.25),
        ),
    },
    {
        "album": "folklore",
        "artist": "Taylor Swift",
        "edition": "standard",
        "tracks": tracks(
            ("the 1", "nostalgic bittersweet reflective calm", 0.48, 0.40),
            ("cardigan", "romantic nostalgic longing bittersweet", 0.38, 0.42),
            ("the last great american dynasty", "storytelling playful defiant energetic", 0.63, 0.62),
            ("exile", "heartbroken sad dramatic longing", 0.12, 0.38),
            ("my tears ricochet", "grief dark heartbroken cathartic", 0.10, 0.45),
            ("mirrorball", "anxious vulnerable dreamy reflective", 0.35, 0.43),
            ("seven", "nostalgic tender dreamy childhood", 0.55, 0.34),
            ("august", "nostalgic romantic longing bittersweet", 0.48, 0.62),
            ("this is me trying", "sad vulnerable anxious healing", 0.22, 0.33),
            ("illicit affairs", "secretive romantic guilty heartbroken", 0.23, 0.40),
            ("invisible string", "romantic hopeful warm calm", 0.78, 0.43),
            ("mad woman", "angry dark defiant cathartic", 0.20, 0.58),
            ("epiphany", "grief calm reflective solemn", 0.12, 0.20),
            ("betty", "regretful romantic hopeful nostalgic", 0.58, 0.58),
            ("peace", "romantic anxious intimate vulnerable", 0.38, 0.31),
            ("hoax", "devastated dark heartbroken calm", 0.08, 0.20),
        ),
    },
    {
        "album": "evermore",
        "artist": "Taylor Swift",
        "edition": "standard",
        "tracks": tracks(
            ("willow", "romantic dreamy warm mysterious", 0.68, 0.48),
            ("champagne problems", "heartbroken regretful reflective sad", 0.14, 0.30),
            ("gold rush", "jealous dreamy romantic anxious", 0.46, 0.58),
            ("'tis the damn season", "nostalgic bittersweet romantic longing", 0.38, 0.48),
            ("tolerate it", "heartbroken lonely vulnerable dark", 0.10, 0.27),
            ("no body, no crime", "dark angry storytelling energetic", 0.30, 0.65),
            ("happiness", "healing bittersweet grief reflective", 0.37, 0.28),
            ("dorothea", "nostalgic warm hopeful affectionate", 0.67, 0.46),
            ("coney island", "sad nostalgic regretful distant", 0.17, 0.31),
            ("ivy", "romantic secretive dreamy intense", 0.57, 0.57),
            ("cowboy like me", "romantic guarded dreamy storytelling", 0.48, 0.38),
            ("long story short", "healing confident hopeful energetic", 0.73, 0.68),
            ("marjorie", "grief nostalgic tender reflective", 0.28, 0.36),
            ("closure", "bitter defiant restless cathartic", 0.30, 0.62),
            ("evermore", "depressed reflective healing hopeful", 0.24, 0.30),
        ),
    },
    {
        "album": "eternal sunshine",
        "artist": "Ariana Grande",
        "edition": "standard",
        "tracks": tracks(
            ("intro (end of the world)", "anxious romantic reflective vulnerable", 0.38, 0.28),
            ("bye", "confident liberated bittersweet energetic", 0.70, 0.72),
            ("don't wanna break up again", "conflicted romantic tired bittersweet", 0.40, 0.58),
            ("Saturn Returns Interlude", "reflective transition calm", 0.50, 0.16),
            ("eternal sunshine", "betrayed reflective heartbroken healing", 0.28, 0.54),
            ("supernatural", "romantic dreamy sensual joyful", 0.79, 0.70),
            ("true story", "defiant bitter confident dramatic", 0.38, 0.70),
            ("the boy is mine", "flirty sensual jealous confident", 0.68, 0.74),
            ("yes, and?", "confident defiant liberated energetic", 0.78, 0.82),
            ("we can't be friends (wait for your love)", "heartbroken longing bittersweet cathartic", 0.31, 0.65),
            ("i wish i hated you", "heartbroken tender vulnerable longing", 0.15, 0.25),
            ("imperfect for you", "romantic healing vulnerable warm", 0.70, 0.45),
            ("ordinary things", "romantic grateful calm hopeful", 0.78, 0.40),
        ),
    },
    {
        "album": "Solar Power",
        "artist": "Lorde",
        "edition": "standard",
        "tracks": tracks(
            ("The Path", "reflective searching warm calm", 0.56, 0.48),
            ("Solar Power", "joyful carefree sunny playful", 0.90, 0.68),
            ("California", "nostalgic liberated bittersweet reflective", 0.55, 0.48),
            ("Stoned at the Nail Salon", "nostalgic anxious reflective calm", 0.38, 0.26),
            ("Fallen Fruit", "angry mournful dark environmental", 0.24, 0.52),
            ("Secrets from a Girl (Who's Seen It All)", "healing reassuring hopeful warm", 0.76, 0.60),
            ("The Man with the Axe", "romantic intimate calm reflective", 0.58, 0.28),
            ("Dominoes", "playful sarcastic breezy confident", 0.67, 0.50),
            ("Big Star", "grief tender loving calm", 0.30, 0.24),
            ("Leader of a New Regime", "uneasy reflective dark calm", 0.35, 0.27),
            ("Mood Ring", "playful ironic anxious energetic", 0.61, 0.64),
            ("Oceanic Feeling", "peaceful warm reflective hopeful", 0.75, 0.36),
        ),
    },
    {
        "album": "you seem pretty sad for a girl so in love",
        "artist": "Olivia Rodrigo",
        "edition": "standard",
        "tracks": tracks(
            ("drop dead", "romantic infatuated playful energetic", 0.83, 0.78),
            ("stupid song", "romantic obsessive joyful dramatic", 0.78, 0.70),
            ("honeybee", "romantic tender anxious warm", 0.64, 0.30),
            ("maggots for brains", "romantic obsessive dark longing", 0.52, 0.62),
            ("u + me = <3", "romantic joyful dreamy playful", 0.86, 0.67),
            ("my way", "jealous defiant playful energetic", 0.50, 0.80),
            ("purple", "romantic dreamy anxious conflicted", 0.52, 0.48),
            ("the cure", "heartbroken dramatic cathartic longing", 0.18, 0.74),
            ("begged", "pleading vulnerable heartbroken tender", 0.13, 0.27),
            ("what's wrong with me", "anxious dark vulnerable restless", 0.18, 0.57),
            ("less", "devastated heartbroken lonely calm", 0.07, 0.22),
            ("expectations", "confident liberated playful energetic", 0.72, 0.80),
            ("cigarette smoke", "heartbroken lonely reflective aftermath", 0.12, 0.30),
        ),
    },
    {
        "album": "HIT ME HARD AND SOFT",
        "artist": "Billie Eilish",
        "edition": "standard",
        "tracks": tracks(
            ("SKINNY", "vulnerable sad reflective intimate", 0.20, 0.24),
            ("LUNCH", "flirty sensual playful energetic", 0.78, 0.82),
            ("CHIHIRO", "dreamy anxious mysterious restless", 0.42, 0.70),
            ("BIRDS OF A FEATHER", "romantic joyful devoted energetic", 0.82, 0.74),
            ("WILDFLOWER", "guilty heartbroken jealous vulnerable", 0.16, 0.38),
            ("THE GREATEST", "heartbroken angry cathartic dramatic", 0.12, 0.72),
            ("L'AMOUR DE MA VIE", "bitter liberated cathartic energetic", 0.55, 0.74),
            ("THE DINER", "dark obsessive playful mysterious", 0.42, 0.68),
            ("BITTERSUITE", "dreamy romantic conflicted dark", 0.42, 0.64),
            ("BLUE", "sad reflective longing bittersweet", 0.20, 0.46),
        ),
    },
    {
        "album": "GUTS",
        "artist": "Olivia Rodrigo",
        "edition": "standard",
        "tracks": tracks(
            ("all-american bitch", "angry ironic cathartic energetic", 0.42, 0.90),
            ("bad idea right?", "impulsive playful romantic energetic", 0.69, 0.84),
            ("vampire", "betrayed angry heartbroken dramatic", 0.14, 0.72),
            ("lacy", "jealous insecure dreamy vulnerable", 0.28, 0.35),
            ("ballad of a homeschooled girl", "anxious awkward cathartic energetic", 0.40, 0.88),
            ("making the bed", "regretful sad reflective vulnerable", 0.22, 0.38),
            ("logical", "heartbroken confused vulnerable dramatic", 0.13, 0.40),
            ("get him back!", "angry playful conflicted energetic", 0.58, 0.90),
            ("love is embarrassing", "self-aware playful heartbroken energetic", 0.58, 0.84),
            ("the grudge", "heartbroken angry lingering vulnerable", 0.10, 0.36),
            ("pretty isn't pretty", "insecure anxious cathartic energetic", 0.34, 0.77),
            ("teenage dream", "anxious vulnerable reflective sad", 0.22, 0.36),
        ),
    },
    {
        "album": "five seconds flat",
        "artist": "Lizzy McAlpine",
        "edition": "standard",
        "tracks": tracks(
            ("doomsday", "heartbroken dark dramatic cathartic", 0.14, 0.62),
            ("an ego thing", "bitter conflicted reflective restrained", 0.32, 0.50),
            ("erase me", "heartbroken anxious dramatic longing", 0.16, 0.54),
            ("called you again", "regretful longing vulnerable sad", 0.18, 0.34),
            ("all my ghosts", "romantic nostalgic hopeful playful", 0.70, 0.57),
            ("reckless driving", "romantic anxious dramatic doomed", 0.34, 0.65),
            ("weird", "anxious dreamy intimate vulnerable", 0.37, 0.35),
            ("ceilings", "dreamy romantic longing heartbroken", 0.34, 0.48),
            ("what a shame", "bitter heartbroken restrained reflective", 0.22, 0.36),
            ("firearm", "angry betrayed cathartic energetic", 0.20, 0.66),
            ("hate to be lame", "romantic vulnerable hesitant warm", 0.58, 0.37),
            ("nobody likes a secret", "secretive anxious romantic intimate", 0.39, 0.30),
            ("chemtrails", "grief nostalgic tender reflective", 0.18, 0.24),
            ("orange show speedway", "nostalgic joyful romantic energetic", 0.78, 0.72),
        ),
    },
    {
        "album": "BRAT",
        "artist": "Charli xcx",
        "edition": "standard",
        "tracks": tracks(
            ("360", "confident playful energetic club", 0.78, 0.86),
            ("Club classics", "confident energetic euphoric club", 0.82, 0.94),
            ("Sympathy is a knife", "jealous anxious cathartic energetic", 0.36, 0.90),
            ("I might say something stupid", "insecure vulnerable lonely calm", 0.20, 0.28),
            ("Talk talk", "romantic flirty anxious energetic", 0.72, 0.84),
            ("Von dutch", "defiant confident aggressive energetic", 0.68, 0.95),
            ("Everything is romantic", "romantic dreamy euphoric energetic", 0.76, 0.88),
            ("Rewind", "nostalgic anxious vulnerable energetic", 0.42, 0.82),
            ("So I", "grief regretful tender reflective", 0.18, 0.38),
            ("Girl, so confusing", "insecure conflicted jealous energetic", 0.38, 0.80),
            ("Apple", "family conflicted playful reflective", 0.48, 0.76),
            ("B2b", "defiant heartbroken restless energetic", 0.43, 0.88),
            ("Mean girls", "confident dark playful energetic", 0.62, 0.82),
            ("I think about it all the time", "anxious reflective vulnerable intimate", 0.40, 0.52),
            ("365", "euphoric reckless confident club", 0.84, 0.98),
        ),
    },
    {
        "album": "Good Riddance",
        "artist": "Gracie Abrams",
        "edition": "standard",
        "tracks": tracks(
            ("Best", "regretful vulnerable heartbroken reflective", 0.20, 0.36),
            ("I know it won't work", "heartbroken longing restless bittersweet", 0.27, 0.57),
            ("Full machine", "romantic dependent vulnerable anxious", 0.34, 0.39),
            ("Where do we go now?", "confused heartbroken reflective restless", 0.28, 0.55),
            ("I should hate you", "heartbroken conflicted longing vulnerable", 0.17, 0.38),
            ("Will you cry?", "bitter heartbroken distant dark", 0.18, 0.44),
            ("Amelie", "dreamy nostalgic longing tender", 0.40, 0.28),
            ("Difficult", "anxious lonely vulnerable restless", 0.22, 0.52),
            ("This is what the drugs are for", "grief lonely reflective calm", 0.13, 0.26),
            ("Fault line", "romantic anxious dependent vulnerable", 0.32, 0.42),
            ("The blue", "romantic hopeful surprised warm", 0.72, 0.40),
            ("Right now", "reflective lonely healing bittersweet", 0.40, 0.31),
        ),
    },
]


def main() -> None:
    catalog = []
    for album in ALBUMS:
        for track_number, track in enumerate(album["tracks"], start=1):
            catalog.append(
                {
                    "title": track["title"],
                    "artist": album["artist"],
                    "album": album["album"],
                    "edition": album["edition"],
                    "track_number": track_number,
                    "moods": track["moods"],
                    "valence": track["valence"],
                    "energy": track["energy"],
                }
            )

    OUTPUT_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(catalog)} classified songs from {len(ALBUMS)} albums")


if __name__ == "__main__":
    main()
