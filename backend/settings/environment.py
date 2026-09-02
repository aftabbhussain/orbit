from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Academic Research Assistant"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "arxiv_papers"
    
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "arxiv_documents"
