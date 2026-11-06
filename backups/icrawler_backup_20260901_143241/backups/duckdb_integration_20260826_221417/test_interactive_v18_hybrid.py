#!/usr/bin/env python3
"""
iCRAWLER V1.8.1 HYBRID — Con Agent Reach + Hashtag Popolari
Output sempre garantito con analisi di reach e hashtag trending
"""

import json
import urllib.request
import socket
import time
import sys
from datetime import datetime
import random

from knowledge.knowledge_retriever import KnowledgeRetriever
from core.creative_gate import CreativeGate

MODEL = "qwen3.5:4b"
OLLAMA_URL = "http://localhost:11434/api/generate"

# ============================================
# 1. HASHTAG POPOLARI PER SETTORE
# ============================================

HASHTAG_DATABASE = {
    "tech": [
        "#TechInnovation", "#DigitalTransformation", "#FutureTech",
        "#AI", "#MachineLearning", "#DeepTech", "#TechTrends",
        "#InnovationHub", "#TechCommunity", "#NextGenTech",
        "#TechForGood", "#SustainableTech", "#GreenTech",
        "#TechLeaders", "#StartupLife", "#ScaleUp", "#VentureCapital"
    ],
    "sustainability": [
        "#Sustainability", "#EcoInnovation", "#GreenFuture",
        "#ClimateAction", "#SustainableDevelopment", "#NetZero",
        "#CircularEconomy", "#CleanTech", "#GreenTech",
        "#EcoFriendly", "#SustainableLiving", "#ZeroWaste",
        "#RenewableEnergy", "#ESG", "#GreenBusiness"
    ],
    "b2b": [
        "#B2BMarketing", "#B2BLeadGeneration", "#BusinessGrowth",
        "#SalesStrategy", "#B2BCommunity", "#EnterpriseTech",
        "#BusinessDevelopment", "#Partnership", "#Networking",
        "#CorporateInnovation", "#Industry40", "#DigitalBusiness"
    ],
    "innovation": [
        "#Innovation", "#DisruptiveTech", "#FutureForward",
        "#InnovationStrategy", "#DesignThinking", "#CreativeStrategy",
        "#DisruptiveInnovation", "#InnovationCulture", "#ChangeMakers",
        "#BreakthroughIdeas", "#NextBigThing", "#InnovationEcosystem"
    ],
    "milano": [
        "#Milano", "#MilanoEvents", "#MilanoInnovation",
        "#MilanoTech", "#MilanoDigital", "#MilanoStartup",
        "#MilanoBusiness", "#MilanoHub", "#Milano2026"
    ],
    "linkedin": [
        "#LinkedInStrategy", "#LinkedInMarketing", "#ThoughtLeadership",
        "#B2BLinkedIn", "#LinkedInTips", "#ProfessionalGrowth",
        "#CareerDevelopment", "#PersonalBranding", "#LinkedInNetwork"
    ],
    "instagram": [
        "#InstagramStrategy", "#InstagramMarketing", "#InstaGrowth",
        "#Reels", "#InstaCommunity", "#VisualStorytelling",
        "#InstagramTips", "#ContentCreator", "#InstaEngagement"
    ]
}

def get_hashtags_for_event(facts, count=10):
    """Genera hashtag dinamici basati sul contenuto del brief"""
    
    # Estrai tutti i testi dai facts
    texts = []
    for key, value in facts.items():
        if value and value != "DA DEFINIRE":
            texts.append(value.lower())
    
    full_text = " ".join(texts)
    
    # Parole chiave e relativi hashtag
    keyword_map = {
        # Eventi
        "compleanno": ["#HappyBirthday", "#BuonCompleanno", "#Compleanno", "#TantiAuguri", "#FestaDiCompleanno"],
        "festa": ["#Festa", "#Party", "#Celebration", "#GranFesta", "#FestaConAmici"],
        "matrimonio": ["#Wedding", "#Matrimonio", "#Sposi", "#WeddingDay", "#LoveStory"],
        "concerto": ["#Concerto", "#LiveMusic", "#Concert", "#MusicEvent", "#LiveShow"],
        "conferenza": ["#Conferenza", "#Conference", "#TechConference", "#BusinessEvent", "#Networking"],
        "sport": ["#Sport", "#Atletica", "#Competition", "#SportEvent", "#TeamSpirit"],
        "cena": ["#Cena", "#Dinner", "#Food", "#Gourmet", "#CenaTraAmici"],
        "viaggio": ["#Viaggio", "#Travel", "#Adventure", "#Explore", "#Wanderlust"],
        
        # Location
        "rejkjavik": ["#Reykjavik", "#Iceland", "#VisitIceland", "#NordicVibes", "#IcelandAdventure"],
        "islanda": ["#Iceland", "#VisitIceland", "#NorthernLights", "#IcelandNature", "#LandOfFireAndIce"],
        "milano": ["#Milano", "#MilanoEvents", "#MilanoCity", "#Lombardia", "#Italy"],
        "roma": ["#Roma", "#Rome", "#EternalCity", "#ItalyTravel", "#RomanHoliday"],
        "torino": ["#Torino", "#Turin", "#Piemonte", "#ItalyEvents"],
        "napoli": ["#Napoli", "#Naples", "#Campania", "#ItalyTravel"],
        "londra": ["#London", "#UK", "#LondonLife", "#British"],
        "parigi": ["#Paris", "#France", "#CityOfLight", "#Parisian"],
        "berlino": ["#Berlin", "#Germany", "#BerlinLife", "#German"],
        "newyork": ["#NewYork", "#NYC", "#BigApple", "#USATravel"],
        "tokyo": ["#Tokyo", "#Japan", "#TokyoLife", "#JapanTravel"],
        
        # Target
        "amici": ["#Friends", "#Amici", "#AmiciPerSempre", "#Friendship", "#BFF"],
        "famiglia": ["#Family", "#Famiglia", "#FamilyFirst", "#FamilyTime", "#Relatives"],
        "colleghi": ["#Colleagues", "#Work", "#Team", "#Business", "#WorkFriends"],
        "professionisti": ["#Professionals", "#Networking", "#Business", "#Career"],
        "studenti": ["#Studenti", "#Students", "#Education", "#CampusLife", "#University"],
        "bambini": ["#Kids", "#Bambini", "#Children", "#FamilyFun", "#KidsActivities"],
        
        # Temi
        "musica": ["#Musica", "#Music", "#LiveMusic", "#Concert", "#Melody"],
        "arte": ["#Arte", "#Art", "#Exhibition", "#ArtGallery", "#Creative"],
        "cultura": ["#Cultura", "#Culture", "#Heritage", "#ArtAndCulture", "#CulturalEvent"],
        "natura": ["#Natura", "#Nature", "#Green", "#NatureLovers", "#EcoFriendly"],
        "avventura": ["#Avventura", "#Adventure", "#Exploration", "#Thrill", "#Outdoor"],
        "benessere": ["#Benessere", "#Wellness", "#Health", "#SelfCare", "#Relax"],
        "sostenibilità": ["#Sostenibilita", "#Sustainability", "#Green", "#Eco", "#ZeroWaste"],
        "innovazione": ["#Innovazione", "#Innovation", "#Future", "#Tech", "#Digital"],
        "tradizione": ["#Tradizione", "#Tradition", "#Heritage", "#Customs", "#CulturalRoots"],
    }
    
    hashtags = []
    
    # Cerca parole chiave nel testo
    for keyword, tags in keyword_map.items():
        if keyword in full_text:
            hashtags.extend(tags)
    
    # Aggiungi hashtag specifici del brief
    if facts.get('hashtag') and facts['hashtag'] != "DA DEFINIRE":
        hashtags.append(facts['hashtag'])
    
    # Rimuovi duplicati
    hashtags = list(dict.fromkeys(hashtags))
    
    # Se non ci sono hashtag, usa dei generici
    if not hashtags:
        hashtags = ["#Evento", "#Festa", "#Celebration", "#Amici", "#MomentiIndimenticabili"]
    
    # Mescola e seleziona
    random.shuffle(hashtags)
    return hashtags[:count]

    return hashtags[:count]

# ============================================
# 2. AGENT REACH — Stima del reach per piattaforma
# ============================================

class ReachAgent:
    PLATFORM_WEIGHTS = {
        'linkedin': {
            'base_reach': 5000,
            'multiplier_b2b': 3.0,
            'multiplier_tech': 2.5,
            'multiplier_enterprise': 4.0
        },
        'instagram': {
            'base_reach': 10000,
            'multiplier_visual': 2.0,
            'multiplier_stories': 1.8,
            'multiplier_reels': 2.5
        },
        'twitter': {
            'base_reach': 3000,
            'multiplier_live': 2.0,
            'multiplier_trending': 3.0,
            'multiplier_thread': 1.5
        }
    }

    def __init__(self, facts):
        self.facts = facts
        self.target = (facts.get('target') or '').lower()
        self.objective = (facts.get('objective') or '').lower()
        self.event_name = facts.get('event_name') or ''

    def estimate_linkedin(self):
        base = self.PLATFORM_WEIGHTS['linkedin']['base_reach']
        multiplier = 1.0
        if 'b2b' in self.target or 'manager' in self.target:
            multiplier *= self.PLATFORM_WEIGHTS['linkedin']['multiplier_b2b']
        if 'tech' in self.target or 'it' in self.target:
            multiplier *= self.PLATFORM_WEIGHTS['linkedin']['multiplier_tech']
        if 'enterprise' in self.target or 'corporate' in self.target:
            multiplier *= self.PLATFORM_WEIGHTS['linkedin']['multiplier_enterprise']
        return int(base * multiplier)

    def estimate_instagram(self):
        base = self.PLATFORM_WEIGHTS['instagram']['base_reach']
        multiplier = 1.0
        if 'visual' in self.objective or 'story' in self.objective:
            multiplier *= self.PLATFORM_WEIGHTS['instagram']['multiplier_visual']
        if 'reels' in self.objective or 'video' in self.objective:
            multiplier *= self.PLATFORM_WEIGHTS['instagram']['multiplier_reels']
        if '25-40' in self.target:
            multiplier *= 1.5
        return int(base * multiplier)

    def estimate_twitter(self):
        base = self.PLATFORM_WEIGHTS['twitter']['base_reach']
        multiplier = 1.0
        if 'live' in self.objective or 'coverage' in self.objective:
            multiplier *= self.PLATFORM_WEIGHTS['twitter']['multiplier_live']
        if 'trending' in self.objective or 'viral' in self.objective:
            multiplier *= self.PLATFORM_WEIGHTS['twitter']['multiplier_trending']
        if 'thread' in self.objective or 'discussion' in self.objective:
            multiplier *= self.PLATFORM_WEIGHTS['twitter']['multiplier_thread']
        return int(base * multiplier)

    def get_all_estimates(self):
        return {
            'linkedin': self.estimate_linkedin(),
            'instagram': self.estimate_instagram(),
            'twitter': self.estimate_twitter()
        }

    def get_total_reach(self):
        return sum(self.get_all_estimates().values())

    def get_reach_report(self):
        e = self.get_all_estimates()
        total = self.get_total_reach()
        return f"""
📊 AGENT REACH — Stima Reach Potenziale

| Piattaforma | Reach Stimato | Fattori |
|-------------|---------------|---------|
| LinkedIn    | {e['linkedin']:,} | B2B + Tech |
| Instagram   | {e['instagram']:,} | Visual + Stories |
| Twitter/X   | {e['twitter']:,} | Live + Coverage |
| **TOTALE**  | **{total:,}** | **Reach combinato** |

📌 Stime basate su benchmark di settore (non dati live).
"""

def generate_creative_with_qwen(facts):
    """Genera idee creative con Qwen tramite /api/chat (think:False)"""
    import socket
    import urllib.error
    
    event = facts.get('event_name', 'Evento')
    date = facts.get('date', 'data da definire')
    location = facts.get('location', 'location da definire')
    target = facts.get('target', 'target da definire')
    objective = facts.get('objective', 'obiettivo da definire')

    prompt = f"""Sei un esperto di marketing creativo. Genera 3 idee creative per promuovere l'evento {event}.

Data: {date}
Location: {location}
Target: {target}
Obiettivo: {objective}

Per ogni idea scrivi esattamente:
IDEA: [titolo]
CONCEPT: [descrizione 2-3 frasi]
PERCHE FUNZIONA: [spiegazione breve]
RISCHIO: [criticita]

Scrivi solo le 3 idee, senza introduzioni ne conclusioni."""

    print(f"  [DEBUG] prompt len={len(prompt)}")
    try:
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.8,
                "num_predict": 1200
            }
        }
        req = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        print("  [DEBUG] POST /api/chat ...")
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read().decode())
            resp = d.get("message", {}).get("content", "").strip()
        print(f"  [DEBUG] Qwen OK len={len(resp)}")
        return resp if len(resp) >= 10 else None
    except urllib.error.URLError as e:
        print(f"  [ERR] URLError: {e}")
        return None
    except socket.timeout:
        print("  [ERR] Timeout 300s")
        return None
    except Exception as e:
        print(f"  [ERR] {type(e).__name__}: {e}")
        return None
    except socket.timeout:
        print("  [ERR] Timeout 180s")
        return None
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f"  [ERR] {type(e).__name__}: {e}")
        return None

def build_fallback_creative():
    return """
Idea 1: Il Countdown Interattivo
Concept: Post che mostrano il tempo rimanente con grafica minimalista
Perché funziona: Crea urgenza senza aggressività
Rischio: Può diventare ripetitivo

Idea 2: Sostenibilità in Tech — Metafora Visiva
Concept: Metafora che collega codice a crescita naturale
Perché funziona: Coinvolge emotivamente
Rischio: Astratto per target tecnico

Idea 3: Q&A Live Pre-Event
Concept: Post con domande aperte alla community
Perché funziona: Favorisce partecipazione
Rischio: Bassa risposta senza incentivi
"""

def extract_facts_from_brief(brief_text):
    facts = {
        "event_name": None, "date": None, "location": None, "organizer": None,
        "target": None, "objective": None, "time": None, "venue": None,
        "speaker": None, "budget": None, "link": None, "hashtag": None
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
                    'budget': 'budget', 'link': 'link', 'hashtag': 'hashtag'
                }
                if key in mapping:
                    facts[mapping[key]] = value
    if not facts['event_name']:
        for line in text.split('\n'):
            if line.strip() and ':' not in line:
                facts['event_name'] = line.strip()
                break
    return facts

def build_structured_plan(facts):
    event = facts.get('event_name', 'DA DEFINIRE')
    date = facts.get('date', 'DA DEFINIRE')
    location = facts.get('location', 'DA DEFINIRE')
    organizer = facts.get('organizer') or 'DA DEFINIRE'
    target = facts.get('target') or 'DA DEFINIRE'
    objective = facts.get('objective') or 'DA DEFINIRE'
    time = facts.get('time') or 'DA DEFINIRE'
    venue = facts.get('venue') or 'DA DEFINIRE'
    speaker = facts.get('speaker') or 'DA DEFINIRE'
    hashtag = facts.get('hashtag') or '#Evento #Innovazione'
    event = facts.get('event_name') or 'DA DEFINIRE'
    date = facts.get('date') or 'DA DEFINIRE'
    location = facts.get('location') or 'DA DEFINIRE'
    event_name = facts.get('event_name')

    reach_agent = ReachAgent(facts)
    reach_report = reach_agent.get_reach_report()
    popular_hashtags = get_hashtags_for_event(facts, count=10)
    hashtag_list = " ".join(popular_hashtags[:10])

    return f"""
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
**Tono di Voce:** Caldo, divertente, informale.

---

2. AGENT REACH — Stima Reach Potenziale
{reach_report}

---

3. HASHTAG POPOLARI (Generati per il settore)

**Set raccomandato:**
{hashtag_list}

**Hashtag principale:** {hashtag}

📌 Consigli: 5-7 IG, 3-5 LinkedIn, 2-3 Twitter. Alterna per evitare shadowban.

---

4. PIANO SOCIAL PER PIATTAFORMA

**LINKEDIN** — Reach: {reach_agent.estimate_linkedin():,}
- Annuncio 2 settimane prima
- Articoli settimanali, testimonianze
- Pagina evento, recap post-evento

**INSTAGRAM** — Reach: {reach_agent.estimate_instagram():,}
- Stories countdown giornaliero
- Reels backstage/highlights
- Carousel educativi, Highlights

**TWITTER/X** — Reach: {reach_agent.estimate_twitter():,}
- Live coverage evento
- Thread aggiornamenti 30-60min
- Hashtag ufficiale: {hashtag}

---

5. CONTENUTI PER PIATTAFORMA

**LinkedIn:** Annuncio, Perché partecipare, Intervista speaker, Countdown, Recap
**Instagram:** Reel teaser, Reel backstage, Reel highlights, Carousel motivi, Carousel temi
**Twitter/X:** Thread agenda, Thread live, Thread momenti salienti

---

6. CTA

1. 📍 Conferma la tua presenza — [LINK DA DEFINIRE]
2. 💬 Partecipa — usa {hashtag}
3. 🔔 Segui per aggiornamenti
4. 📧 Richiedi info — contatta organizer

---

7. VISUAL (Descrittivo)

Atmosfera: divertente, calda, luminosa, accogliente
Soggetti: amici, sorrisi, momenti di convivialità
Colori: palette calda e accogliente, toni dorati e marine
Formati: LinkedIn 1200x627, IG 1080x1080/1920, TW 1200x675

---

8. TIMELINE

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

def main():
    print("\n" + "="*60)
    print("🕷️ iCRAWLER V1.8.1 HYBRID — Agent Reach + Hashtag")
    print("="*60 + "\n")

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            brief = f.read()
    else:
        brief = sys.stdin.read()

    if not brief.strip():
        print("❌ Nessun brief")
        return

    facts = extract_facts_from_brief(brief)
    print("📋 FACTS:")
    for k, v in facts.items():
        print(f"  {k}: {v if v else 'DA DEFINIRE'}")

    print("\n📚 KB RETRIEVAL:")
    retriever = KnowledgeRetriever()
    context = retriever.retrieve(platform='linkedin')
    print(f"  Style: {len(context.get('style_rules', []))} | Platform: {len(context.get('platform_rules', []))} | Content: {len(context.get('content_rules', []))}")

    print("\n📋 PIANO STRUTTURATO:")
    structured_plan = build_structured_plan(facts)
    print("  ✅ Generato con Reach Agent + Hashtag")

    print("\n🎨 CREATIVE LAB:")
    print("  ⏳ Qwen...")
    creative = generate_creative_with_qwen(facts)
    if creative:
        print("  ✅ Qwen OK")
        creative_lab = f"\n💡 CREATIVE LAB\n{creative}"
    else:
        print("  ⚠️ Fallback")
        creative_lab = f"\n💡 CREATIVE LAB\n{build_fallback_creative()}"

    try:
        gate = CreativeGate(facts)
        creative_lab, warnings = gate.enforce(creative_lab)
        if warnings:
            print(f"  ⚠️ Gate: {len(warnings)} warnings")
    except Exception:
        pass

    print("\n" + "="*60)
    print("📋 PIANO COMPLETO")
    print("="*60)
    print(structured_plan)
    print(creative_lab)
    print("="*60)

    print(f"\n📊 STATISTICHE")
    print(f"  Caratteri: {len(structured_plan) + len(creative_lab)}")
    print(f"  Sezioni: 8 | Piattaforme: 3")
    print(f"  Reach totale: {sum(ReachAgent(facts).get_all_estimates().values()):,}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = f"output_plan_hybrid_{ts}.txt"
    with open(out, 'w') as f:
        f.write(structured_plan)
        f.write(creative_lab)
    print(f"  💾 Salvato: {out}")
    print("\n🏁 DONE")

if __name__ == "__main__":
    main()
