"""Simple Python SDK for MedAnalyzer REST API.

This minimal client provides convenience wrappers around the common
endpoints: sessions, messages, and reports. It is intentionally small
and dependency-light (requests only).

Usage:
    from sdk.medanalyzer_client import MedAnalyzerClient

    client = MedAnalyzerClient(base_url="http://localhost:8000", api_key=None)
    session = client.create_session("My API session")
    client.send_message(session_id=session["id"], content="Please review this report")

"""
from __future__ import annotations
import requests
from typing import Optional, Dict, Any, List


class APIError(Exception):
    pass


class MedAnalyzerClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.timeout = timeout
        if api_key:
            # Support simple Bearer token auth if provided
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    # Sessions
    def list_sessions(self) -> List[Dict[str, Any]]:
        resp = self.session.get(f"{self.base_url}/api/v1/chat/sessions", timeout=self.timeout)
        return self._handle(resp)

    def create_session(self, title: str = "New Session") -> Dict[str, Any]:
        resp = self.session.post(f"{self.base_url}/api/v1/chat/sessions", json={"title": title}, timeout=self.timeout)
        return self._handle(resp)

    def get_session(self, session_id: int) -> Dict[str, Any]:
        resp = self.session.get(f"{self.base_url}/api/v1/chat/sessions/{session_id}", timeout=self.timeout)
        return self._handle(resp)

    def rename_session(self, session_id: int, title: str) -> Dict[str, Any]:
        resp = self.session.patch(f"{self.base_url}/api/v1/chat/sessions/{session_id}", json={"title": title}, timeout=self.timeout)
        return self._handle(resp)

    def delete_session(self, session_id: int) -> Dict[str, Any]:
        resp = self.session.delete(f"{self.base_url}/api/v1/chat/sessions/{session_id}", timeout=self.timeout)
        return self._handle(resp)

    # Messages
    def send_message(self, session_id: int, content: str, audience: str = "patient", file_path: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/chat/sessions/{session_id}/messages"
        if file_path:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.split('/')[-1], f)}
                data = {"content": content, "audience": audience}
                resp = self.session.post(url, data=data, files=files, timeout=self.timeout)
                return self._handle(resp)
        else:
            data = {"content": content, "audience": audience}
            resp = self.session.post(url, data=data, timeout=self.timeout)
            return self._handle(resp)

    # Reports (text-only endpoint)
    def upload_text_report(self, text: str, language: str = "en") -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/reports/upload-text"
        resp = self.session.post(url, json={"text": text, "language": language}, timeout=self.timeout)
        return self._handle(resp)

    def upload_file_report(self, file_path: str, language: str = "en") -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/reports/upload-file"
        with open(file_path, "rb") as f:
            files = {"file": (file_path.split('/')[-1], f)}
            data = {"language": language}
            resp = self.session.post(url, data=data, files=files, timeout=self.timeout)
            return self._handle(resp)

    def list_reports(self) -> List[Dict[str, Any]]:
        resp = self.session.get(f"{self.base_url}/api/v1/reports/", timeout=self.timeout)
        return self._handle(resp)

    def get_report(self, report_id: int) -> Dict[str, Any]:
        resp = self.session.get(f"{self.base_url}/api/v1/reports/{report_id}", timeout=self.timeout)
        return self._handle(resp)

    # Helpers
    def _handle(self, resp: requests.Response) -> Any:
        try:
            content = resp.json()
        except Exception:
            content = resp.text
        if not resp.ok:
            raise APIError(f"{resp.status_code} {resp.reason}: {content}")
        return content
