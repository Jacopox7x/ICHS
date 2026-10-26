#!/usr/bin/env python3
"""apply_ciclo1.py - Patch del Ciclo 1 per iCrawler.

NON rimuove hashtag_cloud.py (prompt_builder.py lo importa).
Neutralizza solo _fetch_from_cloud per fermare le chiamate a api.example.com.
Rimozione completa del modulo prevista nel Ciclo 2.
"""
import shutil
from pathlib import Path

ROOT = Path.cwd()
BACKUP = ROOT / "backups" / "ciclo1"
BACKUP.mkdir(parents=True, exist_ok=True)

# === Backup ===
for name in ("config.py", "icrawler_simple.py", "hashtag_cloud.py"):
    src = ROOT / name
    if src.exists():
        shutil.copy2(src, BACKUP / name)
print("[1/4] Backup completato in backups/ciclo1/")

# === Patch 1: config.py (rewrite completo) ===
new_config = '''"""config.py - Configurazione centralizzata di iCrawler.

Regola: i valori definiti qui sono l'unica fonte di verita.
Nessun altro modulo deve ridefinire TEMPERATURE, MAX_TOKENS o modello.
Le variabili d'ambiente sovrascrivono i default.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# --- Ollama ---
OLLAMA_MODEL = os.getenv("ICRAWLER_OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
TEMPERATURE = float(os.getenv("ICRAWLER_TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("ICRAWLER_MAX_TOKENS", "4096"))

# --- Prompt ---
SYSTEM_PROMPT = os.getenv("ICRAWLER_SYSTEM_PROMPT", "Sei uno strategist social media.")
PROMPT_DIR = os.getenv("ICRAWLER_PROMPT_DIR", "prompts")

# --- Filesystem ---
CACHE_DIR = os.getenv("ICRAWLER_CACHE_DIR", "cache")
LOGS_DIR = os.getenv("ICRAWLER_LOGS_DIR", "logs")

# --- Config dict (unica fonte di verita per i consumer) ---
config = {
    "OLLAMA_MODEL": OLLAMA_MODEL,
    "OLLAMA_HOST": OLLAMA_HOST,
    "TEMPERATURE": TEMPERATURE,
    "MAX_TOKENS": MAX_TOKENS,
    "SYSTEM_PROMPT": SYSTEM_PROMPT,
    "PROMPT_DIR": PROMPT_DIR,
    "CACHE_DIR": CACHE_DIR,
    "LOGS_DIR": LOGS_DIR,
}
'''
(ROOT / "config.py").write_text(new_config)
print("[2/4] config.py riscritto")

# === Patch 2: icrawler_simple.py (tre sostituzioni) ===
p = ROOT / "icrawler_simple.py"
s = p.read_text()

old_shebang = '#!/usr/bin/env options={"temperature": 0.3, "num_predict" 8192}\n# python3'
new_shebang = '#!/usr/bin/env python3'
if new_shebang in s:
    print("    (shebang gia applicato)")
elif old_shebang in s:
    s = s.replace(old_shebang, new_shebang)
else:
    raise SystemExit("ERRORE: shebang non trovato in icrawler_simple.py")

old_model = 'self.model = config.get("OLLAMA_MODEL", "qwen3.5:4b")'
new_model = 'self.model = config["OLLAMA_MODEL"]'
if new_model in s:
    print("    (model gia applicato)")
elif old_model in s:
    s = s.replace(old_model, new_model)
else:
    raise SystemExit("ERRORE: riga self.model non trovata")

old_opts = '            options={"temperature": 0.3, "num_predict": 8192}'
new_opts = '''            options={
                "temperature": config["TEMPERATURE"],
                "num_predict": config["MAX_TOKENS"],
            }'''
if new_opts in s:
    print("    (options gia applicato)")
elif old_opts in s:
    s = s.replace(old_opts, new_opts)
else:
    raise SystemExit("ERRORE: riga options non trovata")

p.write_text(s)
print("[3/4] icrawler_simple.py patchato (shebang + model + options)")

# === Patch 3: hashtag_cloud.py - neutralizza _fetch_from_cloud ===
p = ROOT / "hashtag_cloud.py"
s = p.read_text()

old_fetch = '''    def _fetch_from_cloud(self, category: str, topic: str) -> Optional[List[str]]:
        """Tenta di ottenere hashtag dall'API cloud."""
        try:
            response = requests.get(
                self.api_url,
                params={"category": category, "topic": topic},
                timeout=2
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("hashtags", [])
        except:
            pass
        return None'''

new_fetch = '''    def _fetch_from_cloud(self, category: str, topic: str) -> Optional[List[str]]:
        """Cloud disattivato - nessuna API cloud disponibile in locale.

        La funzione resta per non rompere l'interfaccia usata da prompt_builder.py.
        Rimozione completa del modulo prevista nel Ciclo 2.
        """
        return None'''

if new_fetch in s:
    print("    (_fetch_from_cloud gia neutralizzato)")
elif old_fetch in s:
    s = s.replace(old_fetch, new_fetch)
    p.write_text(s)
else:
    raise SystemExit("ERRORE: corpo di _fetch_from_cloud non trovato")
print("[4/4] hashtag_cloud.py neutralizzato (cloud off, file non rimosso)")

# === Verifiche ===
print()
print("=== Verifica config ===")
from config import config as cfg
print(f"TEMP: {cfg['TEMPERATURE']}  MAX: {cfg['MAX_TOKENS']}  MODEL: {cfg['OLLAMA_MODEL']}")
assert cfg["TEMPERATURE"] == 0.2, "TEMPERATURE non e 0.2"
assert cfg["MAX_TOKENS"] == 4096, "MAX_TOKENS non e 4096"
assert cfg["OLLAMA_MODEL"] == "llama3.2:3b", "MODEL non e llama3.2:3b"

print()
print("=== Verifica ICrawler ===")
from icrawler_simple import ICrawler
c = ICrawler()
print(f"MODEL: {c.model}")
assert c.model == "llama3.2:3b", "il modello non e quello di config"

print()
print("=== Verifica prompt_builder (deve ancora importare HashtagCloud) ===")
from prompt_builder import PromptBuilder
pb = PromptBuilder()
print("OK PromptBuilder funzionante")

print()
print("=== Verifica hashtag_cloud neutralizzato ===")
from hashtag_cloud import HashtagCloud
hc = HashtagCloud()
r = hc._fetch_from_cloud("food", "test")
print(f"_fetch_from_cloud ritorna: {r}")
assert r is None, "_fetch_from_cloud non e neutralizzato"

print()
print("CICLO 1 COMPLETATO")
print("  - config.py: bug P1 fixato (0.2 / 4096 / llama3.2:3b)")
print("  - icrawler_simple.py: temperature e num_predict presi dal config")
print("  - hashtag_cloud.py: _fetch_from_cloud neutralizzato (nessuna rete)")
print("  - hashtag_cloud.py NON rimosso: prompt_builder.py lo importa ancora")
print("  - Rimozione completa del modulo prevista nel Ciclo 2")
