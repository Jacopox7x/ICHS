import re
from typing import List, Tuple
from dataclasses import dataclass

CATEGORIES = ["fashion", "food", "evento", "cultura", "sport", "tech", "sostenibilità", "business", "istituzionale"]

CATEGORY_KEYWORDS = {
    "fashion": ["moda", "fashion", "abbigliamento", "stile", "elegante"],
    "food": ["cibo", "food", "ristorante", "gastronomia", "vino"],
    "evento": ["evento", "festival", "convegno", "workshop", "conferenza"],
    "cultura": ["cultura", "arte", "mostra", "museo", "teatro"],
    "sport": ["sport", "maratona", "calcio", "palestra", "fitness"],
    "tech": ["tech", "tecnologia", "digitale", "startup", "innovazione"],
    "sostenibilità": ["sostenibilità", "green", "ecologia", "riciclo", "ambiente"],
    "business": ["business", "impresa", "azienda", "marketing", "vendita"],
    "istituzionale": ["istituzione", "pubblico", "comune", "regione", "ente"]
}

STOPWORDS = {'di', 'il', 'la', 'lo', 'le', 'i', 'gli', 'un', 'una', 'e', 'ma', 'per', 'con', 'su', 'in', 'a', 'da', 'del', 'della', 'delle', 'dei', 'degli', 'è', 'non', 'che', 'se', 'come', 'più', 'meno'}

@dataclass
class TopicResult:
    main_topic: str
    category: str
    keywords: List[str]
    confidence: float

class TopicExtractor:
    def extract_keywords(self, text: str, max_words: int = 5) -> List[str]:
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()
        word_freq = {}
        for word in words:
            if len(word) > 3 and word not in STOPWORDS:
                word_freq[word] = word_freq.get(word, 0) + 1
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_words]]
    
    def detect_category(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[category] = score
        if not scores or max(scores.values()) == 0:
            return "evento", 0.0
        best = max(scores, key=scores.get)
        return best, min(scores[best] / 5.0, 1.0)
    
    def extract(self, text: str) -> TopicResult:
        keywords = self.extract_keywords(text)
        category, confidence = self.detect_category(text)
        main_topic = keywords[0] if keywords else category
        return TopicResult(main_topic=main_topic, category=category, keywords=keywords[:5], confidence=confidence)
