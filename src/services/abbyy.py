"""Async ABBYY Vantage client.

Implements the documented single-call workflow for one file under 30 MB:
OAuth client-credentials token, transaction launch, status polling, and result
file download. The client is dependency-injection friendly for tests.
"""
import asyncio
import time
from typing import Any
import httpx
from src.core.config import get_settings

class AbbyyError(RuntimeError): pass

def extract_ocr_text(parsed: dict) -> str:
    """Join line text from a Vantage OcrJson result (layout.pages[].texts[].lines[].text)."""
    pages = (parsed.get("layout") or {}).get("pages") or []
    page_parts: list[str] = []
    for page in pages:
        line_parts = [line.get("text", "") for text_block in page.get("texts", []) for line in text_block.get("lines", [])]
        page_parts.append("\n".join(part for part in line_parts if part))
    if page_parts: return "\n\n".join(part for part in page_parts if part)
    return parsed.get("text") or parsed.get("content") or ""

class AbbyyVantageClient:
    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self.settings = get_settings()
        self.http = http_client or httpx.AsyncClient(timeout=60)
        self._owns_client = http_client is None
        self.base = self.settings.abbyy_base_url.rstrip("/")

    async def close(self):
        if self._owns_client: await self.http.aclose()

    async def get_token(self) -> str:
        response = await self.http.post(f"{self.base}/auth2/connect/token", data={"grant_type":"client_credentials", "scope":"openid permissions global.wildcard", "client_id":self.settings.abbyy_client_id, "client_secret":self.settings.abbyy_client_secret})
        if response.is_error: raise AbbyyError(f"ABBYY token request failed: {response.status_code} {response.text[:500]}")
        token = response.json().get("access_token")
        if not token: raise AbbyyError("ABBYY token response did not include access_token")
        return token

    async def list_skills(self, token: str) -> list[dict[str, Any]]:
        response = await self.http.get(f"{self.base}/api/publicapi/v1/skills", headers={"Authorization": f"Bearer {token}"})
        if response.is_error: raise AbbyyError(f"ABBYY skills request failed: {response.status_code}")
        body = response.json(); return body if isinstance(body, list) else body.get("skills", body.get("items", []))

    async def launch(self, token: str, content: bytes, file_name: str, mime_type: str | None, skill_id: str) -> str:
        if len(content) >= 30 * 1024 * 1024: raise AbbyyError("ABBYY single-call launch supports files smaller than 30 MB")
        response = await self.http.post(f"{self.base}/api/publicapi/v1/transactions/launch", params={"skillId": skill_id}, headers={"Authorization": f"Bearer {token}"}, files={"files": (file_name, content, mime_type or "application/octet-stream")})
        if response.is_error: raise AbbyyError(f"ABBYY transaction launch failed: {response.status_code} {response.text[:500]}")
        transaction_id = response.json().get("id") or response.json().get("transactionId")
        if not transaction_id: raise AbbyyError("ABBYY launch response did not include transaction id")
        return transaction_id

    async def launch_separate(self, token: str, content: bytes, file_name: str, mime_type: str | None, skill_id: str) -> str:
        """Separate-call workflow for large files: create, upload, then start."""
        response = await self.http.post(f"{self.base}/api/publicapi/v1/transactions", headers={"Authorization": f"Bearer {token}"}, json={"skillId": skill_id})
        if response.is_error: raise AbbyyError(f"ABBYY transaction creation failed: {response.status_code}")
        transaction_id = response.json().get("id") or response.json().get("transactionId")
        if not transaction_id: raise AbbyyError("ABBYY transaction creation did not include transaction id")
        upload = await self.http.post(f"{self.base}/api/publicapi/v1/transactions/{transaction_id}/files", headers={"Authorization": f"Bearer {token}"}, files={"files": (file_name, content, mime_type or "application/octet-stream")})
        if upload.is_error: raise AbbyyError(f"ABBYY file upload failed: {upload.status_code}")
        start = await self.http.post(f"{self.base}/api/publicapi/v1/transactions/{transaction_id}/start", headers={"Authorization": f"Bearer {token}"})
        if start.is_error: raise AbbyyError(f"ABBYY transaction start failed: {start.status_code}")
        return transaction_id

    async def transaction(self, token: str, transaction_id: str) -> dict[str, Any]:
        response = await self.http.get(f"{self.base}/api/publicapi/v1/transactions/{transaction_id}", headers={"Authorization": f"Bearer {token}"})
        if response.is_error: raise AbbyyError(f"ABBYY transaction status failed: {response.status_code}")
        return response.json()

    async def wait_for_completion(self, token: str, transaction_id: str) -> dict[str, Any]:
        deadline = time.monotonic() + self.settings.abbyy_poll_timeout_seconds
        terminal = {"Processed", "ProcessedWithWarnings", "NotProcessed", "Deleted"}
        while time.monotonic() < deadline:
            result = await self.transaction(token, transaction_id)
            status = result.get("status") or result.get("state")
            if status in terminal: return result
            await asyncio.sleep(self.settings.abbyy_poll_interval_seconds)
        raise AbbyyError("ABBYY transaction polling timed out")

    async def download_result_files(self, token: str, transaction_id: str, transaction: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Download the OCR result files from a completed transaction.

        ABBYY's transaction endpoint contains ``documents[].resultFiles``. The
        similarly named ``/documents`` endpoint contains only ``sourceFiles``
        for the OCR skill, so using it silently produced no extracted text.
        """
        if transaction is None:
            transaction = await self.transaction(token, transaction_id)
        documents = transaction.get("documents", [])
        if not documents:
            raise AbbyyError("ABBYY completed the transaction but returned no result documents")
        results: list[dict[str, Any]] = []
        for document in documents:
            for file_info in document.get("resultFiles", document.get("files", [])):
                file_id = file_info.get("id") or file_info.get("fileId")
                if not file_id: continue
                download = await self.http.get(f"{self.base}/api/publicapi/v1/transactions/{transaction_id}/files/{file_id}/download", headers={"Authorization": f"Bearer {token}"})
                if download.is_error: raise AbbyyError(f"ABBYY result download failed: {download.status_code}")
                results.append({"file_id": file_id, "file_name": file_info.get("name") or file_info.get("fileName", "result"), "content": download.content, "content_type": download.headers.get("content-type")})
        if not results:
            raise AbbyyError("ABBYY completed the transaction but returned no OCR result files")
        return results
