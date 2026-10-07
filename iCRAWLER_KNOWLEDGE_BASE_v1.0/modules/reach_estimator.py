from typing import Dict

CITY_DATA = {
    'Roma': {'population': 2_873_000},
    'Milano': {'population': 1_396_000},
    'Torino': {'population': 848_000},
    'Bologna': {'population': 392_000},
    'Firenze': {'population': 367_000},
    'Rovigo': {'population': 50_000},
}

SOCIAL_PENETRATION = {
    'professionale': {'linkedin': 0.35, 'instagram': 0.20, 'twitter': 0.15},
    'leisure': {'linkedin': 0.10, 'instagram': 0.55, 'twitter': 0.25},
    'tecnico': {'linkedin': 0.45, 'instagram': 0.15, 'twitter': 0.30}
}

SECTOR_KEYWORDS = {
    'tecnico': ['tecnico', 'industria', 'ferro', 'acciaio', 'macchinari', 'produzione'],
    'professionale': ['manager', 'ceo', 'commercialista', 'consulente', 'avvocato'],
    'leisure': ['festa', 'divertimento', 'amici', 'party', 'concerto']
}

def detect_sector(facts: Dict, text: str) -> str:
    text_lower = (text + ' ' + str(facts)).lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return sector
    if any(kw in text_lower for kw in ['festa', 'divertimento', 'amici']):
        return 'leisure'
    return 'professionale'

def get_city_population(location: str) -> int:
    for city, data in CITY_DATA.items():
        if city.lower() in location.lower():
            return data['population']
    return 500_000

def get_reach_report(facts: Dict, text: str) -> Dict:
    # Usa il fattore di conversione dinamico da systemic_rules
    from modules.systemic_rules import apply_systemic_rules
    rules = apply_systemic_rules(facts)
    conversion_factor = rules.get('reach_factor', 0.02)
    
    location = facts.get('location', '')
    sector = detect_sector(facts, text)
    population = get_city_population(location)
    
    potential_target = int(population * conversion_factor)
    penetration = SOCIAL_PENETRATION.get(sector, SOCIAL_PENETRATION['professionale'])
    
    reach = {}
    for platform, pct in penetration.items():
        reach[platform] = int(potential_target * pct * 1.5)
        if reach[platform] < 500:
            reach[platform] = 500
    
    total = sum(reach.values())
    
    return {
        'reach': reach,
        'total': total,
        'location': location,
        'sector': sector,
        'population': population,
        'conversion_rate': f"{conversion_factor:.1%}",
        'explanation': f"Basato su popolazione di {location} ({population:,} abitanti), settore {sector}, conversione {conversion_factor:.1%}"
    }
