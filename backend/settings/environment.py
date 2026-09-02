from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Academic Research Assistant"
    debug: bool = False
    server_host: str = "0.0.0.0"
    server_port: int = 8000
