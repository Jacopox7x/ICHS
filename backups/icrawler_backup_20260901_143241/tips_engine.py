"""
Generatore di consigli operativi per iCrawler
"""

def generate_tips(platform: str, event_type: str, target: str, facts: dict) -> list:
    """
    Genera consigli operativi specifici per piattaforma
    
    Args:
        platform: linkedin, instagram, twitter
        event_type: professionale, leisure
        target: target dell'evento
        facts: dizionario facts
    """
    
    tips = []
    
    if platform == "linkedin":
        if event_type == "professionale":
            tips = [
                "🎯 Usa il formato '📝 [Titolo] | [Sottotitolo]' per i post",
                "📊 Condividi dati e statistiche rilevanti per il settore",
                "🔗 Includi link a case study o whitepaper",
                "💬 Fai domande aperte per stimolare il dibattito",
                "🏷️ Usa 3-5 hashtag mirati (non di più)",
                "📅 Pubblica martedì, mercoledì o giovedì alle 8:30-10:00",
                "🖼️ Allega sempre un'immagine di qualità (1200x627)",
                "👥 Tagga le aziende e i partner coinvolti"
            ]
        else:
            tips = [
                "🎉 Usa un tono più leggero e informale",
                "📸 Condividi foto delle persone (non solo prodotti)",
                "❤️ Usa emoji per dare calore al messaggio",
                "⏰ Pubblica nel weekend o dopo le 18:00",
                "🏷️ Usa hashtag più generali e popolari"
            ]
            
    elif platform == "instagram":
        if event_type == "professionale":
            tips = [
                "📷 Carousel: 5-10 slide con contenuto educativo",
                "🎬 Reels: 15-30 secondi, formato verticale (1080x1920)",
                "📝 Testo: breve (max 150 caratteri) + call to action",
                "🏷️ Usa 5-7 hashtag mirati (settore + evento)",
                "📍 Geotagga sempre la location",
                "⏰ Pubblica tra le 12:00 e le 14:00",
                "💬 Rispondi ai commenti entro 1 ora",
                "🔗 Link in bio: aggiorna con il link all'evento"
            ]
        else:
            tips = [
                "🎉 Stories: countdown giornaliero + sondaggi",
                "🎬 Reels: dietro le quinte, momenti divertenti",
                "📸 Photo dump: 5-10 foto senza troppa cura",
                "🏷️ Usa 10-15 hashtag popolari",
                "⏰ Pubblica tra le 19:00 e le 22:00",
                "❤️ Fai repost degli utenti che taggano l'evento"
            ]
            
    elif platform == "twitter":
        tips = [
            "🧵 Thread: 3-5 tweet collegati tra loro",
            "⏰ Pubblica ogni 30-60 minuti durante l'evento",
            "🏷️ Usa 2-3 hashtag (massimo)",
            "📸 Allega sempre un'immagine o video",
            "💬 Ritwitta i partecipanti più attivi",
            "📅 Pubblica tra le 9:00 e le 11:00",
            "🔗 Link agli articoli con preview automatica"
        ]
    
    return tips

def generate_operational_advice(facts: dict) -> dict:
    """Genera consigli operativi completi per tutte le piattaforme"""
    
    event_type = "leisure" if any(kw in str(facts).lower() for kw in ["festa", "party", "divertimento", "amici"]) else "professionale"
    target = facts.get('target', '').lower()
    
    advice = {
        "linkedin": generate_tips("linkedin", event_type, target, facts),
        "instagram": generate_tips("instagram", event_type, target, facts),
        "twitter": generate_tips("twitter", event_type, target, facts)
    }
    
    # Aggiungi consigli generali
    advice["general"] = [
        "📊 Monitora le performance ogni 24 ore",
        "🔄 Adatta il piano in base ai dati reali",
        "📅 Crea un calendario editoriale settimanale",
        "🤝 Collabora con influencer e partner",
        "📈 Usa strumenti di analytics (es. Buffer, Hootsuite)",
        "🎯 Definisci KPI chiari (reach, engagement, conversioni)"
    ]
    
    return advice
