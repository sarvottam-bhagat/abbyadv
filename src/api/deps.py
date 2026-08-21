import asyncio
from time import monotonic

from fastapi import Depends, Header, HTTPException
from jose import jwt, JWTError
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import get_settings
from src.database.base import get_db
from src.database.models import User


# Supabase's /auth/v1/user endpoint is the authoritative token check when no
# JWT secret is configured. Cache only successfully verified claims briefly so
# a page that makes several API calls does not wait on the same network trip.
_AUTH_CACHE_TTL_SECONDS = 30.0
_auth_cache: dict[str, tuple[float, str, str | None]] = {}
_auth_cache_lock = asyncio.Lock()


async def _verified_supabase_claims(token: str, settings) -> tuple[str, str | None]:
    now = monotonic()
    cached = _auth_cache.get(token)
    if cached and cached[0] > now:
        return cached[1], cached[2]

    # Prevent the clients/sessions bootstrap requests from both validating the
    # same bearer token at once during an initial page load.
    async with _auth_cache_lock:
        now = monotonic()
        cached = _auth_cache.get(token)
        if cached and cached[0] > now:
            return cached[1], cached[2]
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
                    headers={"apikey": settings.supabase_publishable_key, "Authorization": f"Bearer {token}"},
                )
        except httpx.HTTPError as exc:
            raise HTTPException(503, "Supabase Auth is unavailable") from exc
        if response.status_code != 200:
            raise HTTPException(401, "Invalid Supabase token")
        claims = response.json()
        auth_id = claims.get("id") or claims.get("sub")
        if not auth_id:
            raise HTTPException(401, "Supabase user response did not include an id")
        email = claims.get("email")
        _auth_cache[token] = (now + _AUTH_CACHE_TTL_SECONDS, auth_id, email)
        if len(_auth_cache) > 256:
            for cached_token, (expires_at, _, _) in list(_auth_cache.items()):
                if expires_at <= now:
                    _auth_cache.pop(cached_token, None)
        return auth_id, email


async def get_current_user(authorization: str | None = Header(None), x_user_id: str | None = Header(None), db: AsyncSession = Depends(get_db)) -> User:
    settings = get_settings(); auth_id = None; email = None
    if authorization and authorization.lower().startswith("bearer ") and settings.supabase_url and settings.supabase_publishable_key:
        token = authorization[7:]
        auth_id, email = await _verified_supabase_claims(token, settings)
    elif authorization and authorization.lower().startswith("bearer ") and settings.supabase_jwt_secret:
        try:
            claims = jwt.decode(authorization[7:], settings.supabase_jwt_secret, algorithms=["HS256"], options={"verify_aud": False}); auth_id = claims.get("sub"); email = claims.get("email")
        except JWTError as exc: raise HTTPException(401, "Invalid Supabase token") from exc
    elif settings.debug and x_user_id:
        auth_id = x_user_id; email = f"{x_user_id}@local.test"
    elif settings.debug:
        auth_id = "local-dev-user"; email = "dev@abbyadv.local"
    else: raise HTTPException(401, "Authentication required")
    user = (await db.execute(select(User).where(User.auth_user_id == auth_id))).scalar_one_or_none()
    if not user:
        user = User(auth_user_id=auth_id, email=email); db.add(user); await db.commit(); await db.refresh(user)
    return user
