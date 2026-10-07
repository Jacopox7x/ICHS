"""
Content Generator — Genera post social partendo dal piano di iCrawler.
Riconosce il tipo di evento e adatta il testo.
Adattato al contesto della sandbox CreAzioni Migranti.
"""
import json
import sys
from pathlib import Path


def load_sandbox():
    base = Path(__file__).parent
    with open(base / "context.json") as f:
        context = json.load(f)
    with open(base / "lessico.json") as f:
        lessico = json.load(f)
    return context, lessico


def detect_event_type(facts: dict) -> str:
    """Riconosce il tipo di evento dal nome e dall'obiettivo."""
    text = (facts.get("event_name", "") + " " + facts.get("objective", "")).lower()

    if any(k in text for k in ["raccolta", "donazione", "dona", "recupero tessuti"]):
        return "campagna_donazioni"
    if any(k in text for k in ["laboratorio", "corso", "workshop", "impara"]):
        return "laboratorio"
    if any(k in text for k in ["collezione", "nuova", "sfilata", "presentazione"]):
        return "nuova_collezione"
    if any(k in text for k in ["evento", "festa", "aperitivo", "incontro"]):
        return "evento_speciale"
    return "generico"


TEMPLATES = {
    "campagna_donazioni": {
        "instagram": """🧵 {event}

📅 {date}
📍 {location}

Hai tessuti che non usi più? Portali da noi.
Diventeranno borse, gonne, gilet. Diventeranno storie.

Materiali accettati: wax, cotone, lino, jeans.

📩 Info: {whatsapp}

{hashtags}""",
        "facebook": """🧵 {event}

Hai tessuti che non usi più? Portali da noi.

Nel nostro laboratorio, ogni tessuto di recupero diventa un oggetto unico: una borsa, una gonna, un gilet. E ogni oggetto diventa un'opportunità per qualcuno.

📅 {date}
📍 {location}
📩 {email}

Ritiro su appuntamento, anche a domicilio per grandi quantità.

#CreAzioniMigranti #SartoriaSociale #EconomiaCircolare""",
    },
    "laboratorio": {
        "instagram": """🧵 {event}

📅 {date}
📍 {location}

Un laboratorio dove le mani imparano, i tessuti rinascono e le persone si incontrano.

Vi aspettiamo!

📩 Info e iscrizioni: {whatsapp}

{hashtags}""",
        "facebook": """🧵 {event}

Ci sono luoghi dove il tempo scorre diversamente: dove un filo diventa una storia, un tessuto di recupero diventa un oggetto unico, e le persone si incontrano per imparare insieme.

È uno di quei luoghi.

📅 {date}
📍 {location}
📩 {email}

Ti aspettiamo. Porta la tua curiosità, al resto pensiamo noi.

#CreAzioniMigranti #SartoriaSociale #Cremona""",
    },
    "nuova_collezione": {
        "instagram": """🧵 {event}

📅 {date}
📍 {location}

Ogni pezzo racconta una storia. Nessun prodotto è uguale a un altro.

Vieni a scoprire le nuove creazioni.

📩 {whatsapp}

{hashtags}""",
        "facebook": """🧵 {event}

Ogni pezzo racconta una storia: di un tessuto ritrovato, di mani che hanno imparato, di un'opportunità che si è aperta.

Vieni a scoprire le nuove creazioni di CreAzioni Migranti.

📅 {date}
📍 {location}
📩 {email}

#CreAzioniMigranti #SartoriaSociale #NuovaCollezione""",
    },
    "evento_speciale": {
        "instagram": """🧵 {event}

📅 {date}
📍 {location}

Vi aspettiamo per un momento insieme.

📩 {whatsapp}

{hashtags}""",
        "facebook": """🧵 {event}

Un momento per stare insieme, per conoscere il nostro laboratorio, per scoprire cosa facciamo.

📅 {date}
📍 {location}
📩 {email}

Ti aspettiamo.

#CreAzioniMigranti #SartoriaSociale #Cremona""",
    },
    "generico": {
        "instagram": """🧵 {event}

📅 {date}
📍 {location}

{objective}

📩 {whatsapp}

{hashtags}""",
        "facebook": """🧵 {event}

{objective}

📅 {date}
📍 {location}
📩 {email}

Ti aspettiamo.

#CreAzioniMigranti #SartoriaSociale #Cremona""",
    },
}


def generate_post(facts: dict, plan: dict, context: dict, platform: str) -> str:
    event_type = detect_event_type(facts)
    template = TEMPLATES[event_type][platform]
    hashtags = " ".join(plan.get("hashtags", [])[:6])

    return template.format(
        event=facts.get("event_name", "Evento"),
        date=facts.get("date", "DA DEFINIRE"),
        location=facts.get("location", context['contatti']['indirizzo']),
        objective=facts.get("objective", ""),
        whatsapp=context['contatti']['whatsapp'],
        email=context['contatti']['email'],
        hashtags=hashtags,
    )


def generate_stories(facts: dict, context: dict) -> list:
    event_type = detect_event_type(facts)
    event = facts.get("event_name", "Evento")
    date = facts.get("date", "DA DEFINIRE")

    if event_type == "campagna_donazioni":
        return [
            f"🧵 {event}",
            f"Porta i tuoi tessuti\n📅 {date}",
            f"Diventeranno storie\n📩 {context['contatti']['whatsapp']}"
        ]
    elif event_type == "laboratorio":
        return [
            f"🧵 {event}",
            f"📅 {date}\n📍 Cremona",
            f"Vieni a trovarci!\n📩 {context['contatti']['whatsapp']}"
        ]
    elif event_type == "nuova_collezione":
        return [
            f"🧵 {event}",
            f"Ogni pezzo\nuna storia",
            f"Scopri le creazioni\n📩 {context['contatti']['whatsapp']}"
        ]
    else:
        return [
            f"🧵 {event}",
            f"📅 {date}\n📍 Cremona",
            f"Ti aspettiamo!\n📩 {context['contatti']['whatsapp']}"
        ]


def generate_all(facts: dict, plan: dict, context: dict) -> dict:
    event_type = detect_event_type(facts)
    return {
        "event_type": event_type,
        "instagram_post": generate_post(facts, plan, context, "instagram"),
        "facebook_post": generate_post(facts, plan, context, "facebook"),
        "instagram_story": generate_stories(facts, context),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python content_generator.py <output_json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    context, lessico = load_sandbox()
    facts = data.get("facts", {})
    plan = data.get("piano_social", {})

    contents = generate_all(facts, plan, context)

    print("=" * 60)
    print(f"🎯 TIPO EVENTO RILEVATO: {contents['event_type']}")
    print("=" * 60)
    print()
    print("=" * 60)
    print("📸 POST INSTAGRAM")
    print("=" * 60)
    print(contents["instagram_post"])
    print()
    print("=" * 60)
    print("📘 POST FACEBOOK")
    print("=" * 60)
    print(contents["facebook_post"])
    print()
    print("=" * 60)
    print("📱 STORIE INSTAGRAM")
    print("=" * 60)
    for i, slide in enumerate(contents["instagram_story"], 1):
        print(f"--- Slide {i} ---")
        print(slide)
        print()
