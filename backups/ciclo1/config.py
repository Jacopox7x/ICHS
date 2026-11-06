import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
SYSTEM_PROMPT = os.getenv("ICRAWLER_SYSTEM_PROMPT", "Sei uno strategist social media.")
PROMPT_DIR = os.getenv("ICRAWLER_PROMPT_DIR", "prompts")
CACHE_DIR = os.getenv("ICRAWLER_CACHE_DIR", "cache")
LOGS_DIR = os.getenv("ICRAWLER_LOGS_DIR", "logs")
MAX_TOKENS = int(os.getenv("ICRAWLER_MAX_TOKENS", "2048"))
TEMPERATURE = float(os.getenv("ICRAWLER_TEMPERATURE", "0.7"))

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

# Parametri Ollama per output più deterministico
TEMPERATURE = 0.2
MAX_TOKENS = 4096
