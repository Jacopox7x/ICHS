import re
from typing import Dict

def extract_with_regex(text: str) -> Dict[str, str]:
    """Estrae facts con regex (fallback robusto)"""
    
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
    
    # DATE
    date_match = re.search(r'(\d{1,2}[-–]\d{1,2}\s+[A-Za-z]+)', text)
    if not date_match:
        date_match = re.search(r'(\d{1,2}\s+[A-Za-z]+)', text)
    if date_match:
        facts['date'] = date_match.group(1)
    
    # LOCATION
    loc_match = re.search(r'a\s+([A-Z][a-z]+)(?=\s|\.|,|$)', text)
    if loc_match:
        loc = loc_match.group(1)
        if loc not in ['Birra', 'Cultura', 'Tutta', 'Europa']:
            facts['location'] = loc
    
    # TARGET
    target_match = re.search(r'(?:per|rivolto a)\s+([^.,;]+)', text, re.IGNORECASE)
    if target_match:
        facts['target'] = target_match.group(1).strip()
    
    # OBJECTIVE
    for kw in ['promuovere', 'attirare', 'formare', 'sensibilizzare', 'creare', 'raccogliere', 'divertire', 'networking']:
        if kw in text.lower():
            for s in text.split('.'):
                if kw in s.lower():
                    facts['objective'] = s.strip()
                    break
            if facts['objective'] != 'DA DEFINIRE':
                break
    
    # EVENT NAME
    if ' il ' in text:
        facts['event_name'] = text.split(' il ')[0].strip()
    else:
        facts['event_name'] = text.split('.')[0].strip()
    if facts['date'] in facts['event_name']:
        facts['event_name'] = facts['event_name'].replace(facts['date'], '').replace(',', '').strip()
    
    # HASHTAG
    htag = re.search(r'(#[a-zA-Z0-9_]+)', text)
    if htag:
        facts['hashtag'] = htag.group(1)
    
    return facts
