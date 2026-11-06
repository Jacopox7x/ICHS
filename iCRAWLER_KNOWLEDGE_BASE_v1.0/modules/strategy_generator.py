"""
Generatore di strategia basato su facts
"""

import re
from typing import Dict

def infer_target(facts: Dict[str, str]) -> str:
    event = facts.get('event_name', '')
    if 'fiera' in event.lower() or 'salone' in event.lower():
        return 'professionisti del settore, aziende, artigiani'
    elif 'convegno' in event.lower() or 'conferenza' in event.lower():
        return 'esperti, ricercatori, studenti universitari'
    elif 'festival' in event.lower() or 'festa' in event.lower():
        return 'famiglie, giovani, appassionati'
    elif 'cena' in event.lower() or 'beneficenza' in event.lower():
        return 'imprenditori, filantropi, professionisti'
    elif 'corsa' in event.lower() or 'maratona' in event.lower():
        return 'runner amatoriali e professionisti'
    else:
        return 'pubblico interessato all\'evento'

def infer_objective(facts: Dict[str, str]) -> str:
    event = facts.get('event_name', '')
    if 'fiera' in event.lower() or 'salone' in event.lower():
        return 'attrarre visitatori, promuovere il settore, creare opportunità di business'
    elif 'convegno' in event.lower() or 'conferenza' in event.lower():
        return 'condividere conoscenze, fare networking, stimolare il dibattito'
    elif 'festival' in event.lower() or 'festa' in event.lower():
        return 'creare un\'esperienza di divertimento e condivisione'
    elif 'cena' in event.lower() or 'beneficenza' in event.lower():
        return 'raccogliere fondi, sensibilizzare, creare relazioni'
    else:
        return 'creare valore e coinvolgimento per i partecipanti'

def detect_tone(facts: Dict[str, str]) -> str:
    text = str(facts).lower()
    if any(kw in text for kw in ['festa', 'party', 'divertimento']):
        return 'Caldo, informale, coinvolgente'
    else:
        return 'Professionale, autorevole, strategico'

def generate_strategy(facts: Dict[str, str]) -> Dict[str, str]:
    target = facts.get('target')
    if target == 'DA DEFINIRE' or not target:
        target = infer_target(facts)
    objective = facts.get('objective')
    if objective == 'DA DEFINIRE' or not objective:
        objective = infer_objective(facts)
    tone = detect_tone(facts)
    return {
        'target': target,
        'objective': objective,
        'tone': tone
    }
