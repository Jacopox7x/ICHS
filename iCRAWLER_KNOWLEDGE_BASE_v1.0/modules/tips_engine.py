"""
Consigli operativi per iCrawler
"""

from typing import Dict, List

def generate_operational_advice(facts: Dict) -> List[str]:
    """Genera consigli operativi per il piano sociale"""
    
    tips = []
    
    # Consigli generali
    tips.extend([
        "📊 Monitora le performance ogni 24 ore",
        "🔄 Adatta il piano in base ai dati reali",
        "📅 Crea un calendario editoriale settimanale",
        "🤝 Collabora con influencer e partner",
        "📈 Usa strumenti di analytics (es. Buffer, Hootsuite)",
        "🎯 Definisci KPI chiari (reach, engagement, conversioni)",
        "📝 Mantieni un tono coerente su tutte le piattaforme",
        "⏰ Pubblica nei momenti di massimo engagement del target"
    ])
    
    # Consigli specifici per tipo evento
    text = str(facts).lower()
    if 'manager' in text or 'ceo' in text or 'b2b' in text:
        tips.append("🎯 LinkedIn: usa formati lunghi e case study")
        tips.append("📊 Condividi dati e trend di settore")
    elif 'festa' in text or 'party' in text or 'divertimento' in text:
        tips.append("🎉 Instagram: usa storie e reels leggeri")
        tips.append("❤️ Coinvolgi gli invitati con sondaggi e domande")
    
    return tips

def get_tips_for_platform(platform: str, facts: Dict) -> List[str]:
    """Consigli specifici per piattaforma"""
    all_tips = generate_operational_advice(facts)
    # Per ora restituiamo solo i generali
    return all_tips[:3]
