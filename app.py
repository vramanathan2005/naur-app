import base64
import hashlib
import hmac
import html
import json
import random
import re
import time
from datetime import date, datetime, time as datetime_time
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st


PASSWORD_COMPONENT = st.components.v1.declare_component(
    "naur_password_gate",
    path=str(Path(__file__).parent / "components" / "password_gate"),
)
AUDIO_PLAYER_COMPONENT = st.components.v1.declare_component(
    "naur_audio_player",
    path=str(Path(__file__).parent / "components" / "audio_player"),
)
DEPLOYMENT_PASSWORD_HASH = (
    "03b5d69347d29b617bd372db3db7b65bfe97115006d7d0d06515277ff2ce9712"
)


st.set_page_config(
    page_title="A song for this moment",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def require_password() -> None:
    """Stop before loading the app until the visitor enters its password."""
    if st.session_state.get("app_authenticated"):
        return

    expected_hash = str(
        st.secrets.get("APP_PASSWORD_SHA256", DEPLOYMENT_PASSWORD_HASH)
    )
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 18% 12%, rgba(143, 202, 158, .46), transparent 28rem),
                radial-gradient(circle at 86% 82%, rgba(207, 231, 175, .48), transparent 30rem),
                linear-gradient(145deg, #f4f8ef, #dfece2);
        }
        [data-testid="stHeader"], [data-testid="stToolbar"] { display: none; }
        [data-testid="stMainBlockContainer"] {
            max-width: 700px;
            padding-top: 16vh;
        }
        .password-kicker {
            color: #587261;
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: .18em;
            text-transform: uppercase;
        }
        .password-title {
            color: #2f352f;
            font-family: Georgia, serif;
            font-size: clamp(3rem, 7.6vw, 5.8rem);
            line-height: .92;
            margin: .55rem 0 1.25rem;
            transform: scaleX(1.075);
            transform-origin: left center;
            width: 93%;
        }
        .st-key-password_submission { display: none; }
        iframe[title="streamlit_component"], iframe[title="st.iframe"] { border: 0; }
        </style>
        <div class="password-kicker">for Naur only</div>
        <div class="password-title">you know the password.</div>
        """,
        unsafe_allow_html=True,
    )

    component_result = PASSWORD_COMPONENT(key="naur_password_component", default=None)

    with st.container(key="password_submission"):
        with st.form("password_form"):
            password = st.text_input(
                "Password",
                type="password",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Enter")

    component_password = (
        component_result.get("password")
        if isinstance(component_result, dict)
        else None
    )
    entered_password = component_password if component_password is not None else (
        password if submitted else None
    )
    if entered_password is not None:
        entered_hash = hashlib.sha256(entered_password.encode("utf-8")).hexdigest()
        if expected_hash and hmac.compare_digest(entered_hash, expected_hash):
            st.session_state.app_authenticated = True
            st.rerun()
        st.error("That password isn't right.")
    st.stop()


require_password()


BIRTH_DATE = date(2005, 8, 31)
DISPLAY_TIMEZONE = ZoneInfo("America/Chicago")
PHOTO_PREVIEW_DIR = Path(__file__).parent / "data" / "photo_thumbs_icloud"
PHOTO_FEATURES_PATH = Path(__file__).parent / "data" / "photo_features_icloud.json"
PHOTO_COLLECTION_VERSION = "icloud-032CGJZh2LxT0bNa17YzmCJ2w-girl-only-v2"
SONG_CATALOG_PATH = Path(__file__).parent / "data" / "songs.json"
SONG_CATALOG_VERSION = "curated-albums-youtube-v2"
SONG_PROFILES_PATH = Path(__file__).parent / "data" / "song_profiles.json"
AUDIO_DIR = Path(__file__).parent / "data" / "audio"
AUDIO_COLLECTION_VERSION = "album-folders-v2"
WORDLE_ALLOWED_WORDS_PATH = (
    Path(__file__).parent / "data" / "wordle_allowed_words.txt"
)
ALBUM_ART_PATHS = {
    "emails i can't send fwd:": (
        Path(__file__).parent / "data" / "album_art" / "emails_i_cant_send_fwd.jpg"
    ),
    "folklore": Path(__file__).parent / "data" / "album_art" / "folklore.png",
    "evermore": Path(__file__).parent / "data" / "album_art" / "evermore.jpeg",
    "eternal sunshine": Path(__file__).parent / "data" / "album_art" / "eternal_sunshine.png",
    "Solar Power": Path(__file__).parent / "data" / "album_art" / "solar_power.jpeg",
    "you seem pretty sad for a girl so in love": (
        Path(__file__).parent
        / "data"
        / "album_art"
        / "you_seem_pretty_sad_for_a_girl_so_in_love.png"
    ),
    "HIT ME HARD AND SOFT": (
        Path(__file__).parent / "data" / "album_art" / "hit_me_hard_and_soft.jpeg"
    ),
    "GUTS": Path(__file__).parent / "data" / "album_art" / "guts.png",
    "five seconds flat": (
        Path(__file__).parent / "data" / "album_art" / "five_seconds_flat.jpeg"
    ),
    "BRAT": Path(__file__).parent / "data" / "album_art" / "brat.png",
    "Good Riddance": (
        Path(__file__).parent / "data" / "album_art" / "good_riddance.jpeg"
    ),
}
WORDLE_WORDS = (
    "HAPPY",
    "GREEN",
    "MUSIC",
    "SMILE",
    "PARTY",
    "SWEET",
    "DREAM",
    "LAUGH",
    "DANCE",
    "HEART",
    "SUNNY",
    "MAGIC",
    "CAKES",
    "GIFTS",
    "CHEER",
    "PHOTO",
    "LOVED",
    "BRAVE",
    "LIGHT",
    "BLOOM",
    "NAURA",
)


@st.cache_data
def load_wordle_allowed_words() -> set[str]:
    """Load the local list of guesses accepted by Wordle."""
    words = {
        word.strip().upper()
        for word in WORDLE_ALLOWED_WORDS_PATH.read_text(encoding="utf-8").splitlines()
        if len(word.strip()) == 5 and word.strip().isalpha()
    }
    words.update(WORDLE_WORDS)
    return words


def ordinal(number: int) -> str:
    """Format an integer with its English ordinal suffix."""
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def birthday_copy(today: date | None = None) -> tuple[str, str]:
    """Return the day-based annual birthday copy."""
    current_date = today or datetime.now(DISPLAY_TIMEZONE).date()
    this_year_birthday = date(current_date.year, BIRTH_DATE.month, BIRTH_DATE.day)

    if current_date == this_year_birthday:
        age = current_date.year - BIRTH_DATE.year
        return "Today is the day ✦", f"It's Neenaur's {ordinal(age)} Birthday!"

    if current_date < this_year_birthday:
        next_birthday = this_year_birthday
    else:
        next_birthday = date(current_date.year + 1, BIRTH_DATE.month, BIRTH_DATE.day)

    turning_age = next_birthday.year - BIRTH_DATE.year
    days_until = (next_birthday - current_date).days
    unit = "day" if days_until == 1 else "days"
    return (
        "A little something for Neenaur",
        f"{days_until} {unit} until Neenaur's {ordinal(turning_age)} Birthday",
    )


def birthday_display(
    now: datetime | None = None,
) -> tuple[str, str, datetime | None]:
    """Return birthday copy and a live-clock target during the final 24 hours."""
    current_time = now or datetime.now(DISPLAY_TIMEZONE)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=DISPLAY_TIMEZONE)
    else:
        current_time = current_time.astimezone(DISPLAY_TIMEZONE)

    current_date = current_time.date()
    eyebrow, title = birthday_copy(current_date)
    if current_date.month == BIRTH_DATE.month and current_date.day == BIRTH_DATE.day:
        return eyebrow, title, None

    birthday_year = current_date.year
    this_year_target = datetime.combine(
        date(birthday_year, BIRTH_DATE.month, BIRTH_DATE.day),
        datetime_time.min,
        tzinfo=DISPLAY_TIMEZONE,
    )
    if current_time >= this_year_target:
        birthday_year += 1
    target = datetime.combine(
        date(birthday_year, BIRTH_DATE.month, BIRTH_DATE.day),
        datetime_time.min,
        tzinfo=DISPLAY_TIMEZONE,
    )
    seconds_remaining = (target - current_time).total_seconds()
    if 0 < seconds_remaining <= 24 * 60 * 60:
        turning_age = birthday_year - BIRTH_DATE.year
        return eyebrow, f"until Neenaur's {ordinal(turning_age)} Birthday", target
    return eyebrow, title, None


def live_birthday_countdown(
    target: datetime,
    label: str,
    preview_seconds: int | None = None,
) -> None:
    """Render a Dallas-time countdown that hands back to the birthday page at zero."""
    target_expression = (
        f"Date.now() + {preview_seconds * 1000}"
        if preview_seconds is not None
        else str(round(target.timestamp() * 1000))
    )
    safe_label = json.dumps(label)
    st.iframe(
        f"""
        <style>
            html, body {{ background: transparent; margin: 0; overflow: hidden; }}
            #countdown {{
                color: #2f2a27;
                font-family: Georgia, "Times New Roman", serif;
                font-size: clamp(3.2rem, 8vw, 6.9rem);
                font-weight: 400;
                letter-spacing: -.065em;
                line-height: .89;
                padding: 0 0 .08em;
            }}
        </style>
        <div id="countdown"></div>
        <script>
            const target = {target_expression};
            const label = {safe_label};
            const output = document.getElementById("countdown");
            function updateCountdown() {{
                const remaining = target - Date.now();
                if (remaining <= 0) {{
                    output.textContent = `00:00 ${{label}}`;
                    window.parent.location.reload();
                    return;
                }}
                const totalMinutes = Math.floor(remaining / 60000);
                const hours = Math.floor(totalMinutes / 60).toString().padStart(2, "0");
                const minutes = (totalMinutes % 60).toString().padStart(2, "0");
                output.textContent = `${{hours}}:${{minutes}} ${{label}}`;
            }}
            updateCountdown();
            setInterval(updateCountdown, 1000);
        </script>
        """,
        height=190,
    )


def score_wordle_guess(guess: str, answer: str) -> list[str]:
    """Score a Wordle guess while handling duplicate letters correctly."""
    result = ["miss"] * 5
    remaining = list(answer)
    for index, letter in enumerate(guess):
        if letter == answer[index]:
            result[index] = "exact"
            remaining[index] = ""
    for index, letter in enumerate(guess):
        if result[index] == "exact":
            continue
        if letter in remaining:
            result[index] = "present"
            remaining[remaining.index(letter)] = ""
    return result


def analyze_wordle(guesses: list[str], answer: str) -> dict[str, object]:
    """Score clue use, efficiency, and how early the answer letters appeared."""
    green_positions: dict[int, str] = {}
    known_present: set[str] = set()
    known_absent: set[str] = set()
    clue_violations = 0
    gray_reuses = 0
    first_guess_variety = len(set(guesses[0])) if guesses else 0
    letter_discovery: dict[str, int] = {}
    first_green_turn: dict[int, int] = {}
    seen_letters: set[str] = set()
    per_guess: list[dict[str, int | str]] = []

    for turn, guess in enumerate(guesses, start=1):
        row_clue_violations = 0
        row_gray_reuses = 0
        if turn > 1:
            row_clue_violations += sum(
                1 for position, letter in green_positions.items() if guess[position] != letter
            )
            row_clue_violations += sum(1 for letter in known_present if letter not in guess)
            row_gray_reuses += sum(1 for letter in set(guess) if letter in known_absent)
        clue_violations += row_clue_violations
        gray_reuses += row_gray_reuses

        scores = score_wordle_guess(guess, answer)
        if turn == 1:
            row_skill = min(99, 69 + len(set(guess)) * 6)
        else:
            new_letters = len(set(guess) - seen_letters)
            exploration_penalty = 0 if guess == answer else max(0, 2 - new_letters) * 4
            row_skill = (
                99
                - row_clue_violations * 16
                - row_gray_reuses * 7
                - exploration_penalty
            )
            row_skill = max(1, min(99, row_skill))
        exact_count = scores.count("exact")
        present_count = scores.count("present")
        row_luck = max(1, min(99, 8 + exact_count * 18 + present_count * 10))
        per_guess.append(
            {
                "guess": guess,
                "skill": row_skill,
                "luck": row_luck,
            }
        )
        seen_letters.update(guess)

        for position, (letter, score) in enumerate(zip(guess, scores)):
            if score == "exact":
                green_positions[position] = letter
                known_present.add(letter)
                first_green_turn.setdefault(position, turn)
                letter_discovery.setdefault(letter, turn)
            elif score == "present":
                known_present.add(letter)
                letter_discovery.setdefault(letter, turn)

        for letter in set(guess):
            letter_scores = [scores[index] for index, value in enumerate(guess) if value == letter]
            if all(score == "miss" for score in letter_scores) and letter not in known_present:
                known_absent.add(letter)

    guess_count = len(guesses)
    variety_penalty = max(0, 5 - first_guess_variety) * 3
    skill = round(
        100
        - max(0, guess_count - 1) * 5
        - clue_violations * 9
        - gray_reuses * 3
        - variety_penalty
    )
    skill = max(1, min(99, skill))
    if guess_count == 1:
        skill = 99

    answer_letters = set(answer)
    discovery_values = [
        (7 - letter_discovery.get(letter, 6)) / 6 for letter in answer_letters
    ]
    discovery_score = sum(discovery_values) / max(1, len(discovery_values))
    green_bonus = sum(max(0, 4 - turn) * 2 for turn in first_green_turn.values())
    luck = round(8 + discovery_score * 70 + min(21, green_bonus))
    luck = max(1, min(99, luck))

    if skill >= 90:
        skill_note = "You used the clues cleanly with almost no wasted information."
    elif clue_violations:
        skill_note = "A few known clues slipped, but you recovered and found the word."
    elif gray_reuses:
        skill_note = "You solved it, though a few gray letters came back for another try."
    else:
        skill_note = "You made steady use of the information from each row."

    if luck >= 85:
        luck_note = "The right letters showed up unusually early."
    elif luck >= 60:
        luck_note = "The board gave you a fair amount to work with."
    else:
        luck_note = "The board made you earn this one."

    return {
        "skill": skill,
        "luck": luck,
        "guess_count": guess_count,
        "note": f"{skill_note} {luck_note}",
        "per_guess": per_guess,
    }


def wordle_rows_html(guesses: list[str], answer: str) -> str:
    """Build six rows of Wordle tiles."""
    rows = []
    for row_index in range(6):
        guess = guesses[row_index] if row_index < len(guesses) else ""
        scores = score_wordle_guess(guess, answer) if guess else ["empty"] * 5
        tiles = []
        for column in range(5):
            letter = html.escape(guess[column]) if guess else "&nbsp;"
            tiles.append(f'<span class="wordle-tile {scores[column]}">{letter}</span>')
        rows.append(f'<div class="wordle-row">{"".join(tiles)}</div>')
    return "".join(rows)


def interactive_wordle_board(
    guesses: list[str],
    answer: str,
    puzzle_index: int,
) -> None:
    """Render a tile grid that captures typing and submits through Streamlit."""
    rows = []
    active_row = len(guesses)
    for row_index in range(6):
        if row_index < len(guesses):
            guess = guesses[row_index]
            scores = score_wordle_guess(guess, answer)
            tiles = "".join(
                f'<span class="tile {scores[index]}">{html.escape(letter)}</span>'
                for index, letter in enumerate(guess)
            )
            row_class = "row"
        else:
            row_class = "row active" if row_index == active_row else "row"
            tiles = "".join('<span class="tile empty"></span>' for _ in range(5))
        rows.append(f'<div class="{row_class}">{tiles}</div>')

    st.iframe(
        f"""
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{ background: transparent; margin: 0; overflow: hidden; }}
            body {{
                color: #2f2a27;
                cursor: text;
                font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                outline: none;
                padding: 6px;
            }}
            .board {{
                background: rgba(255,255,255,.62);
                border: 1px solid rgba(255,255,255,.78);
                border-radius: 28px;
                box-shadow: 0 20px 55px rgba(54,73,59,.11);
                margin: 0 auto;
                max-width: 410px;
                padding: 1.25rem;
            }}
            .row {{
                display: grid;
                gap: .48rem;
                grid-template-columns: repeat(5, 1fr);
                margin-bottom: .48rem;
            }}
            .row:last-child {{ margin-bottom: 0; }}
            .tile {{
                align-items: center;
                aspect-ratio: 1;
                border: 2px solid rgba(68,83,71,.18);
                border-radius: 13px;
                color: white;
                display: flex;
                font-size: clamp(1.2rem, 4vw, 1.8rem);
                font-weight: 850;
                justify-content: center;
                text-transform: uppercase;
                transition: border-color .14s ease, transform .14s ease;
            }}
            .tile.empty {{ background: rgba(255,255,255,.76); color: #2f2a27; }}
            .tile.exact {{ background: #5d9671; border-color: #5d9671; }}
            .tile.present {{ background: #c7a960; border-color: #c7a960; }}
            .tile.miss {{ background: #7a7773; border-color: #7a7773; }}
            .active .tile {{ border-color: rgba(66,111,85,.48); }}
            .active .tile.filled {{ border-color: #426f55; transform: scale(1.025); }}
            .hint {{
                color: #796f68;
                font-size: .78rem;
                margin-top: .8rem;
                text-align: center;
            }}
            .hint strong {{ color: #426f55; }}
        </style>
        <div class="board" id="board" data-puzzle="{puzzle_index}">{"".join(rows)}</div>
        <div class="hint" id="hint"><strong>Type directly into the row.</strong> Backspace deletes. Enter submits.</div>
        <script>
            const activeTiles = Array.from(document.querySelectorAll(".row.active .tile"));
            const hint = document.getElementById("hint");
            let letters = [];
            let sending = false;

            function draw() {{
                activeTiles.forEach((tile, index) => {{
                    tile.textContent = letters[index] || "";
                    tile.classList.toggle("filled", Boolean(letters[index]));
                }});
            }}

            function findSubmission() {{
                const parentDocument = window.parent.document;
                return {{
                    input: parentDocument.querySelector(".st-key-wordle_submission input"),
                    button: parentDocument.querySelector(".st-key-wordle_submission button")
                }};
            }}

            function submitGuess() {{
                if (letters.length !== 5 || sending) {{
                    hint.textContent = letters.length === 5 ? "Submitting…" : "Add five letters first.";
                    return;
                }}
                const submission = findSubmission();
                if (!submission.input || !submission.button) {{
                    hint.textContent = "One second… then press Enter again.";
                    return;
                }}
                sending = true;
                const valueSetter = Object.getOwnPropertyDescriptor(
                    window.parent.HTMLInputElement.prototype,
                    "value"
                ).set;
                valueSetter.call(submission.input, letters.join(""));
                submission.input.dispatchEvent(new Event("input", {{bubbles: true}}));
                submission.input.dispatchEvent(new Event("change", {{bubbles: true}}));
                setTimeout(() => submission.button.click(), 40);
            }}

            document.body.tabIndex = 0;
            document.body.focus();
            document.body.addEventListener("click", () => document.body.focus());
            document.body.addEventListener("keydown", event => {{
                if (/^[a-zA-Z]$/.test(event.key) && letters.length < 5) {{
                    letters.push(event.key.toUpperCase());
                    draw();
                    event.preventDefault();
                }} else if (event.key === "Backspace") {{
                    letters.pop();
                    draw();
                    event.preventDefault();
                }} else if (event.key === "Enter") {{
                    submitGuess();
                    event.preventDefault();
                }}
            }});
        </script>
        """,
        height=575,
    )


def initialize_wordle_gate(gate_id: str) -> None:
    """Reset the puzzle run when a new birthday year begins."""
    if st.session_state.get("wordle_gate_id") == gate_id:
        return
    progress_key = f"wordle_{gate_id}"
    try:
        saved_progress = int(st.query_params.get(progress_key, "0"))
    except (TypeError, ValueError):
        saved_progress = 0
    saved_progress = max(0, min(saved_progress, len(WORDLE_WORDS)))
    st.session_state.wordle_gate_id = gate_id
    st.session_state.wordle_index = min(saved_progress, len(WORDLE_WORDS) - 1)
    st.session_state.wordle_guesses = []
    st.session_state.wordle_failed = False
    st.session_state.wordle_invalid_guess = None
    st.session_state.wordle_bot_active = False
    st.session_state.wordle_pending_next_index = None
    st.session_state.wordle_unlocked_gate = (
        gate_id if saved_progress == len(WORDLE_WORDS) else None
    )


def render_wordle_gate(gate_id: str) -> None:
    """Require 21 completed Wordles before rendering the birthday app."""
    initialize_wordle_gate(gate_id)
    puzzle_index = int(st.session_state.wordle_index)
    answer = WORDLE_WORDS[puzzle_index]
    guesses = list(st.session_state.wordle_guesses)

    st.markdown('<div class="wordle-kicker">21 Wordles for 21</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="wordle-progress">Puzzle {puzzle_index + 1} of {len(WORDLE_WORDS)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="wordle-copy">Solve all 21 to unlock a surprise for Naur!</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.wordle_bot_active:
        bot_result = analyze_wordle(guesses, answer)
        guess_score_rows = "".join(
            '<div class="wordlebot-guess-row">'
            f'<span>{index}. {html.escape(str(row["guess"]))}</span>'
            f'<strong>{row["skill"]}</strong>'
            f'<strong>{row["luck"]}</strong>'
            '</div>'
            for index, row in enumerate(bot_result["per_guess"], start=1)
        )
        st.markdown(
            f'<div class="wordle-board">{wordle_rows_html(guesses, answer)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="wordlebot-card">
                <div class="wordlebot-name">WORDLEBOT</div>
                <div class="wordlebot-title">Solved in {bot_result['guess_count']}/6</div>
                <div class="wordlebot-scores">
                    <div><span>{bot_result['skill']}</span><small>Overall skill</small></div>
                    <div><span>{bot_result['luck']}</span><small>Overall luck</small></div>
                </div>
                <div class="wordlebot-breakdown">
                    <div class="wordlebot-guess-row header">
                        <span>Guess</span><strong>Skill</strong><strong>Luck</strong>
                    </div>
                    {guess_score_rows}
                </div>
                <div class="wordlebot-note">{html.escape(str(bot_result['note']))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        pending_index = int(st.session_state.wordle_pending_next_index)
        button_label = (
            "Unlock the birthday app  ✦"
            if pending_index == len(WORDLE_WORDS)
            else "Next Wordle  →"
        )
        if st.button(button_label, key="continue_after_wordlebot", width="stretch"):
            st.session_state.wordle_bot_active = False
            st.session_state.wordle_pending_next_index = None
            st.session_state.wordle_guesses = []
            if pending_index == len(WORDLE_WORDS):
                st.session_state.wordle_unlocked_gate = gate_id
                st.session_state.wordle_just_unlocked = True
            else:
                st.session_state.wordle_index = pending_index
            st.rerun()
        return
    if st.session_state.wordle_failed:
        st.markdown(
            f'<div class="wordle-board">{wordle_rows_html(guesses, answer)}</div>',
            unsafe_allow_html=True,
        )
        st.error("Not quite. Try this Wordle again.")
        if st.button("Retry this Wordle", key="retry_wordle", width="stretch"):
            st.session_state.wordle_guesses = []
            st.session_state.wordle_failed = False
            st.session_state.wordle_invalid_guess = None
            st.rerun()
        return

    invalid_guess = st.session_state.get("wordle_invalid_guess")
    if invalid_guess:
        st.warning(f'“{invalid_guess}” is not in the Wordle word list. Try another word.')
        st.session_state.wordle_invalid_guess = None

    interactive_wordle_board(guesses, answer, puzzle_index)
    with st.container(key="wordle_submission"):
        with st.form(f"wordle_guess_{puzzle_index}", clear_on_submit=True):
            guess = st.text_input(
                "Five-letter guess",
                max_chars=5,
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Submit tile row")

    if not submitted:
        return
    cleaned_guess = guess.strip().upper()
    if len(cleaned_guess) != 5 or not cleaned_guess.isalpha():
        st.session_state.wordle_invalid_guess = cleaned_guess or "That guess"
        st.rerun()
    if cleaned_guess not in load_wordle_allowed_words():
        st.session_state.wordle_invalid_guess = cleaned_guess
        st.rerun()

    guesses.append(cleaned_guess)
    st.session_state.wordle_guesses = guesses
    if cleaned_guess == answer:
        next_index = puzzle_index + 1
        st.query_params[f"wordle_{gate_id}"] = str(next_index)
        st.session_state.wordle_bot_active = True
        st.session_state.wordle_pending_next_index = next_index
        st.rerun()
    if len(guesses) >= 6:
        st.session_state.wordle_failed = True
    st.rerun()


st.markdown(
    """
    <style>
    :root {
        --ink: #2f2a27;
        --muted: #796f68;
        --cream: #f8f3ed;
        --card: rgba(255, 255, 255, 0.72);
        --rose: #c87878;
        --line: rgba(74, 58, 49, 0.13);
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 10% 5%, rgba(238, 193, 180, .42), transparent 29rem),
            radial-gradient(circle at 94% 35%, rgba(189, 205, 193, .46), transparent 31rem),
            linear-gradient(145deg, #fbf7f2 0%, #f3ede6 100%);
        color: var(--ink);
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { visibility: hidden; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1120px;
        padding-top: 2.5rem;
        padding-bottom: 5rem;
    }

    html, body, [class*="st-"] {
        font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    [data-testid="stIconMaterial"] {
        font-family: "Material Symbols Rounded" !important;
    }

    h1, h2, h3 { color: var(--ink); letter-spacing: -.035em; }

    .eyebrow {
        color: #a25f62;
        font-size: .73rem;
        font-weight: 750;
        letter-spacing: .18em;
        text-transform: uppercase;
        margin-bottom: .6rem;
        position: relative;
        z-index: 20;
    }

    .hero-title {
        max-width: 720px;
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(3.2rem, 8vw, 6.9rem);
        font-weight: 400;
        letter-spacing: -.065em;
        line-height: .89;
        margin: 0 0 1.3rem;
        position: relative;
        z-index: 20;
    }

    .st-key-birthday_countdown {
        position: relative;
        z-index: 20;
    }

    .st-key-wordle_submission {
        display: none;
    }

    .wordle-kicker {
        color: #426f55;
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .18em;
        margin-top: .4rem;
        text-align: center;
        text-transform: uppercase;
    }

    .wordle-progress {
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(2.1rem, 5vw, 3.7rem);
        letter-spacing: -.045em;
        margin-top: .35rem;
        text-align: center;
    }

    .wordle-copy {
        color: var(--muted);
        margin: .45rem auto 1.35rem;
        max-width: 520px;
        text-align: center;
    }

    .wordle-board {
        background: rgba(255,255,255,.62);
        border: 1px solid rgba(255,255,255,.78);
        border-radius: 28px;
        box-shadow: 0 20px 55px rgba(54,73,59,.11);
        margin: 0 auto 1rem;
        max-width: 410px;
        padding: 1.25rem;
    }

    .wordle-row {
        display: grid;
        gap: .48rem;
        grid-template-columns: repeat(5, 1fr);
        margin-bottom: .48rem;
    }

    .wordle-row:last-child { margin-bottom: 0; }

    .wordle-tile {
        align-items: center;
        aspect-ratio: 1;
        border: 2px solid rgba(68,83,71,.18);
        border-radius: 13px;
        color: white;
        display: flex;
        font-size: clamp(1.2rem, 4vw, 1.8rem);
        font-weight: 850;
        justify-content: center;
        text-transform: uppercase;
    }

    .wordle-tile.empty { background: rgba(255,255,255,.72); color: transparent; }
    .wordle-tile.exact { background: #5d9671; border-color: #5d9671; }
    .wordle-tile.present { background: #c7a960; border-color: #c7a960; }
    .wordle-tile.miss { background: #7a7773; border-color: #7a7773; }

    .wordlebot-card {
        background:
            radial-gradient(circle at 92% 5%, rgba(182,219,184,.52), transparent 12rem),
            rgba(255,255,255,.78);
        border: 1px solid rgba(255,255,255,.88);
        border-radius: 26px;
        box-shadow: 0 18px 48px rgba(54,73,59,.13);
        margin: 1rem auto;
        max-width: 410px;
        padding: 1.25rem;
        text-align: center;
    }

    .wordlebot-name {
        color: #426f55;
        font-size: .7rem;
        font-weight: 850;
        letter-spacing: .2em;
    }

    .wordlebot-title {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.75rem;
        letter-spacing: -.035em;
        margin: .45rem 0 1rem;
    }

    .wordlebot-scores {
        display: grid;
        gap: .75rem;
        grid-template-columns: 1fr 1fr;
    }

    .wordlebot-scores div {
        background: rgba(239,247,239,.84);
        border-radius: 18px;
        padding: .8rem;
    }

    .wordlebot-scores span {
        color: #426f55;
        display: block;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 2.35rem;
        line-height: 1;
    }

    .wordlebot-scores small {
        color: var(--muted);
        display: block;
        font-size: .66rem;
        font-weight: 800;
        letter-spacing: .14em;
        margin-top: .3rem;
        text-transform: uppercase;
    }

    .wordlebot-breakdown {
        background: rgba(255,255,255,.62);
        border-radius: 16px;
        margin-top: .85rem;
        padding: .35rem .7rem;
    }

    .wordlebot-guess-row {
        align-items: center;
        border-bottom: 1px solid rgba(66,111,85,.12);
        display: grid;
        font-size: .8rem;
        gap: .55rem;
        grid-template-columns: 1fr 58px 58px;
        padding: .55rem .15rem;
        text-align: center;
    }

    .wordlebot-guess-row:last-child { border-bottom: 0; }
    .wordlebot-guess-row span:first-child { font-weight: 750; text-align: left; }
    .wordlebot-guess-row strong { color: #426f55; font-size: .92rem; }
    .wordlebot-guess-row.header {
        color: var(--muted);
        font-size: .62rem;
        font-weight: 800;
        letter-spacing: .1em;
        text-transform: uppercase;
    }

    .wordlebot-guess-row.header strong { color: var(--muted); font-size: .62rem; }

    .wordlebot-note {
        color: var(--muted);
        font-size: .84rem;
        margin-top: .9rem;
    }

    div[data-testid="stForm"]:has(input[aria-label="Five-letter guess"]) {
        background: rgba(255,255,255,.46);
        border: 1px solid rgba(255,255,255,.72);
        border-radius: 22px;
        margin: 0 auto;
        max-width: 410px;
        padding: .7rem;
    }

    div[data-testid="stTextArea"] textarea {
        background: rgba(255,255,255,.78);
        border: 1px solid var(--line);
        border-radius: 21px;
        box-shadow: 0 18px 60px rgba(81, 61, 50, .08);
        color: var(--ink);
        font-size: 1.06rem;
        line-height: 1.5;
        min-height: 132px;
        padding: 1.1rem 1.2rem;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: rgba(185, 105, 108, .55);
        box-shadow: 0 0 0 3px rgba(185, 105, 108, .09);
    }

    .stButton > button, [data-testid="stFormSubmitButton"] button {
        border-radius: 999px;
        border: 1px solid var(--line);
        font-weight: 680;
        transition: transform .18s ease, box-shadow .18s ease;
    }

    [data-testid="stFormSubmitButton"] button {
        background: var(--ink);
        color: white;
        min-height: 3.1rem;
        padding: 0 1.5rem;
        border: 0;
    }

    .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(61, 45, 37, .11);
        border-color: rgba(74, 58, 49, .22);
    }

    .section-rule { border-top: 1px solid var(--line); margin: 3.5rem 0 2.7rem; }

    .result-label {
        color: var(--muted);
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
    }

    .mood-read {
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(2.25rem, 5vw, 4.1rem);
        line-height: 1;
        margin: .4rem 0 1.7rem;
    }

    .song-card {
        align-items: center;
        background: var(--card);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,.8);
        border-radius: 26px;
        box-shadow: 0 22px 65px rgba(75, 56, 47, .1);
        display: grid;
        gap: 1.2rem;
        grid-template-columns: 112px 1fr auto;
        padding: 1.05rem;
    }

    .album-placeholder, .album-cover {
        align-items: flex-end;
        aspect-ratio: 1;
        border-radius: 19px;
        color: rgba(255,255,255,.85);
        display: flex;
        font-size: 1.4rem;
        justify-content: flex-end;
        padding: .85rem;
    }

    .album-placeholder {
        background: linear-gradient(145deg, #d9a5a1, #986e7a 48%, #53646b);
    }

    .album-cover {
        background-position: center;
        background-size: cover;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,.22);
        padding: 0;
    }

    .song-title { font-family: Georgia, serif; font-size: 1.65rem; line-height: 1.1; }
    .song-artist { color: var(--muted); margin-top: .35rem; }
    .now-playing {
        align-items: end;
        display: flex;
        gap: 4px;
        height: 31px;
        margin-right: .8rem;
    }

    .now-playing span {
        animation: sound-wave .9s ease-in-out infinite alternate;
        background: currentColor;
        border-radius: 999px;
        display: block;
        height: 36%;
        opacity: .75;
        width: 4px;
    }

    .now-playing span:nth-child(2) { animation-delay: -.35s; height: 90%; }
    .now-playing span:nth-child(3) { animation-delay: -.6s; height: 58%; }
    .now-playing span:nth-child(4) { animation-delay: -.2s; height: 75%; }

    @keyframes sound-wave {
        from { transform: scaleY(.42); }
        to { transform: scaleY(1); }
    }

    .photo-grid {
        display: grid;
        gap: .85rem;
        grid-template-columns: 1.25fr .75fr 1fr;
        grid-template-rows: 158px 158px;
        margin-top: 1rem;
    }

    .photo-tile {
        background-position: center;
        background-size: cover;
        border: 1px solid rgba(255,255,255,.65);
        border-radius: 22px;
        box-shadow: 0 13px 35px rgba(66, 48, 39, .07);
        min-height: 130px;
        overflow: hidden;
        position: relative;
    }

    .photo-tile::after {
        background: linear-gradient(transparent, rgba(32,26,24,.22));
        bottom: 0; content: ""; left: 0; position: absolute; right: 0; top: 45%;
    }

    .photo-tile.one { background: linear-gradient(145deg, #dfbbb1, #b8c6bd 70%, #7f9694); grid-row: 1 / 3; }
    .photo-tile.two { background: linear-gradient(35deg, #8e7d74, #d7b9a9 50%, #eddccc); }
    .photo-tile.three { background: linear-gradient(165deg, #d4c3ad, #93a59d 62%, #596d70); }
    .photo-tile.four { background: linear-gradient(65deg, #6f7e82, #a99ba1 42%, #e2bbb1); grid-column: 2 / 4; }

    div[data-testid="stImage"] {
        margin-bottom: .7rem;
    }

    div[data-testid="stImage"] img {
        border: 1px solid rgba(255,255,255,.75);
        border-radius: 20px;
        box-shadow: 0 13px 35px rgba(66, 48, 39, .10);
        height: 200px;
        object-fit: cover;
        width: 100%;
    }

    .st-key-player_controls {
        backdrop-filter: blur(18px);
        border: 1px solid rgba(255,255,255,.72);
        border-radius: 24px;
        box-shadow: 0 16px 42px rgba(61,45,37,.10);
        margin-top: .8rem;
        overflow: hidden;
        padding: .75rem;
    }

    .st-key-player_controls [data-testid="stAudio"] {
        margin: 0;
    }

    .st-key-player_controls audio {
        border-radius: 999px;
        display: block;
        width: 100%;
    }

    .st-key-player_controls audio::-webkit-media-controls-enclosure {
        border-radius: 999px;
    }

    .st-key-next_song button,
    .st-key-save_song button {
        min-height: 2.75rem;
    }

    .st-key-next_song button {
        border: 0;
        color: white;
    }

    .st-key-save_song button {
        background: rgba(255,255,255,.66);
    }

    .st-key-player_actions {
        display: none;
    }

    .st-key-photo_grid [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap;
        gap: .7rem;
    }

    .st-key-photo_grid [data-testid="stColumn"] {
        flex: 1 1 0 !important;
        min-width: 0 !important;
        width: 50% !important;
    }

    .spec-card {
        background: rgba(255,255,255,.45);
        border: 1px solid var(--line);
        border-radius: 18px;
        min-height: 128px;
        padding: 1.15rem;
    }
    .spec-num { color: #b46b6d; font-size: .72rem; font-weight: 800; letter-spacing: .12em; }
    .spec-title { font-weight: 720; margin: .55rem 0 .35rem; }
    .spec-copy { color: var(--muted); font-size: .84rem; line-height: 1.5; }

    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] { padding-top: 1.4rem; }
        .song-card { grid-template-columns: 86px 1fr; }
        .album-placeholder { border-radius: 15px; }
        .now-playing { display: none; }
        .photo-grid { grid-template-columns: 1fr 1fr; grid-template-rows: 175px 130px; }
        .photo-tile.one { grid-row: auto; }
        .photo-tile.four { grid-column: 1 / 3; }
        div[data-testid="stImage"] img { height: 220px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def infer_display_vibe(text: str) -> str:
    """Temporary UX-only categorization; the real model will replace this."""
    normalized = text.lower()
    vibe_rules = [
        (("happy", "excited", "celebrate", "sunny", "great"), "bright & weightless"),
        (("sad", "lonely", "cry", "heartbreak", "miss"), "tender & a little blue"),
        (("calm", "peace", "quiet", "relax", "soft"), "soft, slow & grounded"),
        (("angry", "mad", "frustrated", "rage"), "loud, electric & releasing"),
        (("nostalgic", "remember", "memory", "old", "home"), "warm with a hint of nostalgia"),
        (("love", "romantic", "crush", "butterflies"), "romantic & glowing"),
        (("energy", "energetic", "hype", "dance", "party"), "bright, bold & kinetic"),
        (("dream", "dreamy", "float", "ethereal"), "dreamy & otherworldly"),
        (("focus", "focused", "study", "work", "productive"), "clear-minded & quietly driven"),
        (("cozy", "warm", "blanket", "rainy"), "cozy, close & unhurried"),
        (("hope", "hopeful", "optimistic", "new beginning"), "hopeful & opening up"),
        (("anxious", "nervous", "overwhelmed", "stress"), "gentle & reassuring"),
    ]
    for keywords, label in vibe_rules:
        if any(keyword in normalized for keyword in keywords):
            return label
    return "dreamy & reflective"


def infer_mood_palette(text: str) -> dict[str, str | int]:
    """Choose one of 108 stable palettes from the wording and mood family."""
    normalized = text.lower()
    # Twelve emotional neighborhoods × nine wording-based variations = 108.
    # The second glow always returns to green as her visual signature.
    family_rules = [
        (("happy", "excited", "celebrate", "sunny", "great"), 46),
        (("sad", "lonely", "cry", "heartbreak", "miss"), 214),
        (("calm", "peace", "quiet", "relax", "soft"), 148),
        (("angry", "mad", "frustrated", "rage"), 354),
        (("nostalgic", "remember", "memory", "old", "home"), 28),
        (("anxious", "nervous", "overwhelmed", "stress"), 258),
        (("love", "romantic", "crush", "butterflies"), 332),
        (("energy", "energetic", "hype", "dance", "party"), 14),
        (("dream", "dreamy", "float", "ethereal"), 286),
        (("focus", "focused", "study", "work", "productive"), 178),
        (("cozy", "warm", "blanket", "rainy"), 82),
    ]
    # Unclassified and hopeful language intentionally land in the green family.
    base_hue = 136
    family_index = len(family_rules)
    for index, (keywords, family_hue) in enumerate(family_rules):
        if any(keyword in normalized for keyword in keywords):
            base_hue = family_hue
            family_index = index
            break

    fingerprint = int(hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:8], 16)
    variant = fingerprint % 9
    hue_offset = (-16, -12, -8, -4, 0, 4, 8, 12, 16)[variant]
    hue = (base_hue + hue_offset) % 360
    companion_hue = (hue + 28 + (variant % 3) * 7) % 360
    signature_green = (132 + hue_offset // 2) % 360

    return {
        "start": f"hsl({hue} 42% {95 - variant % 2}%)",
        "end": f"hsl({companion_hue} 31% {87 - variant % 3}%)",
        "glow_one": f"hsla({hue}, 58%, 72%, .46)",
        "glow_two": f"hsla({signature_green}, 45%, 70%, .38)",
        "accent": f"hsl({hue} 34% 39%)",
        "album_one": f"hsl({hue} 47% 69%)",
        "album_two": f"hsl({companion_hue} 37% 51%)",
        "album_three": f"hsl({signature_green} 28% 34%)",
        "palette_number": str(family_index * 9 + variant + 1),
        "hue": hue,
    }


@st.cache_data
def load_photo_features(collection_version: str) -> list[dict]:
    del collection_version  # The value intentionally forms part of Streamlit's cache key.
    if not PHOTO_FEATURES_PATH.exists():
        return []
    return json.loads(PHOTO_FEATURES_PATH.read_text())


@st.cache_data
def load_song_catalog(catalog_version: str) -> list[dict]:
    del catalog_version  # The value intentionally forms part of Streamlit's cache key.
    if not SONG_CATALOG_PATH.exists():
        return []
    return json.loads(SONG_CATALOG_PATH.read_text())


@st.cache_data
def load_song_profiles(profile_version: str) -> dict[str, dict]:
    """Load generated song profiles while allowing an in-progress scan to refresh."""
    del profile_version
    if not SONG_PROFILES_PATH.exists():
        return {}
    return json.loads(SONG_PROFILES_PATH.read_text()).get("profiles", {})


def normalize_audio_name(value: str) -> str:
    """Normalize a title or filename for local-audio matching."""
    normalized = value.lower()
    normalized = re.sub(r"\[[^]]+\]", " ", normalized)
    normalized = re.sub(
        r"\([^)]*(?:official|audio|lyric|video|visuali[sz]er)[^)]*\)",
        " ",
        normalized,
    )
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


def song_profile_key(song: dict) -> str:
    """Return the stable catalog key used by the offline analyzer."""
    return f"{normalize_audio_name(song['artist'])}|{normalize_audio_name(song['title'])}"


def load_playable_song_catalog(
    catalog_version: str,
    audio_collection_version: str,
) -> list[dict]:
    """Match catalog songs with MP3s inside their album folders."""
    del audio_collection_version  # The value intentionally forms part of the cache key.
    catalog = load_song_catalog(catalog_version)
    audio_files = list(AUDIO_DIR.rglob("*.mp3")) if AUDIO_DIR.exists() else []
    files_by_album: dict[str, list[Path]] = {}
    for audio_path in audio_files:
        album_key = normalize_audio_name(audio_path.parent.name)
        files_by_album.setdefault(album_key, []).append(audio_path)

    playable = []
    for song in catalog:
        title_key = normalize_audio_name(song["title"])
        album_key = normalize_audio_name(song["album"])
        title_pattern = re.compile(rf"(^| ){re.escape(title_key)}( |$)")
        matches = [
            path
            for path in files_by_album.get(album_key, [])
            if title_pattern.search(normalize_audio_name(path.stem))
        ]
        if matches:
            audio_path = min(matches, key=lambda path: len(normalize_audio_name(path.stem)))
            playable.append({**song, "audio_path": str(audio_path)})
    return playable


@st.cache_data
def album_art_data_uri(album: str) -> str | None:
    """Return locally stored album artwork as an embeddable data URI."""
    artwork_path = ALBUM_ART_PATHS.get(album)
    if not artwork_path or not artwork_path.exists():
        return None
    encoded = base64.b64encode(artwork_path.read_bytes()).decode("ascii")
    mime_type = "image/png" if artwork_path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime_type};base64,{encoded}"


@st.cache_data(max_entries=3)
def audio_data_uri(audio_path: str) -> str:
    """Return a local MP3 as an embeddable data URI."""
    encoded = base64.b64encode(Path(audio_path).read_bytes()).decode("ascii")
    return f"data:audio/mpeg;base64,{encoded}"


def _legacy_custom_audio_player(
    audio_path: str,
    palette: dict[str, str | int],
    autoplay: bool = False,
) -> None:
    """Render a custom player for a local audio file."""
    source = json.dumps(audio_data_uri(audio_path))
    st.iframe(
        f"""
        <style>
            * {{ box-sizing: border-box; }}
            :root {{
                --accent: {palette['accent']};
                --accent-soft: {palette['album_one']};
                --accent-mid: {palette['album_two']};
                --ink: #2f2a27;
                --muted: #746c66;
            }}
            body {{
                background: transparent;
                color: var(--ink);
                font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                margin: 0;
                overflow: hidden;
            }}
            .player {{
                background: rgba(255,255,255,.4);
                border: 1px solid rgba(255,255,255,.72);
                border-radius: 24px;
                box-shadow: 0 12px 30px rgba(47,42,39,.1);
                padding: 18px 24px 16px;
            }}
            .play {{
                align-items: center;
                background: linear-gradient(145deg, var(--accent-soft), var(--accent-mid));
                border: 0;
                border-radius: 50%;
                box-shadow: 0 8px 22px rgba(47,42,39,.18);
                color: white;
                cursor: pointer;
                display: flex;
                grid-column: 3;
                height: 68px;
                justify-content: center;
                justify-self: center;
                margin: 0;
                padding: 0;
                transition: transform .18s ease, box-shadow .18s ease;
                width: 68px;
            }}
            .play::before {{
                border-bottom: 11px solid transparent;
                border-left: 18px solid currentColor;
                border-top: 11px solid transparent;
                content: "";
                display: block;
                margin-left: 4px;
            }}
            .play:hover {{ box-shadow: 0 11px 27px rgba(47,42,39,.24); transform: translateY(-1px) scale(1.02); }}
            .play:active {{ transform: scale(.96); }}
            .play.playing::before {{
                background: linear-gradient(to right, currentColor 0 6px, transparent 6px 12px, currentColor 12px 18px);
                border: 0;
                height: 22px;
                margin-left: 0;
                width: 18px;
            }}
            .timeline {{ display: block; }}
            .time-row {{
                color: var(--muted);
                display: flex;
                font-size: .68rem;
                font-variant-numeric: tabular-nums;
                justify-content: space-between;
                margin-top: 5px;
            }}
            input[type="range"] {{
                appearance: none;
                background: linear-gradient(to right, var(--accent) 0 var(--fill, 0%), rgba(65,58,53,.14) var(--fill, 0%) 100%);
                border-radius: 999px;
                cursor: pointer;
                height: 6px;
                margin: 0;
                outline: none;
                width: 100%;
            }}
            input[type="range"]::-webkit-slider-thumb {{
                appearance: none;
                background: white;
                border: 2px solid var(--accent);
                border-radius: 50%;
                box-shadow: 0 2px 7px rgba(47,42,39,.18);
                height: 15px;
                width: 15px;
            }}
            .controls {{
                align-items: center;
                display: grid;
                grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 76px minmax(0, 1fr) minmax(0, 1fr);
                margin-top: 7px;
            }}
            .control {{
                align-items: center;
                background: transparent;
                border: 0;
                color: var(--ink);
                cursor: pointer;
                display: flex;
                font-size: 1.45rem;
                height: 54px;
                justify-content: center;
                margin: auto;
                min-width: 48px;
                padding: 0;
                transition: color .18s ease, transform .18s ease;
            }}
            .control:hover {{ color: var(--accent); transform: translateY(-1px); }}
            .control:active {{ transform: scale(.92); }}
            .control.saved {{ color: var(--accent); }}
            .queue {{ font-size: 1.55rem; line-height: .65; }}
            .skip {{ font-size: 1.28rem; }}
            .heart {{ font-family: Georgia, serif; font-size: 2rem; }}
            @media (max-width: 430px) {{
                .player {{ padding: 15px 14px 13px; }}
                .play {{ height: 60px; width: 60px; }}
                .control {{ min-width: 40px; }}
            }}
        </style>
        <div class="player">
            <div class="timeline">
                <input id="progress" type="range" min="0" max="1000" value="0" aria-label="Song progress">
                <div class="time-row">
                    <span id="elapsed">0:00</span>
                    <span id="duration">0:00</span>
                </div>
            </div>
            <div class="controls">
                <button class="control queue" id="queue" aria-label="Mute">☰</button>
                <button class="control skip" id="back" aria-label="Previous song">◀┃</button>
                <button class="play" id="play" aria-label="Play song"></button>
                <button class="control skip" id="forward" aria-label="Next song">┃▶</button>
                <button class="control heart" id="heart" aria-label="Favorite">♡</button>
            </div>
        </div>
        <audio id="audio" preload="metadata" src={source}></audio>
        <script>
            const audio = document.getElementById("audio");
            const play = document.getElementById("play");
            const progress = document.getElementById("progress");
            const elapsed = document.getElementById("elapsed");
            const duration = document.getElementById("duration");
            const back = document.getElementById("back");
            const forward = document.getElementById("forward");
            const heart = document.getElementById("heart");
            const queue = document.getElementById("queue");
            const shouldAutoplay = {str(autoplay).lower()};

            function formatTime(seconds) {{
                if (!Number.isFinite(seconds)) return "0:00";
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60).toString().padStart(2, "0");
                return `${{mins}}:${{secs}}`;
            }}
            function paintRange(input, percent) {{ input.style.setProperty("--fill", `${{percent}}%`); }}
            function setPlaying(isPlaying) {{
                play.classList.toggle("playing", isPlaying);
                play.setAttribute("aria-label", isPlaying ? "Pause song" : "Play song");
            }}

            audio.volume = .82;
            audio.addEventListener("loadedmetadata", () => duration.textContent = formatTime(audio.duration));
            if (shouldAutoplay) {{
                const beginPlayback = () => audio.play().catch(() => {{}});
                if (audio.readyState >= 3) beginPlayback();
                else audio.addEventListener("canplay", beginPlayback, {{once: true}});
            }}
            audio.addEventListener("timeupdate", () => {{
                const percent = audio.duration ? (audio.currentTime / audio.duration) * 100 : 0;
                progress.value = Math.round(percent * 10);
                paintRange(progress, percent);
                elapsed.textContent = formatTime(audio.currentTime);
            }});
            audio.addEventListener("ended", () => setPlaying(false));
            audio.addEventListener("play", () => setPlaying(true));
            audio.addEventListener("pause", () => {{ if (!audio.ended) setPlaying(false); }});
            play.addEventListener("click", () => audio.paused ? audio.play() : audio.pause());
            progress.addEventListener("input", () => {{
                const percent = Number(progress.value) / 10;
                paintRange(progress, percent);
                if (audio.duration) audio.currentTime = (percent / 100) * audio.duration;
            }});
            function clickAppButton(selector) {{
                try {{
                    const button = window.parent.document.querySelector(selector);
                    if (button) {{ button.click(); return true; }}
                }} catch (error) {{}}
                return false;
            }}
            back.addEventListener("click", () => {{
                if (!clickAppButton(".st-key-previous_song button")) {{
                    audio.currentTime = Math.max(0, audio.currentTime - 15);
                }}
            }});
            forward.addEventListener("click", () => {{
                if (!clickAppButton(".st-key-next_song button")) {{
                    audio.currentTime = Math.min(audio.duration || 0, audio.currentTime + 15);
                }}
            }});
            queue.addEventListener("click", () => {{
                audio.muted = !audio.muted;
                queue.style.opacity = audio.muted ? ".38" : "1";
                queue.setAttribute("aria-label", audio.muted ? "Unmute" : "Mute");
            }});
            heart.addEventListener("click", () => {{
                const saved = heart.classList.toggle("saved");
                heart.textContent = saved ? "♥" : "♡";
                heart.setAttribute("aria-label", saved ? "Remove favorite" : "Favorite");
            }});
        </script>
        """,
        height=174,
    )


def custom_audio_player(
    audio_path: str,
    previous_audio_path: str | None,
    next_audio_path: str | None,
    palette: dict[str, str | int],
    autoplay: bool = False,
) -> dict[str, str | int] | None:
    """Render the connected player and return navigation events."""
    return AUDIO_PLAYER_COMPONENT(
        source=audio_data_uri(audio_path),
        previous_source=(
            audio_data_uri(previous_audio_path) if previous_audio_path else None
        ),
        next_source=audio_data_uri(next_audio_path) if next_audio_path else None,
        palette={
            "accent": palette["accent"],
            "soft": palette["album_one"],
            "mid": palette["album_two"],
        },
        autoplay=autoplay,
        default=None,
        key="connected_audio_player",
    )


def mood_song_targets(text: str) -> tuple[set[str], float, float]:
    """Convert free-form language into song tags, positivity, and intensity."""
    normalized = text.lower()
    rules = [
        (("happy", "excited", "sunny", "celebrate", "great"), {"joyful", "playful", "hopeful"}, 0.84, 0.72),
        (("sad", "down", "cry", "blue"), {"sad", "vulnerable", "lonely"}, 0.16, 0.30),
        (("heartbreak", "heartbroken", "broke up", "breakup"), {"heartbroken", "longing", "cathartic"}, 0.12, 0.48),
        (("miss", "remember", "nostalgic", "memory", "old times"), {"nostalgic", "longing", "reflective"}, 0.42, 0.38),
        (("love", "romantic", "crush", "butterflies", "in love"), {"romantic", "warm", "dreamy"}, 0.78, 0.56),
        (("angry", "mad", "frustrated", "rage", "pissed"), {"angry", "defiant", "cathartic"}, 0.22, 0.84),
        (("anxious", "nervous", "overwhelmed", "stress", "worried"), {"anxious", "vulnerable", "restless"}, 0.30, 0.46),
        (("calm", "peace", "quiet", "relax", "soft"), {"calm", "peaceful", "reflective"}, 0.62, 0.24),
        (("dream", "dreamy", "float", "ethereal"), {"dreamy", "calm", "romantic"}, 0.58, 0.34),
        (("energy", "energetic", "hype", "dance", "party", "club"), {"energetic", "confident", "euphoric"}, 0.76, 0.92),
        (("confident", "powerful", "unstoppable", "hot"), {"confident", "defiant", "liberated"}, 0.78, 0.82),
        (("jealous", "insecure", "not enough"), {"jealous", "insecure", "anxious"}, 0.28, 0.58),
        (("alone", "lonely", "empty"), {"lonely", "sad", "reflective"}, 0.13, 0.24),
        (("moving on", "move on", "new beginning", "healing"), {"healing", "hopeful", "liberated"}, 0.66, 0.46),
        (("cozy", "warm", "rainy", "blanket"), {"warm", "calm", "intimate"}, 0.66, 0.28),
    ]

    matched = [rule for rule in rules if any(word in normalized for word in rule[0])]
    if not matched:
        return {"reflective", "dreamy", "bittersweet"}, 0.48, 0.42

    tags: set[str] = set()
    for _, rule_tags, _, _ in matched:
        tags.update(rule_tags)
    valence = sum(rule[2] for rule in matched) / len(matched)
    energy = sum(rule[3] for rule in matched) / len(matched)
    return tags, valence, energy


def select_mood_song(text: str, shuffle_count: int) -> dict | None:
    """Rank playable songs and rotate through the closest matches."""
    catalog = load_playable_song_catalog(
        SONG_CATALOG_VERSION,
        AUDIO_COLLECTION_VERSION,
    )
    if not catalog:
        return None

    target_tags, target_valence, target_energy = mood_song_targets(text)
    profile_version = (
        str(SONG_PROFILES_PATH.stat().st_mtime_ns)
        if SONG_PROFILES_PATH.exists()
        else "missing"
    )
    profiles = load_song_profiles(profile_version)
    scored = []
    for song in catalog:
        profile = profiles.get(song_profile_key(song))
        if profile:
            mood_scores = profile.get("mood_scores", {})
            manual_tags = set(song["moods"])
            manual_floor = 0.55 if profile.get("lyrics") else 0.72
            affinities = [
                max(float(mood_scores.get(tag, 0)), manual_floor if tag in manual_tags else 0)
                for tag in target_tags
            ]
            tag_distance = 1 - sum(affinities) / max(1, len(affinities))
            song_valence = float(profile.get("valence", song["valence"]))
            song_energy = float(profile.get("energy", song["energy"]))
        else:
            song_tags = set(song["moods"])
            overlap = len(target_tags & song_tags)
            tag_distance = 1 - overlap / max(1, min(3, len(target_tags)))
            song_valence = float(song["valence"])
            song_energy = float(song["energy"])
        distance = (
            0.46 * tag_distance
            + 0.30 * abs(song_valence - target_valence)
            + 0.24 * abs(song_energy - target_energy)
        )
        scored.append((distance, song))

    scored.sort(key=lambda item: item[0])
    strongest = [song for _, song in scored[:12]]
    seed = int(hashlib.sha256(text.lower().encode("utf-8")).hexdigest()[:12], 16)
    random.Random(seed).shuffle(strongest)
    return strongest[shuffle_count % len(strongest)]


@st.cache_data
def collage_photo_data(collection_version: str, count: int = 60) -> list[str]:
    """Load a random set of approved photos for the animated collage."""
    features = load_photo_features(PHOTO_COLLECTION_VERSION)
    if not features:
        return []
    del collection_version
    selected = random.sample(features, k=min(count, len(features)))
    photo_data = []
    for photo in selected:
        photo_path = PHOTO_PREVIEW_DIR / photo["preview"]
        if photo_path.exists():
            encoded = base64.b64encode(photo_path.read_bytes()).decode("ascii")
            photo_data.append(f"data:image/jpeg;base64,{encoded}")
    return photo_data


def floating_photo_layer(photo_data: list[str]) -> None:
    """Scatter continuously changing photos behind the full app."""
    if not photo_data:
        return

    photos_json = json.dumps(photo_data)
    st.iframe(
        f"""
        <style>
            * {{ box-sizing: border-box; }}
            html, body {{
                background: transparent;
                height: 100%;
                margin: 0;
                overflow: hidden;
                width: 100%;
            }}
            .photo-layer {{ height: 100vh; position: relative; width: 100vw; }}
            .frame {{
                align-items: center;
                background: rgba(239,247,239,.72);
                border: 3px solid rgba(255,255,255,.88);
                box-shadow: 0 18px 42px rgba(45, 62, 48, .18);
                display: flex;
                justify-content: center;
                opacity: .72;
                padding: 10px;
                position: absolute;
                transition: opacity .55s ease, transform .55s ease;
            }}
            .tile {{
                border-radius: 14px;
                height: 84%;
                object-fit: contain;
                opacity: 1;
                transition: opacity .55s ease;
                width: 84%;
            }}
            .circle {{ border-radius: 50%; }}
            .arch {{ border-radius: 48% 48% 22px 22px; }}
            .soft {{ border-radius: 32px 90px 32px 90px; }}
            .blob {{ border-radius: 42% 58% 46% 54% / 55% 42% 58% 45%; }}
            .pill {{ border-radius: 999px; }}
            .rounded {{ border-radius: 30px; }}
            .frame.swapping {{ opacity: .12; transform: scale(.97) !important; }}
            @media (max-width: 760px) {{
                .frame {{ opacity: .38; transform: scale(.72) !important; }}
            }}
        </style>
        <div class="photo-layer" id="photo-layer"></div>
        <script>
            const photos = {photos_json};
            const layer = document.getElementById("photo-layer");
            const tileCount = Math.min(10, photos.length);
            const anchors = [
                [1, 4, 17, 24], [81, 3, 17, 22], [3, 35, 19, 27],
                [78, 36, 20, 25], [1, 70, 18, 25], [80, 69, 18, 26],
                [24, 1, 15, 18], [61, 4, 15, 19], [25, 76, 17, 22],
                [59, 74, 18, 23]
            ];
            const shapes = ["circle", "arch", "soft", "blob", "pill", "rounded"];
            let queue = [];
            let cursor = 0;
            let tileCursor = 0;

            const host = window.frameElement;
            if (host) {{
                host.style.position = "fixed";
                host.style.inset = "0";
                host.style.width = "100vw";
                host.style.height = "100vh";
                host.style.border = "0";
                host.style.pointerEvents = "none";
                host.style.zIndex = "0";
            }}
            try {{
                const main = window.parent.document.querySelector('[data-testid="stMainBlockContainer"]');
                if (main) {{ main.style.position = "relative"; main.style.zIndex = "2"; }}
            }} catch (error) {{}}

            function shuffleQueue() {{
                queue = Array.from({{length: photos.length}}, (_, i) => i);
                for (let i = queue.length - 1; i > 0; i--) {{
                    const j = Math.floor(Math.random() * (i + 1));
                    [queue[i], queue[j]] = [queue[j], queue[i]];
                }}
                cursor = 0;
            }}

            function nextPhoto() {{
                if (cursor >= queue.length) shuffleQueue();
                return photos[queue[cursor++]];
            }}

            shuffleQueue();
            for (let i = 0; i < tileCount; i++) {{
                const frame = document.createElement("div");
                const [left, top, width, height] = anchors[i];
                frame.className = `frame ${{shapes[i % shapes.length]}}`;
                frame.style.left = `${{left + Math.random() * 2 - 1}}vw`;
                frame.style.top = `${{top + Math.random() * 3 - 1.5}}vh`;
                frame.style.width = `${{width}}vw`;
                frame.style.height = `${{height}}vh`;
                const image = document.createElement("img");
                image.className = "tile";
                image.src = nextPhoto();
                image.alt = "A memory of Neenaur";
                frame.style.transform = `rotate(${{(Math.random() * 7 - 3.5).toFixed(1)}}deg)`;
                frame.appendChild(image);
                layer.appendChild(frame);
            }}

            setInterval(() => {{
                const frames = layer.querySelectorAll(".frame");
                if (!frames.length) return;
                const frame = frames[tileCursor % frames.length];
                const tile = frame.querySelector(".tile");
                tileCursor++;
                frame.classList.add("swapping");
                setTimeout(() => {{
                    tile.onload = () => {{
                        frame.style.transform = `rotate(${{(Math.random() * 7 - 3.5).toFixed(1)}}deg)`;
                        frame.classList.remove("swapping");
                    }};
                    tile.src = nextPhoto();
                }}, 450);
            }}, 1900);
        </script>
        """,
        height=1,
    )


if "mood_text" not in st.session_state:
    st.session_state.mood_text = ""
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "shuffle_count" not in st.session_state:
    st.session_state.shuffle_count = 0
if "autoplay_song" not in st.session_state:
    st.session_state.autoplay_song = False
if "player_event_nonce" not in st.session_state:
    st.session_state.player_event_nonce = None


preview_wordles = st.query_params.get("preview_wordles") == "1"
if preview_wordles:
    dallas_now = datetime.now(DISPLAY_TIMEZONE)
    preview_year = dallas_now.year
    if dallas_now.date() > date(preview_year, BIRTH_DATE.month, BIRTH_DATE.day):
        preview_year += 1
    preview_now = datetime(
        preview_year,
        BIRTH_DATE.month,
        BIRTH_DATE.day - 1,
        0,
        1,
        tzinfo=DISPLAY_TIMEZONE,
    )
    birthday_eyebrow, hero_title, birthday_clock_target = birthday_display(preview_now)
else:
    birthday_eyebrow, hero_title, birthday_clock_target = birthday_display()
st.markdown(
    f'<div class="eyebrow">{html.escape(birthday_eyebrow)}</div>',
    unsafe_allow_html=True,
)
if birthday_clock_target:
    with st.container(key="birthday_countdown"):
        live_birthday_countdown(
            birthday_clock_target,
            hero_title,
            preview_seconds=23 * 60 * 60 + 59 * 60 if preview_wordles else None,
        )
else:
    st.markdown(
        f'<div class="hero-title">{html.escape(hero_title)}</div>',
        unsafe_allow_html=True,
    )

if birthday_clock_target:
    gate_id = "preview" if preview_wordles else str(birthday_clock_target.year)
    initialize_wordle_gate(gate_id)
    if preview_wordles:
        st.info("Wordle gate preview. This progress is separate from the real birthday.")
        preview_a, preview_b = st.columns(2, gap="small")
        with preview_a:
            if st.button("Restart preview", key="restart_wordle_preview", width="stretch"):
                st.query_params["wordle_preview"] = "0"
                st.session_state.wordle_gate_id = None
                st.rerun()
        with preview_b:
            if st.button("Exit preview", key="exit_wordle_preview", width="stretch"):
                del st.query_params["preview_wordles"]
                st.session_state.wordle_gate_id = None
                st.rerun()
    gate_is_unlocked = st.session_state.get("wordle_unlocked_gate") == gate_id
    if not gate_is_unlocked:
        render_wordle_gate(gate_id)
        st.stop()
    if st.session_state.get("wordle_just_unlocked"):
        st.session_state.wordle_just_unlocked = False
        st.balloons()
        st.success("All 21 solved. The birthday app is unlocked.")

with st.form("mood_form", clear_on_submit=False):
    mood_text = st.text_area(
        "Your mood",
        value=st.session_state.mood_text,
        placeholder="Maybe: I feel hopeful, but in a quiet Sunday-evening kind of way…",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Find my song  →", width="content")

if submitted:
    if mood_text.strip():
        cleaned_mood = mood_text.strip()
        if cleaned_mood != st.session_state.mood_text:
            st.session_state.shuffle_count = 0
            st.session_state.autoplay_song = False
        st.session_state.mood_text = cleaned_mood
        with st.spinner("Listening for the feeling…"):
            time.sleep(0.65)
        st.session_state.show_result = True
    else:
        st.warning("Write something first. One word is enough.")

# The palette updates during the same rerun as submission, then remains stable
# for shuffle/save interactions until the mood itself changes.
palette = infer_mood_palette(st.session_state.mood_text) if st.session_state.show_result else {
    "start": "#f4f7ef",
    "end": "#dfe9df",
    "glow_one": "rgba(167, 197, 163, .48)",
    "glow_two": "rgba(112, 164, 134, .40)",
    "accent": "#55775f",
    "album_one": "#afc5a5",
    "album_two": "#78977d",
    "album_three": "#496759",
}
st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background:
            radial-gradient(circle at 10% 5%, {palette['glow_one']}, transparent 29rem),
            radial-gradient(circle at 94% 35%, {palette['glow_two']}, transparent 31rem),
            linear-gradient(145deg, {palette['start']} 0%, {palette['end']} 100%);
        transition: background 700ms ease;
    }}
    .eyebrow, .spec-num {{ color: {palette['accent']}; }}
    .album-placeholder {{
        background: linear-gradient(
            145deg,
            {palette['album_one']},
            {palette['album_two']} 48%,
            {palette['album_three']}
        );
    }}
    .song-card {{
        box-shadow:
            0 22px 65px rgba(75, 56, 47, .10),
            0 0 0 1px {palette['glow_one']};
    }}
    .now-playing {{ color: {palette['accent']}; }}
    .st-key-player_controls {{
        background:
            radial-gradient(circle at 8% 0%, {palette['glow_one']}, transparent 55%),
            linear-gradient(135deg, rgba(255,255,255,.78), {palette['glow_two']});
    }}
    .st-key-next_song button {{
        background: linear-gradient(135deg, {palette['album_two']}, {palette['accent']});
        box-shadow: 0 8px 22px {palette['glow_two']};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

floating_photo_layer(collage_photo_data(PHOTO_COLLECTION_VERSION))


if st.session_state.show_result:
    display_vibe = infer_display_vibe(st.session_state.mood_text)
    selected_song = select_mood_song(
        st.session_state.mood_text,
        st.session_state.shuffle_count,
    )

    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="result-label">I read that as</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mood-read">{display_vibe}</div>', unsafe_allow_html=True)

    song_column = st.container()
    with song_column:
        st.markdown('<div class="result-label">Your song for right now</div>', unsafe_allow_html=True)
        if selected_song:
            previous_song = select_mood_song(
                st.session_state.mood_text,
                st.session_state.shuffle_count - 1,
            )
            next_song = select_mood_song(
                st.session_state.mood_text,
                st.session_state.shuffle_count + 1,
            )
            song_title = html.escape(selected_song["title"])
            song_artist = html.escape(selected_song["artist"])
            artwork_uri = album_art_data_uri(selected_song["album"])
            album_visual = (
                f'<div class="album-cover" style="background-image:url(\'{artwork_uri}\')"></div>'
                if artwork_uri
                else '<div class="album-placeholder">✦</div>'
            )
            st.markdown(
                f"""
                <div class="song-card">
                    {album_visual}
                    <div>
                        <div class="song-title">{song_title}</div>
                        <div class="song-artist">{song_artist}</div>
                    </div>
                    <div class="now-playing" aria-label="Now playing">
                        <span></span><span></span><span></span><span></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.container(key="player_controls"):
                player_event = custom_audio_player(
                    selected_song["audio_path"],
                    previous_song["audio_path"] if previous_song else None,
                    next_song["audio_path"] if next_song else None,
                    palette,
                    autoplay=st.session_state.autoplay_song,
                )
                if isinstance(player_event, dict):
                    event_nonce = player_event.get("nonce")
                    event_action = player_event.get("action")
                    if (
                        event_nonce
                        and event_nonce != st.session_state.player_event_nonce
                        and event_action in {"next", "previous"}
                    ):
                        st.session_state.player_event_nonce = event_nonce
                        st.session_state.shuffle_count += (
                            1 if event_action == "next" else -1
                        )
                        st.session_state.autoplay_song = True
                        st.rerun()
                st.session_state.autoplay_song = False
                with st.container(key="player_actions"):
                    action_a, action_b = st.columns(2, gap="small")
                    with action_a:
                        if st.button("Previous song", key="previous_song"):
                            st.session_state.shuffle_count -= 1
                            st.session_state.autoplay_song = True
                            st.rerun()
                    with action_b:
                        if st.button("Next song", key="next_song"):
                            st.session_state.shuffle_count += 1
                            st.session_state.autoplay_song = True
                            st.rerun()
        else:
            st.info("Add the song catalog to see a mood match.")
