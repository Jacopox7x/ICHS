"""
Site Optimizer — Genera testi per il sito della cooperativa.
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


def generate_home(context: dict, lessico: dict) -> str:
    return f"""# {context['nome']}

## Intrecciamo fili, culture e storie.

{context['nome']} è un luogo dove il cucito diventa occasione di incontro, formazione e riscatto. Qui persone provenienti da percorsi diversi trovano uno spazio accogliente in cui imparare un mestiere, valorizzare le proprie competenze e costruire nuove opportunità.

### Cosa facciamo
- **Sartoria sociale** — creiamo abiti, accessori e oggetti unici utilizzando tessuti wax, materiali di recupero e tessuti di giacenza.
- **Laboratori** — corsi di cucito per bambini, adulti, scuole, gruppi e associazioni.
- **Economia circolare** — diamo una seconda vita ai tessuti e alle persone.

### I nostri valori
{chr(10).join(['- **' + v.capitalize() + '**' for v in context['valori']])}

### Vieni a trovarci
📍 {context['contatti']['indirizzo']}
📩 {context['contatti']['whatsapp']}
✉️ {context['contatti']['email']}

[Scopri le nostre creazioni →]({context['shop']['url']})
"""


def generate_about(context: dict, lessico: dict) -> str:
    return f"""# Chi siamo

{context['nome']} è nata all'interno della cooperativa {context['casa_madre']['nome']}. Offriamo opportunità lavorative e percorsi di crescita a persone in situazione di fragilità.

## Il nostro progetto

Il lavoro in sartoria diventa uno strumento concreto di autonomia, integrazione e valorizzazione delle competenze. Ogni giorno intrecciamo fili, culture e storie.

## I nostri laboratori

Organizziamo laboratori creativi dedicati a bambini, adulti, scuole, gruppi e associazioni. Esperienze dove il tessuto diventa linguaggio, relazione e occasione di condivisione.

## Le nostre creazioni

Realizziamo abiti, accessori e oggetti unici utilizzando tessuti wax, materiali di recupero e tessuti di giacenza. Ogni creazione nasce dall'incontro tra artigianato, sostenibilità e inclusione.

**Nessun prodotto è uguale a un altro.**

## I nostri valori
{chr(10).join(['- **' + v.capitalize() + '**' for v in context['valori']])}

## Contatti
📍 {context['contatti']['indirizzo']}
📩 {context['contatti']['whatsapp']}
✉️ {context['contatti']['email']}
📷 {context['contatti']['instagram']}
"""


def generate_shop_intro(context: dict, lessico: dict) -> str:
    return f"""# Le nostre CreAzioni

Ogni pezzo racconta una storia.

Realizziamo abiti, accessori e oggetti unici utilizzando tessuti wax, materiali di recupero e tessuti di giacenza.

## Perché scegliere le nostre creazioni
- **Pezzi unici** — nessun prodotto è uguale a un altro
- **Artigianato** — fatto a mano a Cremona
- **Sostenibilità** — materiali di recupero, economia circolare
- **Impatto sociale** — ogni acquisto sostiene un progetto

## Le categorie
{chr(10).join(['- **' + c + '**' for c in context['shop']['categorie']])}

[Vai allo shop →]({context['shop']['url']})
"""


if __name__ == "__main__":
    context, lessico = load_sandbox()
    
    print("=" * 60)
    print("🏠 HOME PAGE")
    print("=" * 60)
    print(generate_home(context, lessico))
    print()
    print("=" * 60)
    print("👥 ABOUT US")
    print("=" * 60)
    print(generate_about(context, lessico))
    print()
    print("=" * 60)
    print("🛍️ SHOP INTRO")
    print("=" * 60)
    print(generate_shop_intro(context, lessico))
