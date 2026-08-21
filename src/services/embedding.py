import hashlib
import math
from src.core.config import get_settings

class EmbeddingService:
    def __init__(self): self.settings = get_settings()
    async def embed(self, text: str) -> list[float]:
        if self.settings.openai_api_key:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            response = await client.embeddings.create(model=self.settings.openai_embedding_model, input=text)
            return response.data[0].embedding
        # Deterministic local fallback keeps the pipeline testable without API credentials.
        vector = [0.0] * self.settings.embedding_dimension
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        for index, byte in enumerate(digest): vector[index % len(vector)] += (byte / 255.0) - 0.5
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

