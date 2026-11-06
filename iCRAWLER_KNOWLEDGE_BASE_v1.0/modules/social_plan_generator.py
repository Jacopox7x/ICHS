"""
Generatore di piano social basato su facts
"""

import re
from typing import Dict, List

def get_platforms(facts: Dict[str, str]) -> List[str]:
    text = str(facts).lower()
    if any(kw in text for kw in ['manager', 'ceo', 'business', 'strategia', 'b2b']):
        return ['LinkedIn', 'Twitter/X']
    elif any(kw in text for kw in ['festa', 'party', 'divertimento', 'amici']):
        return ['Instagram', 'WhatsApp', 'TikTok']
    else:
        return ['LinkedIn', 'Instagram', 'Twitter/X']

def get_hashtag(facts: Dict[str, str]) -> str:
    hashtag = facts.get('hashtag')
    if hashtag and hashtag != 'DA DEFINIRE':
        return hashtag
    event = facts.get('event_name', '')
    if event:
        # Crea hashtag dal nome evento (senza spazi)
        hashtag = '#' + ''.join(word.capitalize() for word in event.split()[:3])
        return hashtag
    return '#Evento #Innovazione'

def generate_social_plan(facts: Dict[str, str]) -> Dict[str, str]:
    platforms = get_platforms(facts)
    hashtag = get_hashtag(facts)
    return {
        'platforms': platforms,
        'hashtag': hashtag
    }
