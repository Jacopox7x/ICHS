import re
from typing import Dict

MONTHS = {
    'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
    'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre',
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
}

CITIES = [
    'Roma', 'Milano', 'Torino', 'Bologna', 'Firenze', 'Rovigo',
    'Venezia', 'Napoli', 'Genova', 'Palermo', 'Bari', 'Verona',
    'Foggia', 'Pescara', 'Lecce', 'Taranto', 'Brindisi'
]

def extract_city(text: str) -> str:
    if not text:
        return 'DA DEFINIRE'
    for city in CITIES:
        if re.search(rf'\b{re.escape(city)}\b', text, re.IGNORECASE):
            return city
    match = re.search(r'(?:a|in|tra)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
    if match:
        candidate = match.group(1).strip()
        if candidate.lower() not in ['città', 'parte', 'tutta', 'europa', 'italia', 'birra']:
            return candidate
    return 'DA DEFINIRE'

def extract_date(text: str) -> str:
    if not text:
        return 'DA DEFINIRE'
    patterns = [
        r'(\d{1,2}\s*[-–]\s*\d{1,2}\s+[A-Za-z]+)',
        r'(\d{1,2}\s+[A-Za-z]+)',
        r'(\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            if len(date_str) == 4 and date_str.isdigit():
                if 2000 <= int(date_str) <= 2099:
                    return date_str
            parts = date_str.split()
            if len(parts) >= 2 and parts[-1].lower() in MONTHS:
                return date_str
    return 'DA DEFINIRE'

def extract_target(text: str) -> str:
    if not text:
        return 'DA DEFINIRE'
    match = re.search(r'(?:per|rivolto a)\s+([^.,;]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return 'DA DEFINIRE'

def extract_objective(text: str) -> str:
    if not text:
        return 'DA DEFINIRE'
    match = re.search(r'(?:Obiettivo|Scopo|objective|goal)[\s:]*([^.,;]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return 'DA DEFINIRE'

def get_default_target(text: str) -> str:
    text = text.lower()
    if 'fiera' in text or 'salone' in text:
        return 'professionisti del settore'
    elif 'convegno' in text or 'conferenza' in text:
        return 'addetti ai lavori e studiosi'
    elif 'festival' in text or 'festa' in text:
        return 'appassionati e famiglie'
    elif 'cena' in text:
        return 'partecipanti e sostenitori'
    else:
        return 'pubblico interessato'

def get_default_objective(text: str) -> str:
    text = text.lower()
    if 'fiera' in text or 'salone' in text:
        return 'attrarre professionisti e creare opportunita di business'
    elif 'convegno' in text or 'conferenza' in text:
        return 'condividere conoscenze e fare networking'
    elif 'festival' in text or 'festa' in text:
        return "creare un'esperienza di divertimento e condivisione"
    elif 'cena' in text:
        return 'raccogliere fondi e sensibilizzare i partecipanti'
    else:
        return 'promuovere levento e coinvolgere il pubblico'

def clean_event_name(event_name: str, full_text: str) -> str:
    # NON TOCCARE IL NOME EVENTO
    return event_name

def post_process(facts: Dict[str, str], full_text: str) -> Dict[str, str]:
    result = facts.copy()
    result['location'] = extract_city(full_text)
    result['date'] = extract_date(full_text)
    if result.get('objective') in (None, 'DA DEFINIRE'):
        obj = extract_objective(full_text)
        if obj != 'DA DEFINIRE':
            result['objective'] = obj
        else:
            result['objective'] = get_default_objective(full_text)
    if result.get('target') in (None, 'DA DEFINIRE'):
        tgt = extract_target(full_text)
        if tgt != 'DA DEFINIRE':
            result['target'] = tgt
        else:
            result['target'] = get_default_target(full_text)
    result['event_name'] = clean_event_name(
        result.get('event_name', ''),
        full_text
    )
    return result
