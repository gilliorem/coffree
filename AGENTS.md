# Repository Guidelines

## Project Structure & Module Organization

This repository currently contains the project brief in `README.md`. The intended product is a Telegram bot that sends SUTD students daily free-coffee locations parsed from a SharePoint/Excel workshop schedule.

Use this structure as implementation starts:

```text
src/
  parser.py        # Extract and normalize coffee locations from CSV/Excel data
  bot.py           # Telegram command handlers and message delivery
  scheduler.py     # Daily notification job
  config.py        # Environment variable loading and validation
tests/
  test_parser.py   # Parser behavior and edge cases
data/
  sample_schedule.csv
```

Keep sample data small and anonymized. Do not commit real credentials, bot tokens, or private SharePoint exports.

## Build, Test, and Development Commands

No build system is committed yet. When Python code is added, prefer these commands:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
python -m src.bot
```

`pytest` should run the test suite. `python -m src.bot` should start the Telegram bot locally after required environment variables are configured.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation, type hints for public functions, and clear snake_case names. Keep modules small and focused: parsing logic should not depend on Telegram APIs, and bot handlers should not parse raw spreadsheet rows directly.

Name parser helpers by behavior, for example `extract_locations`, `normalize_location`, and `is_ignored_location`. Keep configuration names uppercase in environment variables, such as `TELEGRAM_BOT_TOKEN`.

## Testing Guidelines

Use `pytest` for tests. Focus first on parser coverage because spreadsheet rows are inconsistent. Test files should be named `test_*.py`, and tests should describe behavior:

```python
def test_extracts_tt_locations_from_mixed_row():
    ...
```

Include cases for `TT19`, `TT24/25`, `Comp LAB`, room numbers like `2.612A`, and ignored values such as `Zoom`, `Offsite`, blanks, workshop names, and APM names.

## Commit & Pull Request Guidelines

The existing git history uses short plain-English commits such as `updated README` and `First commit: Add README.md`. Continue with concise imperative messages, for example `Add schedule parser tests`.

Pull requests should include a short summary, test results, linked issue or task context when available, and screenshots or sample Telegram messages for bot-facing changes. Mention any data-source assumptions, especially SharePoint access, CSV format, or schedule-column parsing rules.

## Security & Configuration Tips

Store secrets in environment variables or a local `.env` file excluded by `.gitignore`. Required secrets will likely include `TELEGRAM_BOT_TOKEN` and, later, SharePoint or Microsoft Graph credentials. Avoid logging raw spreadsheet rows if they contain names or private event details.
