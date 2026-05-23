1. Activate venv:
    windows: `.venv\Scripts\Activate`

2. Run tests:
    `uv run python -m pytest`

Note: use `python -m pytest` with `uv run` in this repo so the project root is on Python's import path and imports like `from src...` resolve correctly.
