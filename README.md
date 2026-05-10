# Coffree — SUTD Daily Free Coffee Bot

*Submitted to the SUTD Academy AI Task Force — B1 Builders Programme.*

![coffree meme](./womencoffee.gif)


## Overview

### Problem
- **Who:** SUTD students who miss out on the free coffee left over after daily APM workshops.
- **Issue:** Workshop F&B is provided across the campus every weekday. By mid-morning, surplus coffee is still available but only the APMs know where. Students waste time hunting, and a lot of coffee is thrown away.

### Outcome
- A Telegram bot, **@SUTD_coffree_bot**, that tells any student where to grab today's free coffee in one tap.
- Reads the shared APM workshop schedule (CSV mirror of the SharePoint sheet), filters out remote/offsite rows, and pushes a daily morning prompt to subscribers.
- Prototype currently covers the 12 most-used campus rooms with photo-guided directions.

---

## Demo

User journey when a student first opens a chat with the bot:

1. `/start` → Bot greets the student and asks "Where are you heading next?" with 4 buttons:
   - `Building 1` · `Building 2` · `Level 4 and above` · `Just give me the coffee location already!`
2. Buttons 1–3 → Bot returns one recommended coffee location (`class_id`, name, building, level) plus a "Get directions to this class" button and "Get all coffee locations" fallback.
3. Button 4 → Bullet list of every free-coffee location for today, each with its own "Need directions" button.
4. Tapping a directions button → Bot sends the photo sequence walking the student from the main entry to the room, ending with `buffet.png` and the closing line *"Enjoy your Free Coffee, Coffree. ☕"*.

Daily routine (08:30 SGT, weekdays):
- Bot asks each subscriber *"Good morning {name}, do you want me to check for free coffee today?"* (`YES` / `NO`).
- `YES` → top 2 locations + a "More coffee locations" button.
- `NO` → *"Alright, have a good day!"*.

![demo](./screenRecording.gif)


---

## Technology Stack

### Frontend
- **Telegram Bot API** via `python-telegram-bot` 21+ (inline keyboards, photo and media-group replies).

### Backend
- **Python 3.10+** for parsing, formatting and orchestration.
- **CSV schedule** (`data/PM_Schedule.csv`) — local export of the APM SharePoint sheet, parsed once and re-read only when the file changes.
- **Local JSON store** (`data/location-hints.json`, `data/subscribers.json`) for per-room metadata and subscriber state.
- **`python-telegram-bot[job-queue]`** for the daily 08:30 SGT cron-style job (Mon–Fri only, skipped when the CSV has no physical room for the day).
- **`python-dotenv`** for loading `.env`.

---

## Development Approach with AI

### AI tools & models
- **Claude (Sonnet / Opus)** — main pair-programmer for parser, formatter, recommender and tests.
- **ChatGPT** — quick prompt iteration on tone of bot replies.
- **GitHub Copilot** — inline completion while writing tests.

### AI agents / roles
- **Architect** — broke the brief into modules (`parser`, `bot`, `scheduler`, `recommender`).
- **Implementer** — wrote each module from a one-paragraph spec.
- **Tester** — generated `pytest` cases from the parser edge cases listed in `AGENTS.md`.
- **Reviewer** — flagged dead code, naming and message tone.

### Key prompts
- "Parse a row of `WORKSHOP | LOCATION | APM | APM | APM` repeated N times; ignore Zoom / Offsite / blanks; return unique physical rooms."
- "Given a student's destination (Building X Level Y), score every coffee location and return the closest one."
- "Rewrite this Telegram reply so it feels like a human friend, not a service notification."

### Key review decisions
- **Skip SharePoint API** for the prototype → use a local CSV mirror. Rationale: faster iteration, no auth dance for the demo.
- **Hard-code the 12 known rooms** in `data/location-hints.json` rather than scraping. Rationale: rooms rarely change and we want photo-guided directions.
- **Use `python-telegram-bot`'s built-in `JobQueue`** instead of an external scheduler. Rationale: one process, one deploy.
- **Make the bot conversational** (greeting + emoji + photo) instead of a dry list. Rationale: hooks the student on first contact.

---

## Installation

```bash
git clone <repo-url> coffree
cd coffree
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # then paste your TELEGRAM_BOT_TOKEN
```

`.env` keys:
```bash
TELEGRAM_BOT_TOKEN=...
COFFREE_DAILY_TIME=08:30
COFFREE_SUBSCRIBERS_FILE=data/subscribers.json
# COFFREE_DATE=8-May-26    # optional — pin "today" for local testing
```

---

## Usage

Run the bot:
```bash
python -m src.telegram_bot
```

Run the test suite:
```bash
pytest
```

Telegram commands:
- `/start` — subscribe and see the onboarding flow.
- `/today` — get today's coffee answer immediately.
- `/stop` — unsubscribe from daily updates.

Free-text questions like *"where can I get free coffee tomorrow"* or *"directions to TT24/25"* are also understood.

---

## Project Structure

```text
coffree/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── telegram_bot.py        # Telegram entrypoint, command + button handlers
│   ├── scheduler.py           # Daily 08:30 SGT job
│   ├── subscribers.py         # JSON-backed subscriber store
│   ├── read_schedule.py       # CSV reader
│   ├── find_coffee_classes.py # Filter physical classrooms from the schedule
│   ├── schedule_dates.py      # today / tomorrow date helpers
│   ├── student_destination.py # Parse "Building 2 Level 5", "TT24/25", "2.612A"
│   ├── recommend_coffee.py    # Score and rank locations vs. destination
│   ├── location_hints.py      # JSON profiles + direction-photo lookup
│   ├── format_message.py      # All user-facing strings
│   └── load_env.py
├── tests/                     # pytest suite, one file per src module
└── data/
    ├── PM_Schedule.csv        # Local mirror of the APM workshop sheet
    ├── location-hints.json    # 12 known rooms (building, level, hint, photos)
    └── class-direction-photo/ # Photo sequences walking to each room
```

---

## Reflection

**What worked**
- Splitting parser, recommender and bot into independent modules made AI-assisted edits safe — each prompt only needed one file's context.
- A local CSV instead of the live SharePoint API unblocked end-to-end demos in hours.
- Heavy `pytest` coverage on the parser caught every spreadsheet edge case (`Zoom`, `Offsite`, `2.612A`, `TT24/25`).

**What failed / changed**
- First version dumped a raw room name. User testing was flat — students didn't know where `TT24/25` was. Added `location-hints.json` + photo-guided directions.
- Initial daily job ran every day; rewritten to weekdays-only and to skip mornings with no physical room in the CSV.
- Tone iteration: "Coffee available at TT24/25" → *"Good morning Remi! Craving coffee right now? I got you. ☕"* — feels human, gets replies.

**Open follow-ups**
- Replace CSV mirror with the SharePoint Graph API.
- Add a hero photo / GIF demo to this README.
- Wire the SUTD-wide room list (currently 12) to the full classroom directory.
