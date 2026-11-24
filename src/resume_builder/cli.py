from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from resume_builder.models import Resume
from resume_builder.pdf import build_pdf


def main() -> None:
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
    args = parser.parse_args()

    try:
        resume = Resume.model_validate_json(args.input.read_text(encoding="utf-8"))
        build_pdf(resume, args.output)
    except FileNotFoundError as error:
        parser.error(f"File not found: {error.filename}")
    except (ValidationError, json.JSONDecodeError) as error:
        print(f"Invalid resume JSON in {args.input}:\n{error}", file=sys.stderr)
        raise SystemExit(2) from error
    except ValueError as error:
        parser.error(str(error))

    print(f"Generated {args.output}")
