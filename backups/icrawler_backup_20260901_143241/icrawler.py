#!/usr/bin/env python3
"""
iCRAWLER V1.8.1 — Entrypoint pulito
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fact_extractor import extract_facts_enhanced
from fact_extractor.post_processor import post_process
from modules.positioning import get_positioning_report
from knowledge.knowledge_retriever import KnowledgeRetriever


def main():
    print("\n" + "="*60)
    print("🕷️ iCRAWLER V1.8.1 HYBRID")
    print("="*60 + "\n")

    if len(sys.argv) < 2:
        print("❌ Usage: icrawler <file> | icrawler --brief 'testo'")
        sys.exit(1)

    if sys.argv[1] == "--brief":
        if len(sys.argv) < 3:
            print("❌ Specifica il brief dopo --brief")
            sys.exit(1)
        brief = sys.argv[2]
    else:
        try:
            with open(sys.argv[1], 'r') as f:
                brief = f.read()
        except FileNotFoundError:
            print(f"❌ File non trovato: {sys.argv[1]}")
            sys.exit(1)

    if not brief.strip():
        print("❌ Nessun brief ricevuto")
        return

    # 1. Estrai fatti + post-processing
    facts = extract_facts_enhanced(brief)
    facts = post_process(facts, brief)

    print("📋 FACTS:")
    for k, v in facts.items():
        print(f"  {k}: {v if v else 'DA DEFINIRE'}")

    # 2. Knowledge Base
    print("\n📚 KB RETRIEVAL:")
    try:
        retriever = KnowledgeRetriever()
        context = retriever.retrieve()
        print(f"  Style: {len(context.get('style_rules', []))} | Platform: {len(context.get('platform_rules', []))} | Content: {len(context.get('content_rules', []))}")
    except Exception as e:
        print(f"  ⚠️ KB error: {e}")

    # 3. Piano strutturato
    print("\n📋 PIANO STRUTTURATO:")
    event = facts.get('event_name', 'Evento')
    date = facts.get('date', 'DA DEFINIRE')
    location = facts.get('location', 'DA DEFINIRE')
    target = facts.get('target', 'DA DEFINIRE')
    objective = facts.get('objective', 'DA DEFINIRE')
    hashtag = facts.get('hashtag', '#Evento #Innovazione')

    structured_plan = f"""
1. STRATEGIA

📍 Evento: {event}
📅 Data: {date}
📍 Location: {location}
🎯 Target: {target}
🎯 Obiettivo: {objective}

**Obiettivo Strategico:** Costruire autorevolezza e engagement nel target.
**Tono di Voce:** Professionale, autorevole, strategico

---

2. PIANO SOCIAL PER PIATTAFORMA

**LINKEDIN** — LinkedIn (canale principale)
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

Atmosfera: istituzionale, professionale, innovativa
Soggetti: CEO, policy maker, leader di settore
Colori: palette istituzionale, blu e verde
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
"""

    print("  ✅ Generato")

    # 4. Creative Lab (semplice per ora)
    print("\n🎨 CREATIVE LAB:")
    print("  ⏳ Qwen... (simulato)")
    creative_lab = """
💡 CREATIVE LAB

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
    print("  ✅ Fallback")

    # 5. Stampa piano completo
    print("\n" + "="*60)
    print("📋 PIANO COMPLETO")
    print("="*60)
    print(structured_plan)
    print(creative_lab)

    # 6. Positioning
    print("\n" + "="*60)
    print("📊 POSIZIONAMENTO STRATEGICO")
    print("="*60)
    positioning = get_positioning_report(brief, facts)
    print(positioning)

    # 7. Salva output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output_plan_hybrid_{timestamp}.txt"
    with open(output_file, 'w') as f:
        f.write("="*60 + "\n")
        f.write("🕷️ iCRAWLER V1.8.1 HYBRID — PIANO COMPLETO\n")
        f.write(f"Generato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        f.write(structured_plan)
        f.write(creative_lab)
        f.write("\n\n" + positioning)
    print(f"\n  💾 Salvato: {output_file}")
    print("\n🏁 DONE")


if __name__ == "__main__":
    main()
