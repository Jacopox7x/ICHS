"""
Modulo posizionamento strategico per iCrawler
"""

import re
from typing import Dict, List

def get_hashtags(facts: Dict, text: str) -> List[str]:
    from modules.hashtag_generator import generate_hashtags
    return generate_hashtags(text, facts)

def get_reach(facts: Dict) -> Dict:
    try:
        from modules.reach_estimator import get_reach_report
        return get_reach_report(facts, "")
    except:
        return {'linkedin': 5000, 'instagram': 10000, 'twitter': 3000}

def get_platforms(facts: Dict) -> List[str]:
    text = str(facts).lower()
    if any(kw in text for kw in ['manager', 'ceo', 'business', 'strategia', 'b2b']):
        return ['LinkedIn', 'Twitter/X']
    elif any(kw in text for kw in ['festa', 'party', 'divertimento', 'amici']):
        return ['Instagram', 'WhatsApp', 'TikTok']
    else:
        return ['LinkedIn', 'Instagram', 'Twitter/X']

def get_posting_times(facts: Dict) -> Dict:
    text = str(facts).lower()
    if 'festa' in text or 'party' in text:
        return {
            'LinkedIn': '16:00-18:00 (venerdì)',
            'Instagram': '19:00-22:00 (sera)',
            'Twitter': '20:00-23:00 (sera)'
        }
    else:
        return {
            'LinkedIn': '08:30-10:00 (martedì-giovedì)',
            'Instagram': '12:00-14:00 (pranzo)',
            'Twitter': '09:00-11:00 (mattina)'
        }

def get_secondary_targets(facts: Dict) -> List[str]:
    text = str(facts).lower()
    targets = []
    if 'manager' in text or 'ceo' in text:
        targets.append('Giovani professionisti')
    if 'studenti' in text or 'università' in text:
        targets.append('Docenti e ricercatori')
    if 'famiglie' in text:
        targets.append('Genitori')
    if 'turisti' in text:
        targets.append('Viaggiatori')
    return targets if targets else ['Comunità locale']

def extract_objective_from_text(text: str) -> str:
    match = re.search(r'(?:Obiettivo|Scopo|obiettivo|scopo):?\s*([^.,;]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    keywords = ['attirare', 'promuovere', 'formare', 'sensibilizzare', 'creare', 'raccogliere', 'divertire']
    for kw in keywords:
        if kw in text.lower():
            sentences = text.split('.')
            for s in sentences:
                if kw in s.lower():
                    return s.strip()
    return None

def get_default_objective(facts: Dict, text: str) -> str:
    event = facts.get('event_name', '')
    target = facts.get('target', '')
    if 'fiera' in event.lower() or 'salone' in event.lower():
        return f"attrarre professionisti del settore e creare opportunità di business"
    elif 'convegno' in event.lower() or 'conferenza' in event.lower():
        return f"condividere conoscenze e fare networking tra {target if target else 'i partecipanti'}"
    elif 'festival' in event.lower() or 'festa' in event.lower():
        return f"creare un'esperienza di divertimento e condivisione"
    else:
        return f"creare valore e coinvolgimento per {target if target else 'i partecipanti'}"

def generate_positioning_advice(facts: Dict, text: str) -> str:
    target = facts.get('target', '')
    objective = facts.get('objective', '')
    if objective == 'DA DEFINIRE':
        objective = extract_objective_from_text(text)
    if not objective:
        objective = get_default_objective(facts, text)
    tone = 'informale e caldo' if any(kw in str(facts).lower() for kw in ['festa', 'party', 'divertimento']) else 'professionale e autorevole'
    if target and objective:
        return f"Posiziona l'evento come il punto di riferimento per {target} che cercano {objective}. Usa un tono {tone}."
    elif target:
        return f"Target principale: {target}. Usa messaggi che parlano direttamente alle loro esigenze."
    else:
        return "Focus sul posizionamento: chiara proposta di valore e differenziazione."

def build_positioning_report(text: str, facts: Dict) -> str:
    report = []
    report.append("="*60)
    report.append("📊 POSIZIONAMENTO STRATEGICO")
    report.append("="*60)
    
    report.append("\n🎯 TARGET PRIMARIO")
    report.append(f"  {facts.get('target', 'DA DEFINIRE')}")
    
    secondary = get_secondary_targets(facts)
    if secondary:
        report.append("\n🎯 TARGET SECONDARI")
        for t in secondary:
            report.append(f"  - {t}")
    
    platforms = get_platforms(facts)
    report.append("\n📱 PIATTAFORME PRIORITARIE")
    for p in platforms:
        report.append(f"  - {p}")
    
    hashtags = get_hashtags(facts, text)
    report.append("\n🏷️ HASHTAG RACCOMANDATI")
    for i, tag in enumerate(hashtags[:10], 1):
        report.append(f"  {i}. {tag}")
    
    # Reach con spiegazione (da reach_estimator se disponibile)
    try:
        from modules.reach_estimator import get_reach_report
        reach_data = get_reach_report(facts, text)
        report.append("\n📊 REACH STIMATO")
        report.append(f"  {reach_data['total']:,} contatti potenziali")
        report.append(f"  📍 Basato su: {reach_data['location']} ({reach_data['population']:,} abitanti)")
        report.append(f"  🏷️ Settore: {reach_data['sector']}")
        report.append(f"  📈 Conversione stimata: {reach_data['conversion_rate']}")
        report.append("\n  Per piattaforma:")
        for plat, val in reach_data['reach'].items():
            report.append(f"    - {plat.capitalize()}: {val:,}")
    except:
        report.append("\n📊 REACH STIMATO")
        report.append("  18,000 contatti potenziali (stima di default)")
    
    times = get_posting_times(facts)
    report.append("\n⏰ ORARI CONSIGLIATI")
    for plat, t in times.items():
        report.append(f"  {plat}: {t}")
    
    advice = generate_positioning_advice(facts, text)
    report.append("\n💡 CONSIGLIO DI POSIZIONAMENTO")
    report.append(f"  {advice}")
    
    report.append("\n" + "="*60)
    return "\n".join(report)

def get_positioning_report(text: str, facts: Dict) -> str:
    """Funzione principale per ottenere il report di posizionamento"""
    return build_positioning_report(text, facts)
