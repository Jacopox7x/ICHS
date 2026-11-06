#!/usr/bin/env python3

import json
import sqlite3
import urllib.request
import time

from knowledge.knowledge_retriever import KnowledgeRetriever
from core.prompt_builder import PromptBuilder

MODEL = "qwen3.5:4b"
OLLAMA_URL = "http://localhost:11434/api/generate"

facts = {
    "event_name": "Tech4Good Summit",
    "date": "22 agosto 2026",
    "location": "Milano",
    "organizer": "Impact Hub",
    "target": "professionisti dell'innovazione",
    "objective": "300 partecipanti",
    "time": None,
    "venue": None,
    "speaker": None
}

print()
print("==========================================")
print("🕷️ iCRAWLER KB → QWEN INTEGRATION TEST")
print("==========================================")
print()

print("=== 1. KNOWLEDGE RETRIEVAL ===")

retriever = KnowledgeRetriever()
context = retriever.retrieve(platform="instagram")
print("Platform rules:", len(context.get("platform_rules", [])))
print("Style rules:", len(context.get("style_rules", [])))
print("Anti-patterns:", len(context.get("anti_patterns", [])))
print("Validation rules:", len(context.get("validation_rules", [])))

print()
print("=== 2. PROMPT BUILDING ===")

builder = PromptBuilder()
prompt = builder.build(facts, context)

print("Prompt costruito:", len(prompt), "caratteri")

print()
print("=== 3. QWEN ===")
print("⏳ Qwen sta generando... (ci vorranno circa 3-4 minuti)")
print("   ☕ Vai a prendere un caffè!")
print()

start = time.time()

payload = json.dumps({
    "model": MODEL,
    "prompt": prompt,
    "stream": False
}).encode("utf-8")

request = urllib.request.Request(
    OLLAMA_URL,
    data=payload,
    headers={"Content-Type": "application/json"}
)

try:
    # Timeout aumentato a 300 secondi (5 minuti)
    with urllib.request.urlopen(request, timeout=300) as response:
        data = json.loads(response.read().decode("utf-8"))

    elapsed = time.time() - start
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    answer = data.get("response", "")

    print(f"✅ Qwen ha risposto in {minutes}m {seconds}s")
    print()
    print("---------- OUTPUT QWEN ----------")
    print(answer)
    print("---------- FINE OUTPUT ----------")

except Exception as e:
    elapsed = time.time() - start
    print(f"❌ ERRORE QWEN dopo {int(elapsed)}s: {e}")

finally:
    retriever.close()

print()
print("==========================================")
print("🏁 TEST TERMINATO")
print("==========================================")
