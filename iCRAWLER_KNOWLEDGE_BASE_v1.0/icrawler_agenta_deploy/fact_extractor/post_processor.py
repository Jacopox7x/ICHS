import re
from typing import Dict

MONTHS = {
    'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
    'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre',
    'january', 'february', 'march', 'april', 'may', 'june',
    'july', 'august', 'september', 'october', 'november', 'december'
}

def extract_city(text: str) -> str:
    # 1. Pattern "a [Città]" o "in [Città]" o "at [Città]"
    match = re.search(r'(?:a|in|at)\s+([A-Z][a-z]+(?:[-\s][A-Z][a-z]+)*)', text, re.IGNORECASE)
    if match:
        city = match.group(1)
        if city.lower() not in ['città', 'parte', 'tutta', 'europa', 'italia']:
            return city
    # 2. Pattern "[Città] Convention Centre"
    match = re.search(r'([A-Z][a-z]+(?:[-\s][A-Z][a-z]+)*)\s+(?:Convention|Center|Expo|Fair|Exhibition)', text)
    if match:
        return match.group(1)
    # 3. Pattern "[Città], [Paese]"
    match = re.search(r'([A-Z][a-z]+(?:[-\s][A-Z][a-z]+)*)\s*,\s*[A-Z]', text)
    if match:
        return match.group(1)
    # 4. Cerca città comuni nel testo
    common_cities = ['Milano', 'Roma', 'Torino', 'Bologna', 'Firenze', 'Rovigo',
                     'Venezia', 'Napoli', 'Genova', 'Palermo', 'Bari', 'Verona',
                     'Dallas', 'Melbourne', 'Tokyo', 'Berlin', 'Paris', 'London',
                     'New York', 'San Francisco', 'Singapore', 'Sydney', 'Dubai']
    for city in common_cities:
        if re.search(rf'\b{city}\b', text, re.IGNORECASE):
            return city
    # 5. Fallback: qualsiasi parola con maiuscola non all'inizio
    words = re.findall(r'[A-Z][a-z]+', text)
    for w in words:
        if w.lower() not in MONTHS and len(w) > 3:
            if not re.search(rf'^[^.!?]*\b{w}\b', text):
                return w
    return 'DA DEFINIRE'

def extract_date(text: str) -> str:
    patterns = [
        r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'(\d{1,2}\s+[A-Za-z]+)(?=\s|\.|,|$)',
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
            if len(parts) >= 2:
                month = parts[-1].lower()
                if month in MONTHS:
                    return date_str
    return 'DA DEFINIRE'

def extract_objective(text: str) -> str:
    match = re.search(r'(?:Obiettivo|Scopo|objective|goal):?\s*([^.,;]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return 'DA DEFINIRE'

def clean_event_name(event_name: str, full_text: str) -> str:
    if not event_name or event_name == 'DA DEFINIRE':
        return 'DA DEFINIRE'
    
    # 1. Rimuovi la data
    date = extract_date(full_text)
    if date != 'DA DEFINIRE':
        event_name = re.sub(rf'\s*{date}\s*', ' ', event_name)
        event_name = re.sub(r'\s*\d{4}\s*', ' ', event_name)
        event_name = re.sub(r'\s*20\s*', ' ', event_name)
    
    # 2. Rimuovi TUTTE le città (senza preposizione)
    city = extract_city(full_text)
    if city and city != 'DA DEFINIRE':
        # Rimuovi "a Dallas", "in Dallas", "at Dallas"
        event_name = re.sub(rf'\s*(?:a|in|at)\s*{city}\b', '', event_name, flags=re.IGNORECASE)
        # Rimuovi "Dallas" da sola (alla fine o in mezzo)
        event_name = re.sub(rf'\s*{city}\b', '', event_name, flags=re.IGNORECASE)
    
    # 3. Rimuovi "Convention Centre", "Center", "Expo"
    event_name = re.sub(r'\s+(?:Convention|Center|Expo|Fair|Exhibition)\s+(?:Centre)?', ' ', event_name, flags=re.IGNORECASE)
    
    # 4. Rimuovi preposizioni residue
    event_name = re.sub(r'\s*il\s*', ' ', event_name)
    event_name = re.sub(r'\s*at\s*', ' ', event_name)
    event_name = re.sub(r'\s*a\s*$', '', event_name)
    event_name = re.sub(r'^\s*a\s*', '', event_name)
    
    # 5. Rimuovi numeri isolati
    event_name = re.sub(r'\s*\d+\s*', ' ', event_name)
    
    # 6. Pulisci spazi e virgole
    event_name = re.sub(r'\s+', ' ', event_name).strip()
    event_name = event_name.strip().strip(',')
    
    return event_name if len(event_name) > 3 else 'DA DEFINIRE'

def post_process(facts: Dict[str, str], full_text: str) -> Dict[str, str]:
    result = facts.copy()
    result['location'] = extract_city(full_text)
    result['date'] = extract_date(full_text)
    if result.get('objective') == 'DA DEFINIRE':
        result['objective'] = extract_objective(full_text)
    result['event_name'] = clean_event_name(
        result.get('event_name', ''),
        full_text
    )
    target = result.get('target', '')
    for prefix in ['Per ', 'rivolto a ', 'for ']:
        if target.startswith(prefix):
            target = target[len(prefix):]
    result['target'] = target.strip()
    return result
