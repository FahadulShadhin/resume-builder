from __future__ import annotations

import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError

from resume_builder.models import Resume
from resume_builder.pdf import build_pdf

ROOT = Path(__file__).resolve().parents[1]


class ResumeBuilderTests(unittest.TestCase):
    def test_builds_single_page_pdf_from_sample_data(self) -> None:
        resume = Resume.model_validate_json((ROOT / "data/resume.json").read_text())

        self.assertEqual(len(resume.experience), 3)
        self.assertEqual(resume.settings.section_order[0], "professional_summary")

        with TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "resume.pdf"
            build_pdf(resume, output)
            contents = output.read_bytes()

        self.assertTrue(contents.startswith(b"%PDF-"))
        self.assertEqual(len(re.findall(rb"/Type\s*/Page\b", contents)), 1)

    def test_rejects_unknown_resume_fields(self) -> None:
        with self.assertRaises(ValidationError):
            Resume.model_validate({"personal_info": {"name": "A", "unexpected": True}})

    def test_single_page_setting_rejects_overflow_without_writing_output(self) -> None:
        resume = Resume.model_validate_json((ROOT / "data/resume.json").read_text())
        resume.summary = "Resume summary. " * 500

        with TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "resume.pdf"
            with self.assertRaisesRegex(ValueError, "single_page is true"):
                build_pdf(resume, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
