from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from resume_builder import drive, variables


class DriveTests(unittest.TestCase):
    def _pdf_path(self, temp_dir: str) -> Path:
        pdf_path = Path(temp_dir) / "resume.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake pdf bytes")
        return pdf_path

    def test_upload_pdf_to_drive_returns_web_link(self) -> None:
        service = MagicMock()
        service.files.return_value.list.return_value.execute.return_value = {"files": []}
        service.files.return_value.create.return_value.execute.return_value = {
            "id": "drive-file-id",
            "name": variables.DEFAULT_DRIVE_FILE_NAME,
            "mimeType": "application/pdf",
            "webViewLink": "https://drive.google.com/file/d/drive-file-id/view",
        }

        with TemporaryDirectory() as temp_dir:
            pdf_path = self._pdf_path(temp_dir)

            with patch.object(drive, "get_drive_service", return_value=service):
                link = drive.upload_pdf_to_drive(pdf_path)

        self.assertEqual(link, "https://drive.google.com/file/d/drive-file-id/view")
        create = service.files.return_value.create
        self.assertEqual(create.call_count, 1)
        self.assertEqual(
            create.call_args.kwargs["body"]["name"],
            variables.DEFAULT_DRIVE_FILE_NAME,
        )

    def test_upload_pdf_to_drive_replaces_existing_file(self) -> None:
        service = MagicMock()
        service.files.return_value.list.return_value.execute.return_value = {
            "files": [{"id": "existing-file-id", "name": variables.DEFAULT_DRIVE_FILE_NAME}]
        }
        service.files.return_value.update.return_value.execute.return_value = {
            "id": "existing-file-id",
            "name": variables.DEFAULT_DRIVE_FILE_NAME,
            "mimeType": "application/pdf",
            "webViewLink": "https://drive.google.com/file/d/existing-file-id/view",
        }

        with TemporaryDirectory() as temp_dir:
            pdf_path = self._pdf_path(temp_dir)

            with patch.object(drive, "get_drive_service", return_value=service):
                link = drive.upload_pdf_to_drive(pdf_path)

        self.assertEqual(link, "https://drive.google.com/file/d/existing-file-id/view")
        update = service.files.return_value.update
        self.assertEqual(update.call_count, 1)
        self.assertEqual(update.call_args.kwargs["fileId"], "existing-file-id")
        self.assertEqual(service.files.return_value.create.call_count, 0)

    def test_get_drive_credentials_requires_oauth_client(self) -> None:
        with patch.object(variables, "GOOGLE_DRIVE_CLIENT_ID", ""), patch.object(
            variables, "GOOGLE_DRIVE_CLIENT_SECRET", ""
        ):
            with self.assertRaises(ValueError):
                drive.get_drive_credentials()


if __name__ == "__main__":
    unittest.main()
