#!/usr/bin/env python3
"""
iCRAWLER V1.8.2 — FALLBACK-ONLY (veloce e stabile)
"""

import sys
import os
from datetime import datetime
from fact_extractor.regex_extractor import extract_with_regex
from fact_extractor.post_processor import post_process
from modules.positioning import get_positioning_report
from modules.systemic_rules import apply_systemic_rules
from knowledge.knowledge_retriever import KnowledgeRetriever
from modules.search_agent import get_live_insights

def main():
    print("\n" + "="*60)
    print("🕷️ iCRAWLER V1.8.2 FALLBACK-ONLY")
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

    # 1. Estrai fatti con FALLBACK (veloce)
    raw_facts = extract_with_regex(brief)
    facts = post_process(raw_facts, brief)

    print("📋 FACTS:")
    for k, v in facts.items():
        print(f"  {k}: {v if v else 'DA DEFINIRE'}")

    # 2. Web Insights live (agente di ricerca)
    print("🔍 Esecuzione web insights...")
    insights = get_live_insights(facts)
    if not insights:
        print("⚠️ Web insights non disponibili, continuo con fallback")
        insights = {}

    # 3. Knowledge Base
    print("\n📚 KB RETRIEVAL:")
    try:
        retriever = KnowledgeRetriever()
        context = retriever.retrieve()

        # WeKnora RAG: contesto cooperativa (fallback graceful)
        print("🌐 WeKnora context...")
        weknora_context = retriever.retrieve_from_weknora(
            f"tono voce, lessico, piattaforme per evento {facts.get('event_name', '')}",
            top_k=5,
            max_chars=5000
        )
        if weknora_context:
            context["weknora_context"] = weknora_context
            print(f"   ✅ {len(weknora_context)} caratteri di contesto")
        else:
            print("   ⚠️  WeKnora non disponibile, continuo senza")
        print(f"  Style: {len(context.get('style_rules', []))} | Platform: {len(context.get('platform_rules', []))} | Content: {len(context.get('content_rules', []))}")
    except Exception as e:
        print(f"  ⚠️ KB error: {e}")

    # 4. Piano strutturato
    print("\n📋 PIANO STRUTTURATO:")
    event = facts.get('event_name', 'Evento')
    date = facts.get('date', 'DA DEFINIRE')
    location = facts.get('location', 'DA DEFINIRE')
    target = facts.get('target', 'DA DEFINIRE')
    objective = facts.get('objective', 'DA DEFINIRE')
    hashtag = facts.get('hashtag', '#Evento #Innovazione')

    # Applica regole sistemiche
    rules = apply_systemic_rules(facts, weknora_context=context.get("weknora_context", "") if 'context' in dir() else "")
    hashtags_suggeriti = " ".join(rules["hashtags"][:8])
    cta_list = rules["cta"]
    visual = rules["visual"]
    times = rules["posting_times"]
    cta_text = "\n".join([f"{i+1}. {c}" for i, c in enumerate(cta_list)])

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
- Pubblica: {times["LinkedIn"]}
- Annuncio 2 settimane prima
- Articoli settimanali, testimonianze
- Pagina evento, recap post-evento
- Thread di approfondimento settimanali
- Contenuti di thought leadership
- Networking post-evento

**INSTAGRAM**
- Pubblica: {times["Instagram"]}
- Stories countdown giornaliero
- Reels backstage/highlights
- Carousel educativi, Highlights
- Storie interattive con sondaggi
- Filtri e sticker personalizzati
- Video brevi con anticipazioni

**TWITTER/X**
- Pubblica: {times["Twitter"]}
- Live coverage evento
- Thread aggiornamenti 30-60min
- Retweet e interazioni con i partecipanti
- Citazioni e highlights dei relatori
- Sondaggi in tempo reale
- Hashtag ufficiale: {hashtag}

---

3. CONTENUTI PER PIATTAFORMA

**LinkedIn:** Annuncio, Perche partecipare, Intervista speaker, Countdown, Recap
**Instagram:** Reel teaser, Reel backstage, Reel highlights, Carousel motivi, Carousel temi
**Twitter/X:** Thread agenda, Thread live, Thread momenti salienti

---

4. CTA

1. {cta_list[0]}
2. {cta_list[1]}
3. {cta_list[2]}
4. {cta_list[3]}

---

5. HASHTAG

**Set raccomandato:**
{hashtags_suggeriti}

📌 Consigli: 5-7 IG, 3-5 LinkedIn, 2-3 Twitter.

---

6. VISUAL

Atmosfera: {visual["atmosfera"]}
Soggetti: {visual["soggetti"]}
Colori: {visual["colori"]}
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

    # 5. Creative Lab (fallback)
    print("\n🎨 CREATIVE LAB:")
    from fact_extractor.creative_lab_fallback import build_creative_lab
    creative_lab = build_creative_lab(facts)
    creative_lab = creative_lab.replace("IDEA", "\n\n💡 IDEA")
    print("  ✅ Creative Lab generato")

    # 6. WEB INSIGHTS (live + fallback)
    print("\n" + "="*60)
    print("🌐 WEB INSIGHTS LIVE")
    print("="*60)

    # Usa i dati live da SearchAgent se disponibili
    if insights.get('news') or insights.get('trending_hashtags'):
        print("\n📰 Notizie e contenuti correlati:")
        for i, news in enumerate(insights.get('news', [])[:5], 1):
            print(f"  {i}. {news['title'][:80]}")
            if news.get('url'):
                print(f"     🔗 {news['url']}")

        hashtags_live = insights.get('trending_hashtags', [])
        if hashtags_live:
            print(f"\n🏷️ Hashtag trending live:")
            print(f"  {' '.join(hashtags_live[:10])}")

        keywords = insights.get('keywords', [])
        if keywords:
            print(f"\n🔑 Keyword emergenti:")
            print(f"  {', '.join(keywords[:10])}")

        competitors = insights.get('competitors', [])
        if competitors:
            print(f"\n🏟️ Eventi competitor rilevati:")
            for comp in competitors[:3]:
                print(f"  - {comp}")
    else:
        # Fallback: usa il vecchio web_search (DuckDuckGo)
        print("  ℹ️ Nessun dato live, uso fallback DuckDuckGo")
        try:
            from modules.web_search import search_web, get_trending_hashtags
            topic = facts.get("event_name", "")
            if topic and topic != "DA DEFINIRE":
                print(f"🔍 Ricerca live per: {topic}")
                risultati = search_web(topic, max_results=5)
                if risultati:
                    print("\n📰 Notizie e contenuti correlati:")
                    for i, r in enumerate(risultati[:3], 1):
                        print(f"  {i}. {r['title'][:80]}...")
                        if r['url']:
                            print(f"     {r['url']}")
                    hashtag_fallback = get_trending_hashtags(topic)
                    if hashtag_fallback:
                        print(f"\n🏷️ Hashtag generati: {' '.join(hashtag_fallback)}")
                else:
                    print("  ⚠️ Nessun risultato live trovato")
            else:
                print("  ⚠️ Nessun tema da cercare")
        except Exception as e:
            print(f"  ⚠️ Web insights non disponibile: {e}")

    print("\n" + "="*60)

    # 7. Stampa piano completo
    print("\n" + "="*60)
    print("📋 PIANO COMPLETO")
    print("="*60)
    print(structured_plan)
    print(creative_lab)

    # 8. Positioning
    print("\n" + "="*60)
    print("📊 POSIZIONAMENTO STRATEGICO")
    print("="*60)
    positioning = get_positioning_report(brief, facts)
    print(positioning)

    # 9. Salva output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output_plan_hybrid_{timestamp}.txt"
    with open(output_file, 'w') as f:
        f.write("="*60 + "\n")
        f.write("🕷️ iCRAWLER V1.8.2 — PIANO COMPLETO (FALLBACK)\n")
        f.write(f"Generato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        f.write(structured_plan)
        f.write(creative_lab)
        f.write("\n\n" + positioning)
    print(f"\n  💾 Salvato: {output_file}")
    print("\n🏁 DONE")


if __name__ == "__main__":
    main()
