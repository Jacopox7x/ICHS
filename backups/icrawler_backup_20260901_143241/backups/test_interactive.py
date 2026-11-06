#!/usr/bin/env python3
"""
Test interattivo con Knowledge Base - Fact Extractor V3 (migliorato)
"""

import json
import urllib.request
import time
import sys
import re

from knowledge.knowledge_retriever import KnowledgeRetriever
from core.prompt_builder import PromptBuilder

MODEL = "qwen3.5:4b"
OLLAMA_URL = "http://localhost:11434/api/generate"

def extract_facts_from_brief(brief_text):
    """Estrazione facts con regex migliorata V3"""
    facts = {
        "event_name": None,
        "date": None,
        "location": None,
        "organizer": None,
        "target": None,
        "objective": None,
        "time": None,
        "venue": None,
        "speaker": None,
        "budget": None,
        "link": None,
        "hashtag": None
    }
    
    text = brief_text.strip()
    
    # 1. Cerca pattern strutturati (campo: valore)
    lines = text.split('\n')
    for line in lines:
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) > 1:
                key = parts[0].strip().lower()
                value = parts[1].strip()
                if key in ['evento', 'nome', 'titolo']:
                    facts["event_name"] = value
                elif key in ['data', 'date']:
                    facts["date"] = value
                elif key in ['luogo', 'location', 'città']:
                    facts["location"] = value
                elif 'organizzato' in key:
                    facts["organizer"] = value
                elif key == 'target':
                    facts["target"] = value
                elif key in ['obiettivo', 'scopo']:
                    facts["objective"] = value
                elif key in ['orario', 'time', 'ore']:
                    facts["time"] = value
                elif key in ['budget', 'prezzo']:
                    facts["budget"] = value
                elif key in ['link', 'url', 'registrazione']:
                    facts["link"] = value
                elif key in ['hashtag', 'tag']:
                    facts["hashtag"] = value
    
    # 2. Se la prima riga non è un campo, usala come nome evento
    if not facts["event_name"] and lines:
        first_line = lines[0].strip()
        if ':' not in first_line and len(first_line) < 100:
            facts["event_name"] = first_line
    
    # 3. Cerca data con regex (formati liberi)
    if not facts["date"]:
        date_patterns = [
            r'(?:il\s+)?(\d{1,2})\s*(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s*(?:(\d{4}))?',
            r'(\d{1,2})\s*[-/]\s*(\d{1,2})\s*(?:[-/]\s*(\d{4}))?',
            r'(\d{1,2})\s*(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s*(?:(\d{4}))?',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                facts["date"] = match.group(0).strip()
                break
    
    # 4. Cerca location con regex
    if not facts["location"]:
        # Cerca "a Milano", "in Milano", "presso Milano"
        location_match = re.search(r'(?:a|in|presso)\s+([A-Z][a-zàèéìòóù]+(?:\s+[A-Z][a-zàèéìòóù]+)*)', text)
        if location_match:
            facts["location"] = location_match.group(1).strip()
        
        # Cerca città conosciute
        cities = ['Milano', 'Roma', 'Torino', 'Firenze', 'Bologna', 'Napoli', 'Venezia', 'Genova', 'Cremona', 'Bergamo']
        for city in cities:
            if city in text:
                facts["location"] = city
                break
    
    # 5. Cerca organizzatore (anche da testo descrittivo)
    if not facts["organizer"]:
        org_patterns = [
            r'(?:organizzato da|organizzatore|promosso da)\s+([^.,\n]+)',
            r'Organizzata (?:da|dai|dalle)\s+([^.,\n]+)',
        ]
        for pattern in org_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                facts["organizer"] = match.group(1).strip()
                break
    
    # 6. Cerca target
    if not facts["target"]:
        target_patterns = [
            r'(?:target|pubblico|audience)\s+([^.,\n]+)',
            r'Target\s*[:;]\s*([^.,\n]+)',
        ]
        for pattern in target_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                facts["target"] = match.group(1).strip()
                break
    
    # 7. Cerca obiettivo
    if not facts["objective"]:
        obj_patterns = [
            r'(?:obiettivo|scopo|finalità)\s+([^.,\n]+)',
            r'Obiettivo\s*[:;]\s*([^.,\n]+)',
        ]
        for pattern in obj_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                facts["objective"] = match.group(1).strip()
                break
    
    # 8. Cerca orario (nuovo)
    if not facts["time"]:
        time_patterns = [
            r'(?:orario|ore|dalle)\s+(\d{1,2}[:.]?\d{0,2}\s*[-–]\s*\d{1,2}[:.]?\d{0,2})',
            r'(\d{1,2}[:.]?\d{0,2})\s*[-–]\s*(\d{1,2}[:.]?\d{0,2})',
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                facts["time"] = match.group(0).strip()
                break
    
    # 9. Cerca budget
    if not facts.get("budget"):
        budget_match = re.search(r'(?:budget|prezzo|€|euro)\s*[:;]?\s*([\d.,]+\s*(?:€|euro|mila|milioni)?)', text, re.IGNORECASE)
        if budget_match:
            facts["budget"] = budget_match.group(1).strip()
    
    # 10. Cerca link
    if not facts.get("link"):
        link_match = re.search(r'(https?://[^\s]+)', text)
        if link_match:
            facts["link"] = link_match.group(0).strip()
    
    # 11. Cerca hashtag
    if not facts.get("hashtag"):
        hashtag_match = re.search(r'(#\w+(?:\s+#\w+)*)', text)
        if hashtag_match:
            facts["hashtag"] = hashtag_match.group(0).strip()
    
    return facts

print()
print("==========================================")
print("🕷️ iCRAWLER KB - TEST INTERATTIVO (V3)")
print("==========================================")
print()
print("Inserisci il brief (Ctrl+D per inviare):")
print()

brief_text = sys.stdin.read()

if not brief_text.strip():
    print("❌ Nessun brief inserito.")
    sys.exit(1)

facts = extract_facts_from_brief(brief_text)

print()
print("=== FACTS ESTRATTI ===")
for key, value in facts.items():
    print(f"  {key}: {value or 'DA DEFINIRE'}")

print()
print("=== 1. KNOWLEDGE RETRIEVAL ===")

retriever = KnowledgeRetriever()
context = retriever.retrieve(platform="instagram")

print("Platform rules:", len(context.get("platform_rules", [])))
print("Style rules:", len(context.get("style_rules", [])))
print("Anti-patterns:", len(context.get("anti_patterns", [])))

print()
print("=== 2. PROMPT BUILDING ===")

builder = PromptBuilder()
prompt = builder.build(facts, context)

print("Prompt costruito:", len(prompt), "caratteri")

print()
print("=== 3. QWEN ===")
print("⏳ Qwen sta generando... (3-4 minuti)")
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
    with urllib.request.urlopen(request, timeout=300) as response:
        data = json.loads(response.read().decode("utf-8"))

    elapsed = time.time() - start
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    answer = data.get("response", "")

    print(f"✅ Qwen ha risposto in {minutes}m {seconds}s")
    print()
    print("---------- PIANO GENERATO ----------")
    print(answer if answer.strip() else "⚠️ QWEN HA PRODOTTO UN OUTPUT VUOTO")
    print("---------- FINE PIANO ----------")

except Exception as e:
    elapsed = time.time() - start
    print(f"❌ ERRORE Qwen dopo {int(elapsed)}s: {e}")

finally:
    retriever.close()

print()
print("==========================================")
print("🏁 TEST TERMINATO")
print("==========================================")
