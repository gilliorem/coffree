"""Load local environment variables for the prototype."""

from __future__ import annotations


def load_local_env() -> None:
    """Load .env when python-dotenv is installed.

    The app still starts without python-dotenv.
    In that case, keys must already be exported in the terminal.
    """
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        return

    load_dotenv()
