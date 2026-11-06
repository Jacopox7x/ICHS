#!/usr/bin/env python3
"""
iCRAWLER V1.8.1 FINAL
Con Validator + Divisione per Piattaforma
"""

import json
import urllib.request
import time
import sys

from knowledge.knowledge_retriever import KnowledgeRetriever
from core.prompt_builder import PromptBuilder
from core.creative_gate import CreativeGate

MODEL = "qwen3.5:4b"
OLLAMA_URL = "http://localhost:11434/api/generate"

def extract_facts_from_brief(brief_text):
    """Estrazione facts"""
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
    lines = text.split('\n')
    for line in lines:
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) > 1:
                key = parts[0].strip().lower()
                value = parts[1].strip()
                if key in ['evento', 'nome', 'titolo', 'event']:
                    facts["event_name"] = value
                elif key in ['data', 'date']:
                    facts["date"] = value
                elif key in ['luogo', 'location', 'citta']:
                    facts["location"] = value
                elif key in ['organizzatore', 'organizer']:
                    facts["organizer"] = value
                elif key in ['target', 'pubblico']:
                    facts["target"] = value
                elif key in ['obiettivo', 'objective']:
                    facts["objective"] = value
                elif key in ['orario', 'time']:
                    facts["time"] = value
                elif key in ['venue', 'sede']:
                    facts["venue"] = value
                elif key in ['speaker', 'relatori']:
                    facts["speaker"] = value
                elif key in ['budget']:
                    facts["budget"] = value
                elif key in ['link']:
                    facts["link"] = value
                elif key in ['hashtag']:
                    facts["hashtag"] = value
    
    return facts

def generate_with_qwen(prompt):
    """Genera risposta da Qwen"""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 4000
        }
    }
    
    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '').strip()
    except Exception as e:
        print(f"❌ Errore Qwen: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("🕷️ iCRAWLER V1.8.1")
    print("="*60 + "\n")
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            brief = f.read()
    else:
        brief = sys.stdin.read()
    
    if not brief.strip():
        print("❌ Nessun brief ricevuto")
        return
    
    # 1. Estrai facts
    facts = extract_facts_from_brief(brief)
    print("📋 FACTS ESTRATTI:")
    for k, v in facts.items():
        print(f"  {k}: {v if v else 'DA DEFINIRE'}")
    
    # 2. Knowledge Retrieval
    print("\n📚 KNOWLEDGE RETRIEVAL:")
    retriever = KnowledgeRetriever()
    
    platform = None
    if facts.get('target'):
        if 'tech' in facts['target'].lower() or 'b2b' in facts['target'].lower():
            platform = 'linkedin'
        elif 'instagram' in facts['target'].lower() or 'consumer' in facts['target'].lower():
            platform = 'instagram'
    
    context = retriever.retrieve(platform=platform)
    
    print(f"  Platform rules: {len(context.get('platform_rules', []))}")
    print(f"  Style rules: {len(context.get('style_rules', []))}")
    print(f"  Content rules: {len(context.get('content_rules', []))}")
    print(f"  Anti-patterns: {len(context.get('anti_patterns', []))}")
    
    # 3. Build prompt
    print("\n🔨 PROMPT BUILDING:")
    builder = PromptBuilder()
    prompt = builder.build(facts, context)
    print(f"  Prompt costruito: {len(prompt)} caratteri")
    
    # 4. Generazione
    print("\n🤖 QWEN GENERATION:")
    print("  ⏳ Generazione in corso... (3-4 minuti)")
    
    start = time.time()
    response = generate_with_qwen(prompt)
    elapsed = time.time() - start
    
    if response:
        print(f"  ✅ Risposta in {int(elapsed//60)}m {int(elapsed%60)}s")
        print(f"  📊 {len(response)} caratteri")
        
        # 5. Creative Gate
        print("\n🎨 CREATIVE GATE:")
        gate = CreativeGate(facts)
        clean_output, warnings = gate.enforce(response)
        
        print(f"  Output pulito: {len(clean_output)} caratteri")
        if warnings:
            print(f"  ⚠️ Warnings: {len(warnings)}")
            for w in warnings:
                print(f"    - {w}")
        
        # 6. Output finale
        print("\n" + "="*60)
        print("📋 PIANO GENERATO")
        print("="*60)
        print(clean_output)
        print("="*60)
        
        # 7. Statistiche
        print(f"\n📊 STATISTICHE")
        print(f"  Generazione: {elapsed:.1f}s")
        print(f"  Caratteri: {len(clean_output)}")
        
    else:
        print("  ❌ Qwen non ha prodotto output")
        
    print("\n🏁 TEST COMPLETATO")

if __name__ == "__main__":
    main()
