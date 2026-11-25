from __future__ import annotations

import argparse
import json
import sys

from pydantic import ValidationError

from src.drive import upload_pdf_to_drive
from src.models import Resume
from src.pdf import build_pdf
from src.progress import ProgressBar
from src.variables import INPUT_PATH, OUTPUT_PATH


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a polished PDF resume from validated JSON data."
    )
    parser.add_argument(
        "--no-drive",
        action="store_true",
        help="Skip uploading the generated resume to Google Drive",
    )
    args = parser.parse_args()

    drive_link: str | None = None
    try:
        resume = Resume.model_validate_json(INPUT_PATH.read_text(encoding="utf-8"))

        with ProgressBar("Generating resume") as progress:
            build_pdf(resume, OUTPUT_PATH)
            progress.update()

        if not args.no_drive:
            with ProgressBar("Uploading resume") as progress:
                drive_link = upload_pdf_to_drive(OUTPUT_PATH)
                progress.update()
    except FileNotFoundError as error:
        parser.error(f"File not found: {error.filename}")
    except (ValidationError, json.JSONDecodeError) as error:
        print(f"Invalid resume JSON in {INPUT_PATH}:\n{error}", file=sys.stderr)
        raise SystemExit(2) from error
    except ValueError as error:
        parser.error(str(error))

    print(f"Generated {OUTPUT_PATH}")
    if drive_link:
        print(f"Uploaded to Google Drive: {drive_link}")
