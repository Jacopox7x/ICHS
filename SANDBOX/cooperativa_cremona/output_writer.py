"""
Output Writer — Converte l'output JSON in Markdown formattato.
"""
import json
import sys
from datetime import datetime
from pathlib import Path


def load_sandbox():
    base = Path(__file__).parent
    with open(base / "context.json") as f:
        context = json.load(f)
    return context


def to_markdown(data: dict, context: dict) -> str:
    """Converte l'output JSON in Markdown."""
    facts = data.get("facts", {})
    plan = data.get("piano_social", {})
    positioning = data.get("positioning", "")
    insights = data.get("web_insights", {})
    
    md = f"""# Piano Social — {context['nome']}

**Generato:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Sandbox:** `{data.get('sandbox', 'N/D')}`

---

## 📋 Dati Evento

| Campo | Valore |
|-------|--------|
| **Evento** | {facts.get('event_name', 'N/D')} |
| **Data** | {facts.get('date', 'N/D')} |
| **Location** | {facts.get('location', 'N/D')} |
| **Target** | {facts.get('target', 'N/D')} |
| **Obiettivo** | {facts.get('objective', 'N/D')} |

---

## 📱 Piano Social

### Piattaforme prioritarie
{chr(10).join(['- ' + p for p in plan.get('platform_priority', [])])}

### Orari di pubblicazione
| Piattaforma | Orario |
|-------------|--------|
| Instagram | {plan.get('posting_times', {}).get('Instagram', 'N/D')} |
| Facebook | {plan.get('posting_times', {}).get('Facebook', 'N/D')} |

### Hashtag
{' '.join(plan.get('hashtags', []))}

### CTA
{chr(10).join(['- ' + c for c in plan.get('cta', [])])}

### Visual
- **Atmosfera:** {plan.get('visual', {}).get('atmosfera', 'N/D')}
- **Soggetti:** {plan.get('visual', {}).get('soggetti', 'N/D')}
- **Colori:** {plan.get('visual', {}).get('colori', 'N/D')}

---

## 📊 Positioning

{positioning}

---

## 🌐 Web Insights

### Notizie correlate
{chr(10).join([f"- [{n['title']}]({n['url']})" for n in insights.get('news', [])[:5]])}

### Immagini
{chr(10).join([f"- {img}" for img in insights.get('images', [])[:5]])}

---

*Generato da iCrawler + Sandbox {context['nome']}*
"""
    return md


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python output_writer.py <output_json>")
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        data = json.load(f)
    
    context = load_sandbox()
    md = to_markdown(data, context)
    
    # Salva in file
    output_path = sys.argv[1].replace(".json", ".md")
    with open(output_path, "w") as f:
        f.write(md)
    
    print(f"✅ Markdown salvato: {output_path}")
    print()
    print(md)
