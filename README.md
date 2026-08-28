# A song for this moment

A Streamlit birthday gift that picks music and photos from a typed mood.

## Run it

```bash
cd /Users/varunramanathan/naur_app
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Keep that Terminal window open, then visit http://localhost:8501/.

## What works

- Free-form mood entry
- Responsive visual design
- 108 mood-based color palettes with green throughout
- Dallas-time birthday countdown that advances to the next age every year
- Real-photo retrieval using hue, saturation, and brightness features
- A manually reviewed photo pool where every selectable image includes Neenaur
- A 149-track song list with mood and energy labels
- Mood-based ranking among locally available full-song MP3 files
- Native in-page audio playback with the four-photo collage kept visible
- Local album artwork displayed in the selected-song card
- Song results, next-song controls, and match explanations
- A simple keyword-based mood label

## What is not finished

- More advanced photo and text matching
- Saved favorites

Local audio belongs in the album folders inside `data/audio/`. The app searches
every album folder automatically, so new MP3s only need to be dropped into the
matching folder.
Filename matching ignores punctuation and labels such as “Official Audio” and
“Lyric Video.”

Album covers live in `data/album_art/` and are mapped by album name in `app.py`.

## Rebuild song analysis

The website reads cached audio and lyric features from `data/song_profiles.json`.
To rebuild them after adding songs:

```bash
source .venv/bin/activate
python -m pip install -r requirements-analysis.txt
python scripts/analyze_song_profiles.py
```

The analyzer requests lyrics from LRCLIB, analyzes them in memory, and stores
only derived mood scores and a content hash. Use `--skip-lyrics` to rebuild the
local audio features without contacting LRCLIB.

If LRCLIB is unavailable, transcribe each MP3 directly with local Whisper.
The transcript is discarded after mood analysis:

```bash
python scripts/analyze_song_profiles.py --transcribe-local
```

Wordle guess validation uses the MIT-licensed `tabatkins/wordle-list` word list.
Its license is included at `data/wordle-list-LICENSE.txt`.

## Deploy on Streamlit Community Cloud

The repository includes the runtime audio, photo thumbnails, album art, song
profiles, and Wordle data. Local environments, analysis models, original photo
exports, generated outputs, and `.streamlit/secrets.toml` stay out of Git.

1. Push this repository to a private GitHub repository.
2. At https://share.streamlit.io/, create an app from the repository.
3. Select `app.py` as the entrypoint and Python 3.13 in Advanced settings.
4. Paste the local `.streamlit/secrets.toml` contents into the Streamlit Secrets
   field. Never commit that file.
5. Deploy the app.
