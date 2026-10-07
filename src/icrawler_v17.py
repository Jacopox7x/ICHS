#!/usr/bin/env python3
"""
iCRAWLER V1.7 - Pipeline completa con Qwen
Versione stabile, onesta e scalabile
"""

import sys
import os
import time
import json
import re
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
import ollama

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent))

# Aggiungi KB (iCRAWLER_KNOWLEDGE_BASE_v1.0) al path
KB_ROOT = Path(__file__).parent.parent / "iCRAWLER_KNOWLEDGE_BASE_v1.0"
sys.path.insert(0, str(KB_ROOT))
from knowledge.knowledge_retriever import KnowledgeRetriever
from core.prompt_builder import PromptBuilder
from core.creative_gate import CreativeGate

from fact_extractor import FactExtractor, format_facts, FactStatus
from deterministic_validator import DeterministicValidator
from fallback_generator import FallbackGenerator


class iCRAWLER_V17:
    """Pipeline principale di iCRAWLER V1.7"""
    
    def __init__(self, model: str = "qwen3.5:4b", quick: bool = False):
        self.extractor = FactExtractor()
        self.fallback = FallbackGenerator()
        self.model = model
        self.quick = quick
        self.max_retries = 3
        self.timeout = 120
        self.stats = {
            "extraction_time": 0,
            "generation_time": 0,
            "validation_time": 0,
            "total_time": 0
        }
    
    def _build_prompt(self, facts: Dict[str, Any]) -> str:
        """Costruisce il prompt per Qwen usando i fatti estratti"""
        def get_value(key: str) -> str:
            fact = facts.get(key)
            return fact.value if fact and fact.value else "NON SPECIFICATO"
        
        event_name = get_value('event_name')
        date = get_value('date')
        location = get_value('location')
        target = get_value('target')
        objective = get_value('objective')
        organizer = get_value('organizer')
        time_val = get_value('time')
        
        date_readable = date
        try:
            if date and date != "NON SPECIFICATO":
                parts = date.split('-')
                if len(parts) == 3:
                    year, month, day = parts
                    month_names = ['', 'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
                                  'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']
                    month_name = month_names[int(month)]
                    date_readable = f"{int(day)} {month_name} {year}"
        except:
            pass
        
        prompt = f"""Sei un social media strategist. Genera un piano social completo per questo evento.

⚠️ IMPORTANTE: DEVI INCLUDERE OBBLIGATORIAMENTE QUESTI DATI NEL PIANO:
- 📅 DATA: {date_readable}
- 📍 LOCATION: {location}

ALTRI DATI DELL'EVENTO:
- Nome evento: {event_name}
- Target: {target}
- Obiettivo: {objective}
- Organizzatore: {organizer}
- Orario: {time_val}

REGOLE FERREE:
1. DEVI scrivere la data "{date_readable}" nel piano
2. DEVI scrivere la location "{location}" nel piano
3. Usa queste sezioni con i titoli esatti: 
   **STRATEGIA**, **PIANO SOCIAL**, **CONTENUTI INSTAGRAM**, **CONTENUTI LINKEDIN**, **CONTENUTI FACEBOOK**, **HASHTAG**, **CTA**
4. Scrivi in modo professionale e creativo
5. Se un dato è "NON SPECIFICATO", scrivi "DA DEFINIRE"
6. NON inventare date o location diverse da quelle fornite

Ora genera il piano:"""
        
        return prompt
    
    def _call_qwen(self, prompt: str) -> Optional[str]:
        """Chiama Qwen con retry"""
        print("🧠 Qwen sta generando il piano...")
        print("   ⏱️ Tempo stimato: 3-4 minuti su MacBook Air")
        print("   ☕ Momento perfetto per un caffè!")
        
        start = time.time()
        
        for attempt in range(self.max_retries):
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={
                        "temperature": 0.3,
                        "num_predict": 4096,
                        "num_ctx": 8192
                    }
                )
                elapsed = time.time() - start
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                print(f"⏱️ Generazione completata in {minutes}m {seconds}s")
                return response['message']['content']
            except Exception as e:
                print(f"⚠️ Tentativo {attempt+1}/{self.max_retries} fallito: {e}")
                if attempt < self.max_retries - 1:
                    wait = 2 ** attempt
                    print(f"   ⏳ Attendo {wait}s prima di riprovare...")
                    time.sleep(wait)
                else:
                    raise
        return None
    
    def process(self, brief: str) -> Dict[str, Any]:
        """Esegue la pipeline completa"""
        total_start = time.time()
        
        print("🕷️ iCRAWLER V1.7")
        print("=" * 60)
        print(f"📦 Modello: {self.model}")
        if self.quick:
            print("⚡ Modalità quick: solo Fact Extractor")
        
        # Step 1: Fact Extraction
        print("\n📋 Step 1: Estrazione fatti...")
        start = time.time()
        facts = self.extractor.extract(brief)
        self.stats["extraction_time"] = time.time() - start
        print(format_facts(facts))
        
        # Se modalità quick, salta Qwen
        if self.quick:
            self.stats["total_time"] = time.time() - total_start
            return {
                'status': 'QUICK',
                'facts': facts,
                'stats': self.stats
            }
        
        # Step 2: Ambiguity Check
        print("\n🔍 Step 2: Verifica ambiguità...")
        critical_fields = ['date', 'event_name', 'location']
        has_critical_ambiguity = any(
            fact.status in [FactStatus.AMBIGUOUS, FactStatus.MISSING] 
            for key, fact in facts.items() 
            if key in critical_fields
        )
        
        if has_critical_ambiguity:
            print("⚠️ Brief ambiguo o incompleto!")
            print("   Campi critici mancanti:")
            for key, fact in facts.items():
                if key in critical_fields and fact.status in [FactStatus.AMBIGUOUS, FactStatus.MISSING]:
                    print(f"   - {key}: {fact.status.value}")
            return {
                'status': 'AMBIGUOUS',
                'facts': facts,
                'stats': self.stats
            }
        
        optional_missing = [
            key for key, fact in facts.items() 
            if key not in critical_fields and fact.status in [FactStatus.AMBIGUOUS, FactStatus.MISSING]
        ]
        if optional_missing:
            print(f"⚠️ Campi opzionali mancanti: {', '.join(optional_missing)}")
            print("   → Verranno usati come 'DA DEFINIRE'")
        
        # Step 3: Qwen Generation
        print("\n🤖 Step 3: Generazione piano con Qwen...")
        start = time.time()
        try:
            # V1.8: Retrieval KB + PromptBuilder strategico
            print("\n📚 Step 3a: Retrieval Knowledge Base...")
            retriever = KnowledgeRetriever()
            context = retriever.retrieve(platform="instagram")
            builder = PromptBuilder()
            facts_dict = {k: (f.value if f and f.value else None) for k, f in facts.items()}
            prompt = builder.build(facts_dict, context)
            retriever.close()
            # Fallback alla logica V17 se la KB è vuota
            if not any(context.values()):
                prompt = self._build_prompt(facts)
            plan = self._call_qwen(prompt)
            if plan is None:
                raise RuntimeError("Qwen non ha restituito output")
            self.stats["generation_time"] = time.time() - start
            print("✅ Piano generato da Qwen")
        except Exception as e:
            print(f"⚠️ Errore Qwen: {e}")
            print("📋 Uso fallback...")
            start = time.time()
            plan = self.fallback.generate(facts)
            self.stats["generation_time"] = time.time() - start
            print("✅ Piano fallback generato")
        
        # Step 4: Validation
        print("\n✅ Step 4: Validazione...")
        start = time.time()
        validator = DeterministicValidator(facts)
        is_valid = validator.validate(plan)
        self.stats["validation_time"] = time.time() - start
        print(validator.get_report())
        
        if not is_valid:
            return {
                'status': 'INVALID',
                'facts': facts,
                'plan': plan,
                'errors': validator.errors,
                'stats': self.stats
            }
        
        # Output finale
        self.stats["total_time"] = time.time() - total_start
        print("\n📄 PIANO GENERATO")
        print("=" * 60)
        print(plan)
        print("\n" + "=" * 60)
        print("📊 STATISTICHE")
        print(f"   Estrazione fatti: {self.stats['extraction_time']:.1f}s")
        print(f"   Generazione: {self.stats['generation_time']:.1f}s")
        print(f"   Validazione: {self.stats['validation_time']:.1f}s")
        print(f"   Totale: {self.stats['total_time']:.1f}s")
        
        return {
            'status': 'SUCCESS',
            'facts': facts,
            'plan': plan,
            'validator': validator,
            'stats': self.stats
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='iCRAWLER V1.7 - Social Media Plan Generator',
        epilog='Esempi:\n  icrawler tests/test_completo.txt\n  icrawler -o piano.md\n  icrawler -m qwen3.5:1.5b'
    )
    parser.add_argument('brief_file', nargs='?', help='File contenente il brief')
    parser.add_argument('-o', '--output', help='File di output (default: auto)')
    parser.add_argument('-m', '--model', default='qwen3.5:4b', help='Modello Ollama da usare')
    parser.add_argument('--quick', action='store_true', help='Modalità rapida (solo Fact Extractor)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Output dettagliato')
    
    args = parser.parse_args()
    
    # Leggi brief
    if args.brief_file:
        try:
            with open(args.brief_file, 'r') as f:
                brief = f.read()
        except FileNotFoundError:
            print(f"❌ File non trovato: {args.brief_file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Errore lettura file: {e}")
            sys.exit(1)
    else:
        print("📝 Inserisci il brief dell'evento (Ctrl+D per finire):")
        brief = sys.stdin.read()
    
    if not brief.strip():
        print("❌ Nessun brief inserito.")
        sys.exit(1)
    
    # Esegui pipeline
    crawler = iCRAWLER_V17(model=args.model, quick=args.quick)
    result = crawler.process(brief)
    
    # Gestisci risultato
    if result['status'] == 'SUCCESS':
        if args.output:
            output_file = args.output
        else:
            output_file = f"output_plan_{int(time.time())}.txt"
        
        with open(output_file, 'w') as f:
            f.write(result['plan'])
        print(f"\n💾 Piano salvato in: {output_file}")
        sys.exit(0)
    elif result['status'] == 'QUICK':
        print("\n⚡ Modalità quick completata.")
        sys.exit(0)
    elif result['status'] == 'AMBIGUOUS':
        print("\n❌ Brief ambiguo. Correggi i campi mancanti e riprova.")
        sys.exit(1)
    elif result['status'] == 'INVALID':
        print("\n❌ Piano non valido. Rigenerazione necessaria.")
        sys.exit(1)


if __name__ == "__main__":
    main()
