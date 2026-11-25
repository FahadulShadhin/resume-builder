from __future__ import annotations

import io
import unittest
from unittest.mock import patch

from resume_builder.progress import ProgressBar


class ProgressBarTests(unittest.TestCase):
    def test_finish_prints_completion_line(self) -> None:
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            progress = ProgressBar("Generating resume")
            progress.update()
            progress.finish()

        self.assertIn("Generating resume", stdout.getvalue())
        self.assertIn("✓", stdout.getvalue())

    def test_finish_only_prints_once(self) -> None:
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            progress = ProgressBar("Uploading resume")
            progress.finish()
            progress.finish()

        self.assertEqual(stdout.getvalue().count("✓"), 1)

    def test_context_manager_finishes_on_success(self) -> None:
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with ProgressBar("Generating resume") as progress:
                progress.update()

        self.assertIn("✓", stdout.getvalue())

    def test_context_manager_does_not_finish_on_error(self) -> None:
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(RuntimeError):
                with ProgressBar("Generating resume") as progress:
                    progress.update()
                    raise RuntimeError("boom")

        self.assertNotIn("✓", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
