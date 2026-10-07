#!/usr/bin/env python3
"""
iCRAWLER V1.7 - Deterministic Validator (flessibile)
"""

import re
from typing import Dict, List
from fact_extractor import Fact, FactStatus

class DeterministicValidator:
    def __init__(self, truth: Dict[str, Fact]):
        self.truth = truth
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def _date_in_plan(self, date_value: str, plan: str) -> bool:
        """Verifica se la data è presente nel piano in vari formati"""
        if not date_value:
            return True
        
        # Formati da cercare
        formats = [
            date_value,  # 2026-08-22
            date_value.replace('-', '/'),  # 2026/08/22
            date_value.replace('-', '.'),  # 2026.08.22
        ]
        
        # Prova a convertire in formato italiano
        try:
            parts = date_value.split('-')
            if len(parts) == 3:
                year, month, day = parts
                month_names = ['', 'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
                              'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']
                month_name = month_names[int(month)]
                # Formati italiani
                formats.append(f"{int(day)} {month_name} {year}")
                formats.append(f"{int(day)}/{int(month)}/{year}")
                formats.append(f"{int(day)}-{int(month)}-{year}")
                # Con zero iniziali
                formats.append(f"{day}/{month}/{year}")
        except:
            pass
        
        # Cerca nel piano
        for fmt in formats:
            if fmt in plan:
                return True
        
        # Cerca con regex più flessibile
        # Es: "22 agosto 2026" o "22/08/2026"
        try:
            parts = date_value.split('-')
            if len(parts) == 3:
                year, month, day = parts
                patterns = [
                    rf'{int(day)}\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+{year}',
                    rf'{day}/{month}/{year}',
                    rf'{day}-{month}-{year}',
                ]
                for pattern in patterns:
                    if re.search(pattern, plan, re.IGNORECASE):
                        return True
        except:
            pass
        
        return False
    
    def _location_in_plan(self, location: str, plan: str) -> bool:
        """Verifica se la location è presente nel piano"""
        if not location:
            return True
        
        if location in plan:
            return True
        
        # Cerca con case insensitive
        if re.search(re.escape(location), plan, re.IGNORECASE):
            return True
        
        return False
    
    def validate(self, plan: str) -> bool:
        self.errors = []
        self.warnings = []
        
        # 1. Verifica data (flessibile)
        date_fact = self.truth.get('date')
        if date_fact and date_fact.value:
            if not self._date_in_plan(date_fact.value, plan):
                self.errors.append(f"Data '{date_fact.value}' non trovata nel piano (cercato in vari formati)")
        
        # 2. Verifica location (flessibile)
        loc_fact = self.truth.get('location')
        if loc_fact and loc_fact.value:
            if not self._location_in_plan(loc_fact.value, plan):
                self.errors.append(f"Location '{loc_fact.value}' non trovata nel piano")
        
        # 3. Verifica sezioni (più flessibile)
        required_sections = [
            ('Strategia', r'(strategia|strategico|obiettivo|approccio)'),
            ('Piano', r'(piano|contenuti|post|social)'),
            ('Instagram', r'(instagram|ig|post)'),
            ('LinkedIn', r'(linkedin|professional)'),
            ('CTA', r'(cta|call to action|azione|prenota|iscriviti)'),
        ]
        
        for section_name, pattern in required_sections:
            if not re.search(pattern, plan, re.IGNORECASE):
                self.warnings.append(f"Sezione '{section_name}' potrebbe mancare (cercato: {pattern})")
        
        return len(self.errors) == 0
    
    def get_report(self) -> str:
        lines = []
        if self.errors:
            lines.append("❌ ERRORI:")
            for e in self.errors:
                lines.append(f"   - {e}")
        if self.warnings:
            lines.append("⚠️ WARNING:")
            for w in self.warnings:
                lines.append(f"   - {w}")
        if not self.errors and not self.warnings:
            lines.append("✅ Tutto ok!")
        return "\n".join(lines)
