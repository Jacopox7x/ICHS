import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
SYSTEM_PROMPT = os.getenv("ICRAWLER_SYSTEM_PROMPT", "Sei uno strategist social media.")
PROMPT_DIR = os.getenv("ICRAWLER_PROMPT_DIR", "prompts")
CACHE_DIR = os.getenv("ICRAWLER_CACHE_DIR", "cache")
LOGS_DIR = os.getenv("ICRAWLER_LOGS_DIR", "logs")

# Valori unificati (risolto bug del doppio settaggio)
MAX_TOKENS = int(os.getenv("ICRAWLER_MAX_TOKENS", "4096"))
TEMPERATURE = float(os.getenv("ICRAWLER_TEMPERATURE", "0.2"))

config = {
    "OLLAMA_MODEL": OLLAMA_MODEL,
    "OLLAMA_HOST": OLLAMA_HOST,
    "SYSTEM_PROMPT": SYSTEM_PROMPT,
    "PROMPT_DIR": PROMPT_DIR,
    "CACHE_DIR": CACHE_DIR,
    "LOGS_DIR": LOGS_DIR,
    "MAX_TOKENS": MAX_TOKENS,
    "TEMPERATURE": TEMPERATURE,
}
