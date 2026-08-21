class ChatHistoryManager:
    def summarize(self, messages: list[dict]) -> str:
        return "\n".join(f"{message.get('role')}: {message.get('content')}" for message in messages[-10:])

