from __future__ import annotations

from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from src import variables


def get_drive_credentials() -> Credentials:
    client_id = variables.GOOGLE_DRIVE_CLIENT_ID
    client_secret = variables.GOOGLE_DRIVE_CLIENT_SECRET
    if not client_id or not client_secret:
        raise ValueError(
            "Google Drive upload failed: OAuth client credentials are not configured. "
            "Set the GOOGLE_DRIVE_CLIENT_ID and GOOGLE_DRIVE_CLIENT_SECRET environment "
            "variables for your Google Cloud OAuth 2.0 Desktop client."
        )

    token_path = Path(variables.GOOGLE_DRIVE_TOKEN_PATH)
    credentials: Credentials | None = None
    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(token_path, scopes=variables.DRIVE_SCOPES)

    if credentials is None or not credentials.valid:
        if credentials is not None and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        if credentials is None or not credentials.valid:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost:8080/"],
                    }
                },
                scopes=variables.DRIVE_SCOPES,
            )
            credentials = flow.run_local_server(port=0)
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(credentials.to_json(), encoding="utf-8")

    return credentials


def get_drive_service() -> Any:
    credentials = get_drive_credentials()
    return build("drive", "v3", credentials=credentials)


def _find_drive_file(service: Any, file_name: str) -> str | None:
    try:
        result = (
            service.files()
            .list(
                q=f"name='{file_name}' and trashed=false",
                pageSize=1,
                fields="files(id,name)",
            )
            .execute()
        )
    except HttpError as error:
        raise ValueError(f"Google Drive upload failed: {error}") from error

    files = result.get("files", [])
    return files[0]["id"] if files else None


def upload_pdf_to_drive(
    file_path: Path, file_name: str = variables.DEFAULT_DRIVE_FILE_NAME
) -> str:
    try:
        service = get_drive_service()
        media = MediaFileUpload(str(file_path), mimetype="application/pdf")
        existing_file_id = _find_drive_file(service, file_name)

        if existing_file_id:
            created = (
                service.files()
                .update(
                    fileId=existing_file_id,
                    media_body=media,
                    fields="id,name,mimeType,webViewLink",
                )
                .execute()
            )
        else:
            created = (
                service.files()
                .create(
                    body={"name": file_name, "mimeType": "application/pdf"},
                    media_body=media,
                    fields="id,name,mimeType,webViewLink",
                )
                .execute()
            )
    except HttpError as error:
        raise ValueError(f"Google Drive upload failed: {error}") from error

    return created.get("webViewLink") or f"https://drive.google.com/file/d/{created.get('id')}/view"
