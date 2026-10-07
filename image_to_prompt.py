"""
Meccanismo di decodifica immagine → prompt per iCrawler.
"""

def image_to_prompt(image_description: str, style: str = "normal") -> dict:
    """
    Decodifica una descrizione di immagine in prompt per l'AI.
    
    Args:
        image_description: descrizione testuale dettagliata dell'immagine
        style: "normal" | "explicit" | "character" | "object" | "product" | "landscape"
    
    Returns:
        dict con 'english' e 'italian'
    """
    
    style_map = {
        "normal": "Photorealistic image of {desc}. Highly detailed, sharp, natural lighting.",
        "explicit": "Photorealistic image of {desc}. Highly explicit, raw, detailed quality.",
        "character": "App icon design / character design of {desc}. Clean modern style, vibrant neon colors, soft glow, high detail.",
        "object": "Product photography of {desc}. Studio lighting, clean background, high detail.",
        "product": "Product photography of {desc}. Studio lighting, clean background, high detail.",
        "landscape": "Landscape photography of {desc}. Vivid colors, dramatic lighting, wide angle."
    }
    
    template = style_map.get(style, style_map["normal"])
    english = template.format(desc=image_description)
    
    translations = {
        "Photorealistic image of": "Immagine realistica di",
        "App icon design / character design of": "Design di personaggio / icona di",
        "Product photography of": "Fotografia di prodotto di",
        "Landscape photography of": "Fotografia di paesaggio di",
        "Highly detailed, sharp, natural lighting.": "Altamente dettagliato, nitido, illuminazione naturale.",
        "Clean modern style, vibrant neon colors, soft glow, high detail.": "Stile moderno e pulito, colori neon vivaci, bagliore soft, alto dettaglio.",
        "Studio lighting, clean background, high detail.": "Illuminazione da studio, sfondo pulito, alto dettaglio.",
        "Vivid colors, dramatic lighting, wide angle.": "Colori vividi, illuminazione drammatica, grandangolo.",
        "Highly explicit, raw, detailed quality.": "Molto esplicito, grezzo, dettagliato."
    }
    
    italian = english
    for eng, ita in translations.items():
        italian = italian.replace(eng, ita)
    
    return {
        "english": english.strip(),
        "italian": italian.strip()
    }


if __name__ == "__main__":
    test = "Robot spider con occhi arancioni, corpo blu metallico, sei zampe meccaniche"
    result = image_to_prompt(test, style="character")
    print("🇬🇧 English:", result["english"])
    print("🇮🇹 Italiano:", result["italian"])
