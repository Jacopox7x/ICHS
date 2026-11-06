#!/usr/bin/env python3
"""
iCRAWLER V1.8.1 HYBRID — Versione Stabile
"""

import json
import urllib.request
import time
import sys
import random
from datetime import datetime
from pathlib import Path

from knowledge.knowledge_retriever import KnowledgeRetriever
from core.creative_gate import CreativeGate

# ============================================
# 1.5 DETECT EVENT TYPE (professional / leisure)
# ============================================

def detect_event_type(facts):
    professional_keywords = [
        "conferenza", "summit", "workshop", "formazione", "business",
        "networking", "professionisti", "azienda", "corporate", "industry",
        "tecnologia", "innovazione", "startup", "investitori", "manager",
        "ceo", "cto", "policy maker", "sviluppo", "digitale", "marketing"
    ]
    leisure_keywords = [
        "festa", "compleanno", "matrimonio", "cena", "amici",
        "famiglia", "vacanza", "spiaggia", "divertimento", "party",
        "concerto", "spettacolo", "culturale", "arte", "sport",
        "runner", "maratona", "turistico", "relax", "gioia"
    ]
    texts = []
    for key in ['event_name', 'target', 'objective', 'location']:
        value = facts.get(key, '')
        if value and value != "DA DEFINIRE":
            texts.append(value.lower())
    full_text = " ".join(texts)
    professional_score = sum(1 for kw in professional_keywords if kw in full_text)
    leisure_score = sum(1 for kw in leisure_keywords if kw in full_text)
    if professional_score > leisure_score:
        return "professionale"
    elif leisure_score > professional_score:
        return "leisure"
    else:
        target = facts.get('target', '').lower()
        if any(kw in target for kw in ["amici", "famiglia", "divertimento"]):
            return "leisure"
        elif any(kw in target for kw in ["professionisti", "manager", "ceo"]):
            return "professionale"
        return "professionale"


MODEL = "qwen3.5:4b"
OLLAMA_URL = "http://localhost:11434/api/chat"

# ============================================
# 1. FACT EXTRACTOR
# ============================================

def extract_facts_from_brief(brief_text):
    facts = {
        "event_name": None, "date": None, "location": None,
        "organizer": None, "target": None, "objective": None,
        "time": None, "venue": None, "speaker": None,
        "budget": None, "link": None, "hashtag": None
    }
    text = brief_text.strip()
    for line in text.split('\n'):
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) > 1:
                key = parts[0].strip().lower()
                value = parts[1].strip()
                mapping = {
                    'evento': 'event_name', 'nome': 'event_name', 'titolo': 'event_name', 'event': 'event_name',
                    'data': 'date', 'date': 'date',
                    'luogo': 'location', 'location': 'location', 'citta': 'location',
                    'organizzatore': 'organizer', 'organizer': 'organizer',
                    'target': 'target', 'pubblico': 'target',
                    'obiettivo': 'objective', 'objective': 'objective',
                    'orario': 'time', 'time': 'time',
                    'venue': 'venue', 'sede': 'venue',
                    'speaker': 'speaker', 'relatori': 'speaker',
                    'budget': 'budget',
                    'link': 'link',
                    'hashtag': 'hashtag'
                }
                if key in mapping:
                    facts[mapping[key]] = value
    if not facts['event_name']:
        for line in text.split('\n'):
            if line.strip() and ':' not in line:
                facts['event_name'] = line.strip()
                break
    return facts

# ============================================
# 2. HASHTAG CLOUD (FALLBACK)
# ============================================

def get_hashtags_from_cloud(topic, count=10):
    base = topic.replace(" ", "").lower()
    return [
        f"#{base}", f"#{base}2026", f"#{base}Event",
        f"#{base}Community", f"#{base}Innovation",
        f"#{base}Life", f"#{base}Daily", f"#{base}World",
        f"#{base}Experience", f"#{base}Vibes"
    ][:count]

# ============================================
# 3. CREATIVE LAB (QWEN + FALLBACK)
# ============================================

def generate_creative_with_qwen(facts):
    event = facts.get('event_name', 'Evento')
    date = facts.get('date', 'data da definire')
    location = facts.get('location', 'location da definire')
    
    prompt = f"""Genera 3 idee creative per promuovere l'evento "{event}".
Data: {date}
Location: {location}

Formato:
IDEA: [titolo]
CONCEPT: [descrizione]
PERCHE FUNZIONA: [spiegazione]
RISCHIO: [criticita]"""
    
    try:
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "think": False,
            "options": {"temperature": 0.8, "num_predict": 1500}
        }
        req = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode())
            resp = d.get("message", {}).get("content", "").strip()
        return resp if len(resp) >= 10 else None
    except Exception as e:
        print(f"  [ERR] Qwen: {e}")
        return None

def build_fallback_creative():
    return """
IDEA: Il Countdown Interattivo
Concept: Post che mostrano il tempo rimanente con grafica minimalista
Perche funziona: Crea urgenza senza aggressivita
Rischio: Puo diventare ripetitivo

IDEA: Sostenibilita in Tech — Metafora Visiva
Concept: Metafora che collega codice a crescita naturale
Perche funziona: Coinvolge emotivamente
Rischio: Astratto per target tecnico

IDEA: Q&A Live Pre-Event
Concept: Post con domande aperte alla community
Perche funziona: Favorisce partecipazione
Rischio: Bassa risposta senza incentivi
"""

# ============================================
# 4. PIANO STRUTTURATO
# ============================================

def build_structured_plan(facts):
    # Rileva tipo evento
    event_type = detect_event_type(facts)
    
    # Imposta visual in base al tipo
    if event_type == "leisure":
        atmosfera = "divertente, calda, luminosa, accogliente"
        soggetti = "amici, sorrisi, momenti di convivialita"
        colori = "palette calda e accogliente, toni dorati e marine"
        tono = "Caldo, divertente, informale"
        piattaforma_reach = "Instagram e WhatsApp (canali principali)"
    else:
        atmosfera = "istituzionale, professionale, innovativa"
        soggetti = "CEO, policy maker, leader di settore"
        colori = "palette istituzionale, blu e verde"
        tono = "Professionale, autorevole, strategico"
        piattaforma_reach = "LinkedIn (canale principale)"
    
    event = facts.get('event_name') or 'DA DEFINIRE'
    date = facts.get('date') or 'DA DEFINIRE'
    location = facts.get('location') or 'DA DEFINIRE'
    organizer = facts.get('organizer') or 'DA DEFINIRE'
    target = (facts.get('target') or 'DA DEFINIRE')
    objective = (facts.get('objective') or 'DA DEFINIRE')
    time = (facts.get('time') or 'DA DEFINIRE')
    venue = facts.get('venue') or 'DA DEFINIRE'
    speaker = facts.get('speaker') or 'DA DEFINIRE'
    hashtag = (facts.get('hashtag') or '#Evento #Innovazione')
    
    return (f"""
1. STRATEGIA

📍 Evento: {event}
📅 Data: {date}
📍 Location: {location}
🏢 Organizer: {organizer}
🎯 Target: {target}
🎯 Obiettivo: {objective}
🕐 Orario: {time}
🏛️ Venue: {venue}
🎤 Speaker: {speaker}

**Obiettivo Strategico:** Costruire autorevolezza e engagement nel target.
**Tono di Voce:** {tono}

---

2. PIANO SOCIAL PER PIATTAFORMA

**LINKEDIN** — {piattaforma_reach}
- Annuncio 2 settimane prima
- Articoli settimanali, testimonianze
- Pagina evento, recap post-evento

**INSTAGRAM**
- Stories countdown giornaliero
- Reels backstage/highlights
- Carousel educativi, Highlights

**TWITTER/X**
- Live coverage evento
- Thread aggiornamenti 30-60min
- Hashtag ufficiale: {hashtag}

---

3. CONTENUTI PER PIATTAFORMA

**LinkedIn:** Annuncio, Perche partecipare, Intervista speaker, Countdown, Recap
**Instagram:** Reel teaser, Reel backstage, Reel highlights, Carousel motivi, Carousel temi
**Twitter/X:** Thread agenda, Thread live, Thread momenti salienti

---

4. CTA

1. 📍 Registrati ora — [LINK DA DEFINIRE]
2. 💬 Partecipa — usa {hashtag}
3. 🔔 Segui per aggiornamenti
4. 📧 Richiedi info — contatta organizer

---

5. HASHTAG

**Set raccomandato:**
{hashtag}

📌 Consigli: 5-7 IG, 3-5 LinkedIn, 2-3 Twitter.

---

6. VISUAL

Atmosfera: {atmosfera}
Soggetti: {soggetti}
Colori: {colori}
Formati: LinkedIn 1200x627, IG 1080x1080/1920, TW 1200x675

---

7. TIMELINE

| Settimana | Azione | Piattaforma |
|-----------|--------|-------------|
| -4 | Annuncio | LinkedIn, IG |
| -3 | Programma | LinkedIn |
| -2 | Teaser | IG, TW |
| -1 | Countdown | Tutte |
| Evento | Live | TW, IG |
| +1 | Recap | LinkedIn, IG |
| +2 | Report | LinkedIn |
""").format(event=event, date=date, location=location, organizer=organizer, target=target, objective=objective, time=time, venue=venue, speaker=speaker, hashtag=hashtag, atmosfera=atmosfera, soggetti=soggetti, colori=colori, tono=tono, piattaforma_reach=piattaforma_reach)

# ============================================
# 5. MAIN
# ============================================

def main():
    print("\n" + "="*60)
    print("🕷️ iCRAWLER V1.8.1 HYBRID")
    print("="*60 + "\n")
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            brief = f.read()
    else:
        brief = sys.stdin.read()
    
    if not brief.strip():
        print("❌ Nessun brief ricevuto")
        return
    
    facts = extract_facts_from_brief(brief)
    print("📋 FACTS:")
    for k, v in facts.items():
        print(f"  {k}: {v if v else 'DA DEFINIRE'}")
    
    print("\n📚 KB RETRIEVAL:")
    retriever = KnowledgeRetriever()
    context = retriever.retrieve()
    print(f"  Style: {len(context.get('style_rules', []))} | Platform: {len(context.get('platform_rules', []))} | Content: {len(context.get('content_rules', []))}")
    
    print("\n📋 PIANO STRUTTURATO:")
    structured_plan = build_structured_plan(facts)
    print("  ✅ Generato")
    
    print("\n🎨 CREATIVE LAB:")
    print("  ⏳ Qwen...")
    creative = generate_creative_with_qwen(facts)
    if creative:
        creative_lab = f"\n💡 CREATIVE LAB\n{creative}"
        print("  ✅ Qwen OK")
    else:
        creative_lab = f"\n💡 CREATIVE LAB\n{build_fallback_creative()}"
        print("  ⚠️ Fallback")
    
    print("\n" + "="*60)
    print("📋 PIANO COMPLETO")
    print("="*60)
    print(structured_plan)
    print(creative_lab)
    print("\n" + "="*60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output_plan_hybrid_{timestamp}.txt"
    with open(output_file, 'w') as f:
        f.write("="*60 + "\n")
        f.write("🕷️ iCRAWLER V1.8.1 HYBRID — PIANO COMPLETO\n")
        f.write(f"Generato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        f.write(structured_plan)
        f.write(creative_lab)
    print(f"  💾 Salvato: {output_file}")
    print("\n🏁 DONE")

if __name__ == "__main__":
    main()
