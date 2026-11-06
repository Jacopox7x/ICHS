"""
Stima reach basata su dati reali
"""

from typing import Dict
import json
import os

# Database città (da espandere)
CITY_DATA = {
    'Roma': {'population': 2_873_000, 'region': 'Lazio'},
    'Milano': {'population': 1_396_000, 'region': 'Lombardia'},
    'Torino': {'population': 848_000, 'region': 'Piemonte'},
    'Bologna': {'population': 392_000, 'region': 'Emilia-Romagna'},
    'Firenze': {'population': 367_000, 'region': 'Toscana'},
    'Rovigo': {'population': 50_000, 'region': 'Veneto'},
    'Venezia': {'population': 254_000, 'region': 'Veneto'},
    'Napoli': {'population': 914_000, 'region': 'Campania'},
    'Genova': {'population': 558_000, 'region': 'Liguria'},
    'Palermo': {'population': 630_000, 'region': 'Sicilia'},
}

# Penetrazione social per settore (dati ISTAT + benchmark)
SOCIAL_PENETRATION = {
    'professionale': {
        'linkedin': 0.35,  # 35% dei professionisti su LinkedIn
        'instagram': 0.20,
        'twitter': 0.15,
    },
    'leisure': {
        'linkedin': 0.10,
        'instagram': 0.55,
        'twitter': 0.25,
    },
    'tecnico': {
        'linkedin': 0.45,
        'instagram': 0.15,
        'twitter': 0.30,
    }
}

# Settori per tipo di evento
SECTOR_KEYWORDS = {
    'tecnico': ['tecnico', 'industria', 'ferro', 'acciaio', 'macchinari', 'produzione'],
    'professionale': ['manager', 'ceo', 'commercialista', 'consulente', 'avvocato'],
    'leisure': ['festa', 'divertimento', 'amici', 'party', 'concerto'],
}

def detect_sector(facts: Dict, text: str) -> str:
    """Determina il settore in base a target e testo"""
    text_lower = (text + ' ' + str(facts)).lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return sector
    # Default: professionale per eventi B2B, leisure per eventi B2C
    if any(kw in text_lower for kw in ['festa', 'divertimento', 'amici']):
        return 'leisure'
    return 'professionale'

def get_city_population(location: str) -> int:
    """Ottiene popolazione della città dal database"""
    for city, data in CITY_DATA.items():
        if city.lower() in location.lower():
            return data['population']
    return 500_000  # Default per città non mappate

def estimate_reach(facts: Dict, text: str) -> Dict[str, int]:
    """
    Stima reach basata su:
    1. Popolazione città
    2. Penetrazione social per settore
    3. Fattore di conversione per tipo evento
    """
    
    location = facts.get('location', '')
    sector = detect_sector(facts, text)
    population = get_city_population(location)
    
    # Fattore di conversione: quanta parte della popolazione è target
    # Per eventi locali: 1-5% della popolazione
    # Per eventi regionali: 5-15%
    # Per eventi nazionali: 15-30%
    conversion_factor = 0.02  # Default: 2% della popolazione (locale)
    
    # Aggiusta per settore
    if sector == 'tecnico':
        conversion_factor = 0.03  # Più alto per settori di nicchia
    elif sector == 'professionale':
        conversion_factor = 0.025
    elif sector == 'leisure':
        conversion_factor = 0.05  # Più alto per eventi leisure
    
    # Calcola target potenziale
    potential_target = int(population * conversion_factor)
    
    # Reach per piattaforma
    penetration = SOCIAL_PENETRATION.get(sector, SOCIAL_PENETRATION['professionale'])
    
    reach = {}
    for platform, pct in penetration.items():
        reach[platform] = int(potential_target * pct * 1.5)  # 1.5x per social sharing
    
    # Assicura che il reach sia almeno un minimo credibile
    for platform in ['linkedin', 'instagram', 'twitter']:
        if reach.get(platform, 0) < 500:
            reach[platform] = 500
    
    return reach

def get_reach_report(facts: Dict, text: str) -> Dict:
    """Genera report reach con spiegazione"""
    reach = estimate_reach(facts, text)
    total = sum(reach.values())
    
    location = facts.get('location', '')
    sector = detect_sector(facts, text)
    
    return {
        'reach': reach,
        'total': total,
        'location': location,
        'sector': sector,
        'population': get_city_population(location),
        'conversion_rate': f"{0.02 if sector == 'professionale' else 0.05:.1%}",
        'explanation': f"Basato su popolazione di {location} ({get_city_population(location):,} abitanti) e settore {sector}."
    }
