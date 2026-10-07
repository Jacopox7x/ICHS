"""
Runner sandbox CreAzioni Migranti.
Estrae fatti dal brief PURO, poi adatta TUTTO l'output al contesto sandbox.
"""
import json
import sys
import io
import contextlib
import re
from pathlib import Path

ICRAWLER_PATH = Path(__file__).parent.parent.parent / "iCRAWLER_KNOWLEDGE_BASE_v1.0"
sys.path.insert(0, str(ICRAWLER_PATH))

from fact_extractor.regex_extractor import extract_with_regex
from fact_extractor.post_processor import post_process
from modules.search_agent import get_live_insights
from modules.systemic_rules import apply_systemic_rules


def load_sandbox():
    base = Path(__file__).parent
    with open(base / "context.json") as f:
        context = json.load(f)
    with open(base / "lessico.json") as f:
        lessico = json.load(f)
    return context, lessico


def clean_facts(facts: dict, brief: str = "") -> dict:
    """Pulisce i facts da newline, prefissi e testo spurio."""
    cleaned = {}
    bad_locations = [
        "Bonomelli", "Via", "Data", "Target", "Obiettivo", "Tema",
        "Periodo", "Location", "Brindisi", "Auguri", "Festa", "DA DEFINIRE"
    ]
    brief_lower = brief.lower()

    for key, value in facts.items():
        if isinstance(value, str):
            value = re.sub(
                r'^(Evento|Data|Location|Target|Obiettivo|Tema|Organizer|Venue|Time|Speaker|Budget|Link|Hashtag|Periodo)\s*:\s*',
                '', value, flags=re.IGNORECASE
            )

            if key in ["event_name", "location", "target", "date", "time", "venue",
                       "speaker", "organizer", "budget", "link", "hashtag"]:
                value = value.split("\n")[0].strip()
            elif key == "objective":
                value = value.split("\n")[0].strip()

            if key == "event_name":
                value = re.sub(r'\s*Data\s*:.*$', '', value, flags=re.IGNORECASE).strip()
                value = re.sub(r'\s*Location\s*:.*$', '', value, flags=re.IGNORECASE).strip()

            # Correggi location
            if key == "location":
                if value in bad_locations or not value:
                    if "cremona" in brief_lower:
                        value = "Cremona"
                    else:
                        value = "DA DEFINIRE"

        cleaned[key] = value
    return cleaned


def build_positioning(facts: dict, context: dict) -> str:
    target = facts.get("target", "comunità")
    hashtags = [h for a in context['anime'] for h in a['hashtag']]
    hashtags_str = "\n".join([f"  {i+1}. {h}" for i, h in enumerate(hashtags)])
    platforms_str = "\n".join([f"  - {c}" for c in context['canali']['prioritari']])

    return f"""============================================================
📊 POSIZIONAMENTO STRATEGICO — {context['nome']}
============================================================

🎯 TARGET PRIMARIO
  {target}

🎯 TARGET SECONDARI
  - Famiglie cremonesi
  - Appassionati di artigianato e cucito
  - Sostenitori dell'economia circolare

📱 PIATTAFORME PRIORITARIE
{platforms_str}

🏷️ HASHTAG RACCOMANDATI
{hashtags_str}

📍 LOCATION
  {context['contatti']['indirizzo']}

⏰ ORARI CONSIGLIATI
  Instagram: 18:00-20:00 (dopo il lavoro)
  Facebook: 12:00-14:00 e 19:00-21:00

💡 CONSIGLIO DI POSIZIONAMENTO
  Posiziona {context['nome']} come il punto di riferimento per la comunità
  di Cremona che cerca un luogo dove imparare, creare e stare insieme.
  Usa un tono caldo e accogliente, ma concreto: racconta le mani che
  lavorano, non solo i risultati.

🎨 VALORI DA COMUNICARE
  {', '.join(context['valori'])}

📞 CONTATTI
  WhatsApp: {context['contatti']['whatsapp']}
  Email: {context['contatti']['email']}
  Instagram: {context['contatti']['instagram']}

============================================================"""


def adapt_plan(plan: dict, context: dict, lessico: dict) -> dict:
    result = dict(plan)
    result["hashtags"] = [h for anima in context["anime"] for h in anima["hashtag"]]
    result["cta"] = [
        "🧵 Vieni a trovarci in laboratorio",
        "✂️ Impara a cucire con noi",
        "🎁 Regala un oggetto che ha una storia",
        "🤝 Sostieni il progetto",
    ]
    result["visual"] = {
        "atmosfera": "calda, concreta, artigianale, accogliente",
        "soggetti": "mani che lavorano, tessuti wax, volti, macchine da cucire",
        "colori": "toni caldi e terrosi, blu notte, giallo ocra, rosso wax",
    }
    result["posting_times"] = {
        "Instagram": "18:00-20:00 (dopo il lavoro)",
        "Facebook": "12:00-14:00 e 19:00-21:00",
        "LinkedIn": "08:30-10:00 (martedì-giovedì)",
    }
    result["platform_priority"] = context["canali"]["prioritari"]
    result["sector"] = "sociale_artigianale"
    result["advice"] = (
        f"Posiziona {context['nome']} come il punto di riferimento "
        f"per la comunità di Cremona. Tono caldo e accogliente, ma concreto."
    )
    result["sandbox"] = context["id"]
    result["organizzazione"] = context["nome"]
    result["canali_prioritari"] = context["canali"]["prioritari"]
    result["valori"] = context["valori"]
    result["parole_chiave"] = lessico["parole_da_usare"]
    return result


def run(brief_path_or_text: str) -> dict:
    context, lessico = load_sandbox()

    brief_path = Path(brief_path_or_text)
    if brief_path.exists():
        with open(brief_path) as f:
            brief = f.read()
    else:
        brief = brief_path_or_text

    with contextlib.redirect_stdout(io.StringIO()):
        raw_facts = extract_with_regex(brief)
        facts = post_process(raw_facts, brief)
        facts = clean_facts(facts, brief)

        facts_for_search = dict(facts)
        facts_for_search["location"] = "Cremona"
        insights = get_live_insights(facts_for_search)

        base_plan = apply_systemic_rules(facts)

    adapted_plan = adapt_plan(base_plan, context, lessico)
    positioning = build_positioning(facts, context)

    return {
        "facts": facts,
        "piano_social": adapted_plan,
        "positioning": positioning,
        "web_insights": insights,
        "sandbox": context["id"],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python runner.py <brief.txt | 'testo brief'>")
        sys.exit(1)

    arg = sys.argv[1]
    result = run(arg)
    print(json.dumps(result, indent=2, ensure_ascii=False))
