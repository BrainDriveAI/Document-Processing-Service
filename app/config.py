from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ChunkingStrategy(str, Enum):
    HIERARCHICAL = "hierarchical"
    SEMANTIC = "semantic"
    TOKEN_BASED = "token_based"
    ADAPTIVE = "adaptive"


class Settings(BaseSettings):
    # App settings
    app_name: str = "BrainDrive Document AI"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "json"
    log_file: Optional[str] = "logs/app.log"
    
    # File processing
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    temp_dir: str = "data/temp"
    upload_dir: str = "data/uploads"
    supported_formats: List[str] = ["pdf", "docx", "doc", "txt"]
    
    # Document processing
    default_chunking_strategy: ChunkingStrategy = ChunkingStrategy.HIERARCHICAL
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 200
    min_chunk_size: int = 100
    max_chunk_size: int = 2000
    
    # spaCy settings
    spacy_model: str = "en_core_web_sm"
    
    # Performance
    max_concurrent_processes: int = 4
    processing_timeout: int = 300  # 5 minutes

    UPLOADS_DIR: Optional[str] = Field(default="data/uploads", env="UPLOADS_DIR", description="The directory to upload to.")
    UPLOAD_MAX_PART_SIZE: int = 50 * 1024 * 1024
    UPLOAD_MAX_FIELDS: Optional[int] = None
    UPLOAD_MAX_FILE_SIZE: Optional[int] = None
    
    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["*"]

    # FastAPI settings
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8000, env="API_PORT")
    DEBUG: bool = Field(False, env="DEBUG")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
