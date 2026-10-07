"""
Creative Lab Fallback — 5 idee strutturate (senza Qwen)
"""

import re
from typing import List, Dict

def generate_creative_ideas(facts: Dict[str, str]) -> List[Dict]:
    event = facts.get('event_name', 'Evento')
    location = facts.get('location', '')
    target = facts.get('target', '')
    
    text = str(facts).lower()
    is_tech = any(kw in text for kw in ['tech', 'digitale', 'conferenza', 'summit', 'ai', 'software'])
    is_food = any(kw in text for kw in ['birra', 'vino', 'cibo', 'ristorante', 'gastronomia'])
    is_sport = any(kw in text for kw in ['corsa', 'maratona', 'sport', 'running'])
    is_leisure = any(kw in text for kw in ['festa', 'party', 'divertimento', 'amici'])
    
    ideas = []
    
    # Idea 1: Countdown
    ideas.append({
        'title': 'Il Countdown Interattivo',
        'concept': f'Post che mostrano il tempo rimanente all\'evento "{event}" con grafica minimalista e aggiornamenti giornalieri. Ogni giorno un\'immagine diversa che anticipa un tema o un ospite.',
        'why': 'Crea urgenza senza aggressività e mantiene alta l\'attenzione giorno dopo giorno.',
        'risk': 'Può diventare ripetitivo se non si variano abbastanza le immagini o i messaggi.'
    })
    
    # Idea 2: Q&A
    ideas.append({
        'title': 'Q&A Live Pre-Event',
        'concept': f'Post con domande aperte alla community su {event}. Le domande più votate verranno discusse durante l\'evento.',
        'why': 'Favorisce partecipazione attiva e crea un senso di comunità prima ancora dell\'evento.',
        'risk': 'Bassa risposta senza incentivi o senza una chiara visibilità del premio.'
    })
    
    # Idea 3: Dietro le quinte
    ideas.append({
        'title': 'Dietro le Quinte',
        'concept': f'Mostra la preparazione di {event}: allestimento, prove, interviste ai relatori, preparazione dei materiali.',
        'why': 'Umanizza l\'evento e crea aspettativa. Il pubblico ama vedere cosa succede "dietro".',
        'risk': 'Può risultare banale se non c\'è un elemento di sorpresa o se le riprese sono di bassa qualità.'
    })
    
    # Idea 4: Specifica per settore
    if is_tech:
        ideas.append({
            'title': 'La Sfida della Settimana',
            'concept': f'Lancia una sfida tecnica settimanale legata al tema di {event}. I partecipanti possono inviare soluzioni o idee.',
            'why': 'Coinvolge attivamente la community tecnica e dimostra il valore pratico di ciò che verrà discusso.',
            'risk': 'Può escludere i non addetti ai lavori se la sfida è troppo tecnica.'
        })
    elif is_food:
        ideas.append({
            'title': 'La Ricetta del Giorno',
            'concept': f'Pubblica una ricetta o un abbinamento legato al tema di {event}. Ogni giorno un piatto diverso.',
            'why': 'Il cibo unisce e crea connessioni emotive. Le ricette sono contenuti evergreen e facilmente condivisibili.',
            'risk': 'Se l\'evento non ha un tema food, può sembrare forzato.'
        })
    elif is_sport:
        ideas.append({
            'title': 'La Sfida Sportiva',
            'concept': f'Lancia una sfida sportiva quotidiana (es. "corri 5 km e condividi il tuo tempo").',
            'why': 'Coinvolge fisicamente la community e crea un senso di squadra.',
            'risk': 'Può escludere chi non pratica sport.'
        })
    elif is_leisure:
        ideas.append({
            'title': 'La Playlist della Festa',
            'concept': f'Crea una playlist collaborativa per {event}. Ogni giorno viene aggiunta una canzone scelta dalla community.',
            'why': 'La musica crea atmosfera e coinvolgimento.',
            'risk': 'Può diventare caotica se non ci sono regole nella selezione delle canzoni.'
        })
    else:
        ideas.append({
            'title': 'Il Muro della Community',
            'concept': f'Crea un muro virtuale dove i partecipanti possono lasciare messaggi, disegni o video di supporto per {event}.',
            'why': 'Costruisce un senso di comunità e di appartenenza.',
            'risk': 'Richiede moderazione per evitare contenuti inappropriati.'
        })
    
    # Idea 5: Sempre
    ideas.append({
        'title': 'L\'Influencer del Giorno',
        'concept': f'Collabora con un influencer o un esperto del settore per un takeover dei social di {event} per un giorno.',
        'why': 'Amplifica la portata dell\'evento e porta un pubblico nuovo.',
        'risk': 'Se l\'influencer non è in linea con il target, può risultare fuori luogo.'
    })
    
    return ideas[:5]

def build_creative_lab(facts: Dict[str, str]) -> str:
    ideas = generate_creative_ideas(facts)
    lines = ["💡 CREATIVE LAB", ""]
    for i, idea in enumerate(ideas, 1):
        lines.append(f"IDEA {i}: {idea['title']}")
        lines.append(f"Concept: {idea['concept']}")
        lines.append(f"Perche funziona: {idea['why']}")
        lines.append(f"Rischio: {idea['risk']}")
        lines.append("")
    return "\n".join(lines)
