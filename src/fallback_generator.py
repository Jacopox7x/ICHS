#!/usr/bin/env python3
"""
iCRAWLER V1.7 - Fallback Generator
"""

from typing import Dict
from fact_extractor import Fact

class FallbackGenerator:
    def generate(self, truth: Dict[str, Fact]) -> str:
        def get_value(key: str) -> str:
            fact = truth.get(key)
            return fact.value if fact and fact.value else "DA DEFINIRE"
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                iCRAWLER - SAFE MINIMUM PLAN                 ║
╚══════════════════════════════════════════════════════════════╝

⚠️  AI GENERATION TEMPORARILY UNAVAILABLE

📅 EVENTO: {get_value('event_name')}
📆 DATA: {get_value('date')}
📍 LOCATION: {get_value('location')}
👥 TARGET: {get_value('target')}
🎯 OBIETTIVO: {get_value('objective')}
⏰ ORARIO: {get_value('time')}

📋 STRATEGIA: [DA ELABORARE]
📢 CTA: [DA DEFINIRE]
🏷️ HASHTAG: #{get_value('event_name').replace(' ', '')} #Evento

NOTA: Piano generato automaticamente (AI non disponibile)
"""
