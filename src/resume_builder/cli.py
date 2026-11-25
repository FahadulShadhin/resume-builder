from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ValidationError

from resume_builder.drive import upload_pdf_to_drive
from resume_builder.models import Resume
from resume_builder.pdf import build_pdf
from resume_builder.progress import ProgressBar


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Generate a polished PDF resume from validated JSON data."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/resume.json"),
        help="Path to the resume JSON file (default: data/resume.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/resume.pdf"),
        help="Path for the generated PDF (default: output/resume.pdf)",
    )
    parser.add_argument(
        "--no-drive",
        action="store_true",
        help="Skip uploading the generated resume to Google Drive",
    )
    args = parser.parse_args()

    drive_link: str | None = None
    try:
        resume = Resume.model_validate_json(args.input.read_text(encoding="utf-8"))

        with ProgressBar("Generating resume") as progress:
            build_pdf(resume, args.output)
            progress.update()

        if not args.no_drive:
            with ProgressBar("Uploading resume") as progress:
                drive_link = upload_pdf_to_drive(args.output)
                progress.update()
    except FileNotFoundError as error:
        parser.error(f"File not found: {error.filename}")
    except (ValidationError, json.JSONDecodeError) as error:
        print(f"Invalid resume JSON in {args.input}:\n{error}", file=sys.stderr)
        raise SystemExit(2) from error
    except ValueError as error:
        parser.error(str(error))

    print(f"Generated {args.output}")
    if drive_link:
        print(f"Uploaded to Google Drive: {drive_link}")
