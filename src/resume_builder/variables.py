from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Single source of truth for project variables; secrets are read from `.env`
# (real environment variables take precedence over `.env` values).
load_dotenv()

GOOGLE_DRIVE_CLIENT_ID: str | None = os.environ.get("GOOGLE_DRIVE_CLIENT_ID")
GOOGLE_DRIVE_CLIENT_SECRET: str | None = os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET")
GOOGLE_DRIVE_TOKEN_PATH: str = os.environ.get("GOOGLE_DRIVE_TOKEN_PATH", "token.json")

DRIVE_SCOPES: list[str] = ["https://www.googleapis.com/auth/drive.file"]
DEFAULT_DRIVE_FILE_NAME: str = "Fahadul_Islam_Shadhin_Resume.pdf"

INPUT_PATH: Path = Path("data/resume.json")
OUTPUT_PATH: Path = Path("output/resume.pdf")
