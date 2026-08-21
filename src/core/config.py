from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "AbbyAdv API"
    debug: bool = False
    auto_create_schema: bool = False
    database_url: str = "sqlite+aiosqlite:///./abbyadv.db"
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""
    supabase_publishable_key: str = ""
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "abbyadv_documents"
    upload_bucket: str = "case-documents"
    embedding_dimension: int = 1536
    abbyy_base_url: str = "https://vantage-au.abbyy.com"
    abbyy_client_id: str = ""
    abbyy_client_secret: str = ""
    abbyy_skill_id: str = ""
    abbyy_poll_interval_seconds: float = 1.0
    abbyy_poll_timeout_seconds: float = 300.0
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    indian_kanoon_api_token: str = ""
    ecourts_api_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_production(self) -> None:
        if self.debug: return
        required = {"SUPABASE_URL": self.supabase_url, "SUPABASE_PUBLISHABLE_KEY": self.supabase_publishable_key, "SUPABASE_SERVICE_ROLE_KEY": self.supabase_service_role_key, "DATABASE_URL": self.database_url}
        missing = [name for name, value in required.items() if not value]
        if missing: raise RuntimeError(f"Missing production configuration: {', '.join(missing)}")

@lru_cache
def get_settings() -> Settings:
    return Settings()
