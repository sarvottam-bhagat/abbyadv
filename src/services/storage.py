from src.core.config import get_settings
from supabase import create_client
from uuid import uuid4
class StorageService:
    def __init__(self):
        self.settings = get_settings()
        self.client = create_client(self.settings.supabase_url, self.settings.supabase_service_role_key) if self.settings.supabase_url and self.settings.supabase_service_role_key else None
    def key(self, user_id: str, case_id: str, file_name: str) -> str:
        """Create a collision-safe key so every selected file is retained."""
        safe_name = file_name.replace("/", "_").replace("\\", "_")
        return f"{user_id}/{case_id}/{uuid4().hex}-{safe_name}"
    async def upload_url(self, key: str) -> str:
        if self.client:
            result = self.client.storage.from_(self.settings.upload_bucket).create_signed_upload_url(key)
            return result.get("signed_url") or result.get("signedUrl") or result.get("signedURL") or str(result)
        return f"/local-upload/{key}"
    async def download(self, key: str) -> bytes:
        if not self.client: raise RuntimeError("Supabase Storage is not configured; cannot download uploaded content")
        return self.client.storage.from_(self.settings.upload_bucket).download(key)
    async def upload_bytes(self, key: str, content: bytes, content_type: str = "application/octet-stream") -> str:
        if not self.client: raise RuntimeError("Supabase Storage is not configured; cannot upload generated content")
        self.client.storage.from_(self.settings.upload_bucket).upload(key, content, {"content-type": content_type, "upsert": "true"})
        return key
    async def signed_download_url(self, key: str, expires_in: int = 3600) -> str:
        if not self.client: raise RuntimeError("Supabase Storage is not configured; cannot create download URL")
        result = self.client.storage.from_(self.settings.upload_bucket).create_signed_url(key, expires_in)
        return result.get("signedURL") or result.get("signedUrl") or result.get("signed_url") or str(result)
