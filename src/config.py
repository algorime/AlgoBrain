"""Configuration management for AlgoBrain."""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Core Configuration
    gemini_api_key: str = Field(..., description="Gemini API key")
    gemini_model: str = Field(default="models/gemini-2.5-flash-preview-05-20")
    gemini_embedding_model: str = Field(default="models/gemini-embedding-exp-03-07")
    
    # Qdrant Configuration
    qdrant_url: str = Field(default="http://localhost:6333")
    qdrant_api_key: Optional[str] = Field(default=None)
    collection_name: str = Field(default="algobrain_knowledge")
    
    # Neo4j Configuration
    neo4j_uri: str = Field(default="bolt://localhost:7687")
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: str = Field(default="password")
    neo4j_database: str = Field(default="neo4j")
    
    # Graphiti Configuration
    graphiti_server_url: str = Field(default="http://localhost:8000")
    
    # Web Search
    tavily_api_key: Optional[str] = Field(default=None)
    
    # API Server
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8080)
    api_workers: int = Field(default=1)
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    
    # Security
    api_key_header: str = Field(default="X-API-Key")
    api_keys: str = Field(default="dev-key-123")
    
    # Performance
    max_concurrent_requests: int = Field(default=10)
    request_timeout: int = Field(default=30)
    vector_search_limit: int = Field(default=20)
    graph_traversal_limit: int = Field(default=100)
    
    # MITRE ATT&CK
    mitre_attack_url: str = Field(
        default="https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    )
    mitre_update_interval: int = Field(default=86400)  # 24 hours
    
    # Human-in-the-Loop
    hitl_confidence_threshold: float = Field(default=0.85)
    hitl_queue_size: int = Field(default=1000)
    
    # Model Configuration
    securebert_model: str = Field(default="ehsanaghaei/SecureBERT")
    embedding_dimension: int = Field(default=768)
    max_tokens: int = Field(default=4096)
    temperature: float = Field(default=0.1)
    
    @property
    def api_keys_list(self) -> List[str]:
        """Parse API keys from comma-separated string."""
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return os.getenv("ENVIRONMENT", "development") == "development"
    
    @property
    def neo4j_config(self) -> dict:
        """Get Neo4j connection configuration."""
        return {
            "uri": self.neo4j_uri,
            "auth": (self.neo4j_user, self.neo4j_password),
            "database": self.neo4j_database
        }
    
    @property
    def qdrant_config(self) -> dict:
        """Get Qdrant connection configuration."""
        config = {"url": self.qdrant_url}
        if self.qdrant_api_key:
            config["api_key"] = self.qdrant_api_key
        return config


# Global settings instance
settings = Settings()