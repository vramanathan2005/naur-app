#!/usr/bin/env python3
"""Build cached audio and lyric profiles for the birthday song catalog.

Lyrics are requested from LRCLIB, analyzed in memory, and discarded. The output
contains only derived scores, a source id, and a hash used to detect changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import time
import warnings
from pathlib import Path

import librosa
import numpy as np
import requests


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "songs.json"
AUDIO_DIR = ROOT / "data" / "audio"
OUTPUT_PATH = ROOT / "data" / "song_profiles.json"
MODEL_CACHE_DIR = ROOT / "data" / "models"
WHISPER_CACHE_DIR = MODEL_CACHE_DIR / "whisper"
LRCLIB_URL = "https://lrclib.net/api/get"
USER_AGENT = "NaurBirthdaySongAnalyzer/1.0 (personal local birthday app)"

MOOD_PROTOTYPES = {
    "angry": "furious angry resentful confrontational and full of rage",
    "anxious": "anxious nervous worried overwhelmed uncertain and afraid",
    "bittersweet": "happy and sad at once, tender memories with an ache",
    "calm": "quiet peaceful relaxed gentle still and soothing",
    "cathartic": "an emotional release that lets pain and anger pour out",
    "confident": "self-assured powerful bold glamorous and in control",
    "dark": "ominous shadowy brooding heavy and emotionally dark",
    "defiant": "rebellious unapologetic resistant independent and fearless",
    "dreamy": "ethereal floating imaginative soft hazy and otherworldly",
    "energetic": "fast lively exciting kinetic upbeat and full of energy",
    "euphoric": "overwhelming joy celebration freedom and exhilaration",
    "healing": "recovering accepting growing forgiving and moving forward",
    "heartbroken": "devastated by lost love, betrayal, breakup and grief",
    "hopeful": "optimistic reassuring resilient and looking toward a better future",
    "insecure": "not feeling good enough, self-conscious and doubtful",
    "intimate": "private close vulnerable affectionate and emotionally near",
    "jealous": "envy possessiveness comparison suspicion and romantic jealousy",
    "joyful": "happy bright cheerful delighted sunny and celebratory",
    "liberated": "free independent relieved released and starting over",
    "lonely": "alone isolated empty abandoned and longing for company",
    "longing": "missing someone, yearning, wanting and unable to let go",
    "nostalgic": "remembering the past, childhood, home and old memories",
    "peaceful": "safe content grounded serene and at peace",
    "playful": "fun teasing witty flirty mischievous and lighthearted",
    "reflective": "thoughtful introspective observant and looking inward",
    "restless": "unable to settle, tense impatient agitated and on edge",
    "romantic": "falling in love, affection, devotion, desire and butterflies",
    "sad": "unhappy tearful blue depressed grieving and emotionally hurt",
    "vulnerable": "emotionally exposed honest fragile tender and unguarded",
    "warm": "cozy affectionate comforting close soft and reassuring",
}

POSITIVE_MOODS = {"confident", "euphoric", "healing", "hopeful", "joyful", "liberated", "peaceful", "playful", "romantic", "warm"}
NEGATIVE_MOODS = {"angry", "anxious", "dark", "heartbroken", "insecure", "jealous", "lonely", "sad"}
HIGH_AROUSAL_MOODS = {"angry", "cathartic", "confident", "defiant", "energetic", "euphoric", "jealous", "playful"}
LOW_AROUSAL_MOODS = {"calm", "dark", "dreamy", "intimate", "lonely", "peaceful", "reflective", "sad", "vulnerable", "warm"}


def clamp(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 4)


def normalize_name(value: str) -> str:
    value = value.lower()
    value = re.sub(r"\[[^]]+\]", " ", value)
    value = re.sub(r"\([^)]*(?:official|audio|lyric|video|visuali[sz]er)[^)]*\)", " ", value)
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def song_key(song: dict) -> str:
    return f"{normalize_name(song['artist'])}|{normalize_name(song['title'])}"


def find_audio(song: dict) -> Path | None:
    album_dir = AUDIO_DIR / song["album"]
    if not album_dir.exists():
        album_key = normalize_name(song["album"])
        album_dir = next((p for p in AUDIO_DIR.iterdir() if p.is_dir() and normalize_name(p.name) == album_key), album_dir)
    title = normalize_name(song["title"])
    pattern = re.compile(rf"(^| ){re.escape(title)}( |$)")
    matches = [p for p in album_dir.glob("*.mp3") if pattern.search(normalize_name(p.stem))]
    return min(matches, key=lambda p: len(normalize_name(p.stem))) if matches else None


def audio_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def decode_audio(path: Path, duration: float, sample_rate: int = 22050) -> np.ndarray:
    sample_length = min(55.0, max(30.0, duration * 0.45))
    start = max(0.0, (duration - sample_length) / 2)
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", str(path), "-t", f"{sample_length:.3f}", "-ac", "1", "-ar", str(sample_rate), "-f", "f32le", "pipe:1"],
        check=True,
        capture_output=True,
    )
    return np.frombuffer(result.stdout, dtype="<f4").copy()


def analyze_audio(path: Path) -> dict:
    sample_rate = 22050
    duration = audio_duration(path)
    samples = decode_audio(path, duration, sample_rate)
    if samples.size < sample_rate:
        raise ValueError("decoded audio is too short")

    rms = librosa.feature.rms(y=samples)[0]
    onset = librosa.onset.onset_strength(y=samples, sr=sample_rate)
    tempo = float(np.asarray(librosa.feature.tempo(onset_envelope=onset, sr=sample_rate)).flat[0])
    centroid = librosa.feature.spectral_centroid(y=samples, sr=sample_rate)[0]
    bandwidth = librosa.feature.spectral_bandwidth(y=samples, sr=sample_rate)[0]
    rolloff = librosa.feature.spectral_rolloff(y=samples, sr=sample_rate, roll_percent=0.85)[0]
    flatness = librosa.feature.spectral_flatness(y=samples)[0]
    zcr = librosa.feature.zero_crossing_rate(samples)[0]
    chroma = librosa.feature.chroma_stft(y=samples, sr=sample_rate)

    rms_db = float(librosa.amplitude_to_db(np.array([max(float(np.mean(rms)), 1e-8)]), ref=1.0)[0])
    beat_strength = float(np.mean(onset) / (np.std(onset) + 1e-6))
    brightness = clamp(float(np.mean(centroid)) / 4200)
    noisiness = clamp(float(np.mean(flatness)) * 5.5)
    dynamic_range = clamp(float(np.percentile(rms, 95) - np.percentile(rms, 10)) * 12)
    tempo_energy = clamp((tempo - 65) / 105)
    loudness = clamp((rms_db + 32) / 25)
    energy = clamp(0.42 * loudness + 0.32 * tempo_energy + 0.16 * clamp(beat_strength / 2.4) + 0.10 * dynamic_range)
    danceability = clamp(0.48 * math.exp(-((tempo - 118) / 48) ** 2) + 0.34 * clamp(beat_strength / 2.2) + 0.18 * (1 - noisiness))
    acousticness = clamp(0.48 * (1 - brightness) + 0.32 * (1 - noisiness) + 0.20 * (1 - loudness))
    audio_valence = clamp(0.18 + 0.30 * brightness + 0.28 * tempo_energy + 0.24 * danceability)

    return {
        "duration_seconds": round(duration, 3),
        "sample_seconds": round(len(samples) / sample_rate, 3),
        "tempo_bpm": round(tempo, 2),
        "rms_db": round(rms_db, 3),
        "energy": energy,
        "audio_valence": audio_valence,
        "danceability": danceability,
        "brightness": brightness,
        "acousticness": acousticness,
        "dynamic_range": dynamic_range,
        "spectral_centroid_hz": round(float(np.mean(centroid)), 2),
        "spectral_bandwidth_hz": round(float(np.mean(bandwidth)), 2),
        "spectral_rolloff_hz": round(float(np.mean(rolloff)), 2),
        "zero_crossing_rate": round(float(np.mean(zcr)), 5),
        "chroma": [round(float(value), 4) for value in np.mean(chroma, axis=1)],
    }


def fetch_lyrics(song: dict, duration: float, *, verify_tls: bool) -> dict | None:
    response = requests.get(
        LRCLIB_URL,
        params={
            "track_name": song["title"],
            "artist_name": song["artist"],
            "album_name": song["album"],
            "duration": round(duration),
        },
        headers={"User-Agent": USER_AGENT},
        timeout=25,
        verify=verify_tls,
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    result = response.json()
    return result if result.get("plainLyrics") else None


def lyric_chunks(lyrics: str, words_per_chunk: int = 180) -> list[str]:
    lines = [re.sub(r"\s+", " ", line).strip() for line in lyrics.splitlines()]
    lines = [line for line in lines if line and not re.fullmatch(r"\[[^]]+\]", line)]
    words = " ".join(lines).split()
    return [" ".join(words[i : i + words_per_chunk]) for i in range(0, len(words), words_per_chunk)]


def load_embedding_model():
    os.environ.setdefault("HF_HOME", str(MODEL_CACHE_DIR))
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer

    MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        cache_folder=str(MODEL_CACHE_DIR),
        local_files_only=True,
    )


def analyze_lyrics(lyrics: str, model) -> dict:
    chunks = lyric_chunks(lyrics)
    if not chunks:
        raise ValueError("lyrics contain no analyzable text")
    mood_names = list(MOOD_PROTOTYPES)
    prototype_vectors = model.encode(
        [MOOD_PROTOTYPES[name] for name in mood_names],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    chunk_vectors = model.encode(chunks, normalize_embeddings=True, show_progress_bar=False)
    similarities = np.asarray(chunk_vectors) @ np.asarray(prototype_vectors).T
    raw = 0.65 * similarities.max(axis=0) + 0.35 * similarities.mean(axis=0)
    low, high = float(raw.min()), float(raw.max())
    scaled = (raw - low) / max(1e-6, high - low)
    mood_scores = {name: round(float(score), 4) for name, score in zip(mood_names, scaled)}
    top_moods = sorted(mood_scores, key=mood_scores.get, reverse=True)[:8]
    positive = float(np.mean([mood_scores[name] for name in POSITIVE_MOODS]))
    negative = float(np.mean([mood_scores[name] for name in NEGATIVE_MOODS]))
    high_arousal = float(np.mean([mood_scores[name] for name in HIGH_AROUSAL_MOODS]))
    low_arousal = float(np.mean([mood_scores[name] for name in LOW_AROUSAL_MOODS]))
    valence = clamp(0.5 + 0.55 * (positive - negative))
    lyrical_energy = clamp(0.5 + 0.55 * (high_arousal - low_arousal))
    return {
        "word_count": len(re.findall(r"[A-Za-z']+", lyrics)),
        "chunk_count": len(chunks),
        "mood_scores": mood_scores,
        "top_moods": top_moods,
        "valence": valence,
        "energy": lyrical_energy,
    }


def load_whisper_model(model_name: str):
    import whisper

    WHISPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return whisper.load_model(model_name, download_root=str(WHISPER_CACHE_DIR))


def transcribe_local_song(audio_path: Path, model) -> tuple[str, dict]:
    """Transcribe the MP3 directly without retaining transcript text."""
    result = model.transcribe(
        str(audio_path),
        language="en",
        task="transcribe",
        fp16=False,
        temperature=0,
        condition_on_previous_text=True,
        verbose=None,
    )
    transcript = re.sub(r"\s+", " ", str(result.get("text", ""))).strip()
    segments = result.get("segments", [])
    quality = {
        "segment_count": len(segments),
        "word_count": len(re.findall(r"[A-Za-z']+", transcript)),
        "average_log_probability": round(
            float(np.mean([segment.get("avg_logprob", -1.0) for segment in segments])), 4
        ) if segments else None,
        "average_no_speech_probability": round(
            float(np.mean([segment.get("no_speech_prob", 1.0) for segment in segments])), 4
        ) if segments else None,
    }
    return transcript, quality


def fallback_mood_scores(song: dict, audio: dict) -> dict[str, float]:
    scores = {name: 0.08 for name in MOOD_PROTOTYPES}
    for mood in song.get("moods", []):
        if mood in scores:
            scores[mood] = 0.86
    scores["energetic"] = max(scores["energetic"], audio["energy"])
    scores["calm"] = max(scores["calm"], 1 - audio["energy"])
    scores["playful"] = max(scores["playful"], audio["danceability"] * 0.8)
    scores["warm"] = max(scores["warm"], audio["acousticness"] * 0.7)
    return {name: round(value, 4) for name, value in scores.items()}


def save_profiles(profiles: dict) -> None:
    payload = {
        "version": 1,
        "method": "all-MiniLM-L6-v2 lyric embeddings plus librosa audio features",
        "profiles": profiles,
    }
    temporary = OUTPUT_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT_PATH)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-lyrics", action="store_true", help="analyze audio without contacting LRCLIB")
    parser.add_argument("--transcribe-local", action="store_true", help="derive lyrics locally from each MP3 with Whisper")
    parser.add_argument("--whisper-model", default="base.en", help="Whisper model used by --transcribe-local")
    parser.add_argument("--limit", type=int, help="process only the first N catalog songs")
    parser.add_argument("--insecure-lrclib", action="store_true", help="disable TLS verification only when the local clock breaks certificate validation")
    parser.add_argument("--force", action="store_true", help="rebuild existing profiles")
    args = parser.parse_args()

    if args.insecure_lrclib:
        warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if OUTPUT_PATH.exists():
        profiles = json.loads(OUTPUT_PATH.read_text(encoding="utf-8")).get("profiles", {})
    else:
        profiles = {}
    embedding_model = None
    whisper_model = None

    selected_catalog = catalog[: args.limit] if args.limit else catalog
    for index, song in enumerate(selected_catalog, start=1):
        key = song_key(song)
        existing = profiles.get(key)
        if existing and not args.force and (
            args.skip_lyrics
            or (existing.get("lyrics") and not args.transcribe_local)
            or (
                args.transcribe_local
                and (existing.get("lyric_source") or {}).get("provider") == "local-whisper"
            )
        ):
            print(f"[{index:03}/{len(selected_catalog)}] cached  {song['artist']} - {song['title']}", flush=True)
            continue
        audio_path = find_audio(song)
        if not audio_path:
            print(f"[{index:03}/{len(catalog)}] missing audio  {song['artist']} - {song['title']}", flush=True)
            continue
        action = "lyrics" if existing and not args.force else "analyze"
        print(f"[{index:03}/{len(selected_catalog)}] {action} {song['artist']} - {song['title']}", flush=True)
        audio = existing["audio"] if existing and not args.force else analyze_audio(audio_path)
        lyric_result = None
        lyric_source = None
        if args.transcribe_local:
            try:
                if whisper_model is None:
                    whisper_model = load_whisper_model(args.whisper_model)
                transcript, transcription_quality = transcribe_local_song(audio_path, whisper_model)
                if transcription_quality["word_count"] >= 35:
                    if embedding_model is None:
                        embedding_model = load_embedding_model()
                    lyric_result = analyze_lyrics(transcript, embedding_model)
                    lyric_result["transcription_quality"] = transcription_quality
                    lyric_source = {
                        "provider": "local-whisper",
                        "model": args.whisper_model,
                        "content_sha256": hashlib.sha256(transcript.encode("utf-8")).hexdigest(),
                    }
                else:
                    lyric_source = {
                        "provider": "local-whisper",
                        "model": args.whisper_model,
                        "accepted": False,
                        "quality": transcription_quality,
                        "content_sha256": hashlib.sha256(transcript.encode("utf-8")).hexdigest(),
                    }
                    print(
                        "    transcript rejected: "
                        f"only {transcription_quality['word_count']} recognized words",
                        flush=True,
                    )
                del transcript
            except Exception as exc:
                print(f"    local transcription unavailable: {exc}", flush=True)
        elif not args.skip_lyrics:
            try:
                fetched = fetch_lyrics(song, audio["duration_seconds"], verify_tls=not args.insecure_lrclib)
                if fetched:
                    if embedding_model is None:
                        embedding_model = load_embedding_model()
                    lyrics = fetched["plainLyrics"]
                    lyric_result = analyze_lyrics(lyrics, embedding_model)
                    lyric_source = {
                        "provider": "LRCLIB",
                        "id": fetched.get("id"),
                        "matched_title": fetched.get("trackName"),
                        "matched_artist": fetched.get("artistName"),
                        "content_sha256": hashlib.sha256(lyrics.encode("utf-8")).hexdigest(),
                    }
            except requests.RequestException as exc:
                print(f"    lyric lookup unavailable: {exc}", flush=True)

        mood_scores = lyric_result["mood_scores"] if lyric_result else fallback_mood_scores(song, audio)
        top_moods = sorted(mood_scores, key=mood_scores.get, reverse=True)[:8]
        if lyric_result:
            valence = clamp(0.68 * lyric_result["valence"] + 0.32 * audio["audio_valence"])
            energy = clamp(0.72 * audio["energy"] + 0.28 * lyric_result["energy"])
        else:
            valence = clamp(0.58 * float(song["valence"]) + 0.42 * audio["audio_valence"])
            energy = clamp(0.68 * audio["energy"] + 0.32 * float(song["energy"]))
        profiles[key] = {
            "title": song["title"],
            "artist": song["artist"],
            "album": song["album"],
            "audio_file": str(audio_path.relative_to(ROOT)),
            "audio": audio,
            "lyrics": lyric_result,
            "lyric_source": lyric_source,
            "mood_scores": mood_scores,
            "top_moods": top_moods,
            "valence": valence,
            "energy": energy,
        }
        save_profiles(profiles)
        if not args.skip_lyrics:
            time.sleep(0.35)

    print(f"Saved {len(profiles)} profiles to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
