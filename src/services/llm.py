from src.core.config import get_settings

class LLMService:
    def __init__(self): self.settings = get_settings()
    async def complete(self, system: str, user: str, *, json_object: bool = False) -> str:
        if not self.settings.openai_api_key:
            return "LLM provider is not configured. Verify the retrieved sources and complete the legal analysis manually."
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        try:
            request = {
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            }
            if json_object:
                request["response_format"] = {"type": "json_object"}
            response = await client.chat.completions.create(**request)
            return response.choices[0].message.content or "No answer was generated."
        finally:
            await client.close()

    async def stream(self, system: str, user: str):
        """Yield answer tokens as OpenAI produces them."""
        if not self.settings.openai_api_key:
            yield "LLM provider is not configured. Verify the retrieved sources and complete the legal analysis manually."
            return
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        try:
            response = await client.chat.completions.create(model="gpt-4o-mini", temperature=0.1, stream=True, messages=[{"role":"system","content":system},{"role":"user","content":user}])
            async for chunk in response:
                token = chunk.choices[0].delta.content if chunk.choices else None
                if token:
                    yield token
        finally:
            await client.close()
