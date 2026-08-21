from src.services.document_pipeline import chunk_text, index_document
from src.services.abbyy import AbbyyVantageClient
from src.services.storage import StorageService
from src.core.config import get_settings
class DocumentProcessor:
    """Coordinates ABBYY extraction followed by chunking and Qdrant indexing."""
    abbyy_client = AbbyyVantageClient
    chunk = staticmethod(chunk_text)
    index = staticmethod(index_document)
    async def extract_and_index(self, db, document):
        settings = get_settings()
        if not settings.abbyy_client_id or not settings.abbyy_client_secret or not settings.abbyy_skill_id:
            raise RuntimeError("ABBYY credentials and skill ID are required")
        client = self.abbyy_client(); storage = StorageService()
        try:
            content = await storage.download(document.storage_key); token = await client.get_token()
            if len(content) < 30 * 1024 * 1024: transaction_id = await client.launch(token, content, document.file_name, document.mime_type, settings.abbyy_skill_id)
            else: transaction_id = await client.launch_separate(token, content, document.file_name, document.mime_type, settings.abbyy_skill_id)
            return transaction_id
        finally: await client.close()
