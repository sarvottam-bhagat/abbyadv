import logging
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        response = await call_next(request); response.headers["X-Request-Id"] = request_id; return response
def configure_logging(): logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
