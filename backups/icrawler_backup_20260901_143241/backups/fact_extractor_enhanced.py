import re

def extract_facts_enhanced(text):
    """Estrae facts da brief - VERSIONE CON LOCATION FIX"""
    facts = {
        'event_name': 'DA DEFINIRE',
        'date': 'DA DEFINIRE',
        'location': 'DA DEFINIRE',
        'organizer': 'DA DEFINIRE',
        'target': 'DA DEFINIRE',
        'objective': 'DA DEFINIRE',
        'time': 'DA DEFINIRE',
        'venue': 'DA DEFINIRE',
        'speaker': 'DA DEFINIRE',
        'budget': 'DA DEFINIRE',
        'link': 'DA DEFINIRE',
        'hashtag': 'DA DEFINIRE'
    }
    
    # ========== EVENT NAME ==========
    match = re.search(r'(?:evento:|nome:|titolo:\s*)([^.\n]+)', text, re.IGNORECASE)
    if match:
        facts['event_name'] = match.group(1).strip()
    else:
        first_part = text.split('.')[0]
        if ' il ' in first_part:
            facts['event_name'] = first_part.split(' il ')[0].strip()
        else:
            facts['event_name'] = first_part[:50].strip()
    
    # ========== DATE ==========
    date_patterns = [
        r'(\d{1,2}\s+(?:Gennaio|Febbraio|Marzo|Aprile|Maggio|Giugno|Luglio|Agosto|Settembre|Ottobre|Novembre|Dicembre)\s+\d{4})',
        r'(\d{1,2}\s+(?:Gennaio|Febbraio|Marzo|Aprile|Maggio|Giugno|Luglio|Agosto|Settembre|Ottobre|Novembre|Dicembre))(?=\s|\.|,|$)',
        r'il\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        r'(\d{1,2}\s+[A-Za-z]+)(?=\s|\.|,|$)'
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            facts['date'] = match.group(1).strip()
            break
    
    # ========== LOCATION (FIX) ==========
    # Pattern più precisi per catturare "a Rovigo", "in Rovigo", "Rovigo"
    location_patterns = [
        r'a\s+([A-Z][a-z]+)(?=\s|\.|,|$|-)',  # a Rovigo
        r'in\s+([A-Z][a-z]+)(?=\s|\.|,|$|-)', # in Rovigo
        r'location:\s*([^.,;]+)',
        r'([A-Z][a-z]+)(?=\s*\.|\s*,|\s*$)'   # Rovigo alla fine
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            loc = match.group(1).strip()
            # Filtra parole comuni che non sono città
            if len(loc) > 3 and len(loc) < 30 and loc.lower() not in ['tutta', 'parte', 'settore', 'tutti', 'europa', 'italia']:
                facts['location'] = loc
                break
    
    # ========== TARGET ==========
    target_keywords = ['operai', 'manager', 'professionisti', 'studenti', 'imprenditori', 'famiglie', 'turisti', 'giovani', 'lavoratori']
    found = [kw for kw in target_keywords if kw in text.lower()]
    match = re.search(r'(?:rivolto a|per|target:\s*)([^.,;]+)', text, re.IGNORECASE)
    if match:
        target_text = match.group(1).strip()
        if target_text and len(target_text) < 50:
            facts['target'] = target_text
    elif found:
        facts['target'] = ', '.join(found)
    
    # ========== OBJECTIVE ==========
    objective_keywords = ['attirare', 'promuovere', 'raccogliere', 'formare', 'sensibilizzare', 'creare', 'coinvolgere', 'aggiornamento', 'aggiornare', 'informare', 'fare networking', 'incontrare', 'sviluppare', 'networking', 'pitch']
    for kw in objective_keywords:
        if kw in text.lower():
            sentences = text.split('.')
            for s in sentences:
                if kw in s.lower():
                    obj = s.strip()
                    if len(obj) > 5 and len(obj) < 200:
                        facts['objective'] = obj
                        break
            if facts['objective'] != 'DA DEFINIRE':
                break
    
    # ========== ORGANIZER ==========
    match = re.search(r'(?:organizzato da|organizzatore:\s*)([^.,;]+)', text, re.IGNORECASE)
    if match:
        facts['organizer'] = match.group(1).strip()
    
    # ========== HASHTAG ==========
    match = re.search(r'(#[a-zA-Z0-9_]+)', text)
    if match:
        facts['hashtag'] = match.group(1)
    
    return facts
