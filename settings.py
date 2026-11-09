"""Configurazione centralizzata di iCrawler."""

import sys
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CogneeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    llm_provider: str = Field(default="ollama")
    llm_model: str = Field(default="phi3.5-fixed")
    llm_endpoint: str = Field(default="http://localhost:11434")
    embedding_provider: str = Field(default="ollama")
    embedding_model: str = Field(default="nomic-embed-text:latest")
    embedding_endpoint: str = Field(default="http://localhost:11434/api/embed")
    embedding_dimensions: int = Field(default=768)
    documents_path: str = Field(default="./accademia_material")


def validate_config() -> CogneeSettings:
    try:
        settings = CogneeSettings()
    except Exception as e:
        print("=" * 60, file=sys.stderr)
        print("❌ CONFIGURAZIONE NON VALIDA", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print("Copia `.env.example` in `.env`:", file=sys.stderr)
        print("    cp .env.example .env", file=sys.stderr)
        print(f"Errore: {e}", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        sys.exit(1)
    if not Path(settings.documents_path).exists():
        print(f"⚠️  DOCUMENTS_PATH '{settings.documents_path}' non esiste.", file=sys.stderr)
    return settings
