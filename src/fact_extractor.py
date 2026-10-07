#!/usr/bin/env python3
"""
iCRAWLER V1.7 - Fact Extractor (migliorato)
"""

import re
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

class FactStatus(Enum):
    VALIDATED = "VALIDATED"
    LIKELY = "LIKELY"
    AMBIGUOUS = "AMBIGUOUS"
    MISSING = "MISSING"

@dataclass
class Fact:
    value: Optional[str]
    raw: Optional[str]
    confidence: float
    status: FactStatus
    source: str

class FactExtractor:
    def __init__(self):
        self.month_map = {
            'gennaio': '01', 'febbraio': '02', 'marzo': '03',
            'aprile': '04', 'maggio': '05', 'giugno': '06',
            'luglio': '07', 'agosto': '08', 'settembre': '09',
            'ottobre': '10', 'novembre': '11', 'dicembre': '12',
        }
        
        self.patterns = {
            'date': r'(\d{1,2})\s*(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s*(\d{4})?',
            'location': r'(?:[Aa] |[Ii]n |[Pp]resso |,\s*)([A-Z][a-zàèéìòóù]+(?:\s+[A-Z][a-zàèéìòóù]+)*)(?=[,.\n]|$)',
            'target': r'(?:target|pubblico|audience)\s*[:;]\s*([^.\n]+)',
            'objective': r'(?:obiettivo|scopo|finalità)\s*[:;]\s*([^.\n]+)',
            'organizer': r'(?:organizzato da|organizzatore|promosso da)\s*[:;]\s*([^.\n]+)',
            'time': r'(?:orario|alle|ore)\s*[:;]?\s*(\d{1,2}\s*[:.]?\s*\d{0,2})',
        }
    
    def extract(self, text: str) -> Dict[str, Fact]:
        facts = {}
        facts['date'] = self._extract_date(text)
        facts['location'] = self._extract_location(text)
        facts['target'] = self._extract_target(text)
        facts['objective'] = self._extract_objective(text)
        facts['organizer'] = self._extract_organizer(text)
        facts['time'] = self._extract_time(text)
        facts['event_name'] = self._extract_event_name(text)
        return facts
    
    def _extract_date(self, text: str) -> Fact:
        match = re.search(self.patterns['date'], text, re.IGNORECASE)
        if match:
            day, month_name, year = match.groups()
            month = self.month_map.get(month_name.lower())
            if month:
                if year:
                    normalized = f"{year}-{month}-{day.zfill(2)}"
                    return Fact(normalized, match.group(0), 1.0, FactStatus.VALIDATED, "date_pattern")
                else:
                    normalized = f"2026-{month}-{day.zfill(2)}"
                    return Fact(normalized, match.group(0), 0.7, FactStatus.LIKELY, "date_pattern")
        return Fact(None, None, 0.0, FactStatus.MISSING, "none")
    
    def _extract_location(self, text: str) -> Fact:
        match = re.search(self.patterns['location'], text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            if location.lower() not in ['target', 'obiettivo', 'organizzato', 'evento']:
                return Fact(location, match.group(0), 0.9, FactStatus.LIKELY, "location_pattern")
        
        cities = ['Milano', 'Roma', 'Torino', 'Firenze', 'Bologna', 'Napoli', 'Venezia', 'Genova', 'Cremona', 'Bergamo']
        for city in cities:
            if city in text:
                return Fact(city, city, 0.7, FactStatus.LIKELY, "city_fallback")
        
        return Fact(None, None, 0.0, FactStatus.MISSING, "none")
    
    def _extract_target(self, text: str) -> Fact:
        match = re.search(self.patterns['target'], text, re.IGNORECASE)
        if match:
            return Fact(match.group(1).strip(), match.group(0), 0.9, FactStatus.LIKELY, "target_pattern")
        return Fact(None, None, 0.0, FactStatus.MISSING, "none")
    
    def _extract_objective(self, text: str) -> Fact:
        """Estrae l'obiettivo con supporto per numeri e unità monetarie"""
        
        # Pattern per obiettivi con numeri e unità
        objective_patterns = [
            # Cattura "50.000 euro", "50,000 euro", "50 mila", "50 milioni"
            r'(?:raccogliere|raggiungere|ottenere)\s+([\d.,]+\s*(?:euro|€|mila|milioni|migliaia))',
            # Cattura "50.000" se seguito da "euro" o "€" nel contesto
            r'(?:raccogliere|raggiungere|ottenere)\s+([\d.,]+)\s*(?:[Ee]uro|[Ee]uro\s*[Mm]ila|[Mm]ila|[Mm]ilioni)',
            # Cattura "50.000" con contesto di euro
            r'([\d.,]+\s*(?:euro|€|mila|milioni))\s*(?:di\s*)?(?:fondi|euro|€)',
            # Cattura "50.000 euro" anche senza verbo
            r'([\d.,]+\s*(?:[Ee]uro|[Mm]ila|[Mm]ilioni))',
            # Pattern originale come fallback
            r'(?:obiettivo|scopo|finalità)\s*[:;]\s*([^.\n]+)',
            r'obiettivo\s*[:;]\s*([^.\n]+)',
        ]
        
        for pattern in objective_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                
                # Se il valore è solo un numero, aggiungi unità dal contesto
                if re.match(r'^[\d.,]+$', value):
                    context = text[max(0, match.start()-80):match.end()+80]
                    if 'euro' in context or '€' in context:
                        value += " euro"
                    elif 'mila' in context:
                        value += " mila"
                    elif 'milioni' in context:
                        value += " milioni"
                    elif 'migliaia' in context:
                        value += " migliaia"
                
                return Fact(value, match.group(0), 0.85, FactStatus.LIKELY, "objective_pattern")
        
        return Fact(None, None, 0.0, FactStatus.MISSING, "none")
    
    def _extract_organizer(self, text: str) -> Fact:
        match = re.search(self.patterns['organizer'], text, re.IGNORECASE)
        if match:
            return Fact(match.group(1).strip(), match.group(0), 0.9, FactStatus.LIKELY, "organizer_pattern")
        return Fact(None, None, 0.0, FactStatus.MISSING, "none")
    
    def _extract_time(self, text: str) -> Fact:
        match = re.search(self.patterns['time'], text, re.IGNORECASE)
        if match:
            time_str = match.group(1).strip()
            if ':' not in time_str:
                time_str = f"{time_str.zfill(2)}:00"
            return Fact(time_str, match.group(0), 0.9, FactStatus.LIKELY, "time_pattern")
        return Fact(None, None, 0.0, FactStatus.MISSING, "none")
    
    def _extract_event_name(self, text: str) -> Fact:
        lines = text.strip().split('\n')
        
        # 1. Cerca parole chiave all'inizio
        event_keywords = ['workshop', 'evento', 'conferenza', 'incontro', 'seminario', 'corso', 'laboratorio', 'festa', 'sagra', 'serata']
        
        for line in lines[:5]:
            line_clean = line.strip()
            if not line_clean:
                continue
            # Esclude righe che iniziano con "Data:" o "Luogo:"
            if re.match(r'^(Data|Luogo|Target|Obiettivo|Organizzato|Orario)\s*[:;]', line_clean, re.IGNORECASE):
                continue
            if len(line_clean) < 80:
                for keyword in event_keywords:
                    if keyword in line_clean.lower():
                        return Fact(line_clean, line_clean, 0.8, FactStatus.LIKELY, "keyword_detection")
                if line_clean == lines[0].strip() and len(line_clean) < 60:
                    return Fact(line_clean, line_clean, 0.7, FactStatus.LIKELY, "first_line_fallback")
        
        # 2. Fallback: cerca pattern specifici
        patterns = [
            r'(Serata di [^.,\n]+)',
            r'(Festa di [^.,\n]+)',
            r'(Sagra della [^.,\n]+)',
            r'(Workshop di [^.,\n]+)',
            r'(Evento di [^.,\n]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return Fact(match.group(1).strip(), match.group(0), 0.75, FactStatus.LIKELY, "pattern_detection")
        
        # 3. Fallback: prima riga
        if lines:
            first_line = lines[0].strip()
            if first_line and len(first_line) < 80:
                if not re.match(r'^(Data|Luogo|Target|Obiettivo|Organizzato|Orario)\s*[:;]', first_line, re.IGNORECASE):
                    return Fact(first_line, first_line, 0.6, FactStatus.LIKELY, "first_line")
        
        return Fact(None, None, 0.0, FactStatus.MISSING, "none")


def format_facts(facts: Dict[str, Fact]) -> str:
    icons = {
        FactStatus.VALIDATED: "✅",
        FactStatus.LIKELY: "🟡",
        FactStatus.AMBIGUOUS: "❓",
        FactStatus.MISSING: "❌"
    }
    
    output = ["=" * 60]
    output.append("SOURCE OF TRUTH")
    output.append("=" * 60)
    
    for key, fact in facts.items():
        icon = icons.get(fact.status, "⚪")
        output.append(f"\n{icon} {key.upper()}")
        output.append(f"  Value: {fact.value or 'NON TROVATO'}")
        output.append(f"  Confidence: {fact.confidence:.0%}")
        output.append(f"  Status: {fact.status.value}")
        output.append(f"  Source: {fact.source}")
    
    return "\n".join(output)
