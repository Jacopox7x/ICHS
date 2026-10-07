#!/bin/bash

echo "🔧 iCRAWLER - CORREZIONI AUTOMATICHE"
echo "========================================"
echo ""

# 1. BACKUP DEI FILE ORIGINALI
echo "📦 Backup dei file originali..."
mkdir -p backup_$(date +%Y%m%d_%H%M%S)
cp topics.py backup_$(date +%Y%m%d_%H%M%S)/
cp prompts/strategist.txt backup_$(date +%Y%m%d_%H%M%S)/
echo "✅ Backup completato"

# 2. CORREZIONE topics.py (parole chiave migliorate)
echo ""
echo "📝 Aggiornamento topics.py..."
cat > topics.py << 'TOPICS'
import re
from typing import List, Tuple
from dataclasses import dataclass

CATEGORIES = ["fashion", "food", "evento", "cultura", "sport", "tech", "sostenibilità", "business", "istituzionale"]

CATEGORY_KEYWORDS = {
    "fashion": ["moda", "fashion", "abbigliamento", "stile", "elegante", "outfit", "tessuto", "collezione", "vintage", "streetwear", "tendenza", "look", "accessorio", "sfilata"],
    "food": ["cibo", "food", "ristorante", "gastronomia", "vino", "enogastronomia", "cucina", "ricetta", "degustazione", "chef", "caffè", "coffee", "tazza", "fumante", "espresso", "cappuccino", "gusto", "sapori", "tradizione"],
    "evento": ["evento", "festival", "convegno", "workshop", "conferenza", "mostra", "fiera", "manifestazione", "incontro", "spettacolo", "concerto", "premi", "premio", "cerimonia"],
    "cultura": ["cultura", "arte", "mostra", "museo", "teatro", "cinema", "letteratura", "storia", "musica", "spettacolo", "artista", "esposizione", "collezione", "culturale"],
    "sport": ["sport", "bicicletta", "corsa", "pedalare", "bici", "cycling", "outdoor", "natura", "paesaggio", "attività", "fitness", "gara", "atleta", "competizione", "allenamento", "maratona"],
    "tech": ["tech", "tecnologia", "digitale", "startup", "programmazione", "innovazione", "software", "hardware", "cloud", "laptop", "computer", "app", "scalabilità", "intelligenza", "artificiale", "AI"],
    "sostenibilità": ["sostenibilità", "green", "ecologia", "riciclo", "ambiente", "eco", "natura", "energia", "rifiuti", "green", "ecologico", "risparmio", "energetico", "carbonio", "impronta", "ecosostenibile"],
    "business": ["business", "impresa", "azienda", "marketing", "vendita", "mercato", "investimento", "manager", "strategia", "profitto", "crescita", "sviluppo", "commerciale", "impreditorialità"],
    "istituzionale": ["istituzione", "pubblico", "comune", "regione", "governo", "ente", "cittadino", "servizio", "amministrazione", "pubblica", "normativa", "legge", "decreto"]
}

STOPWORDS = {'di', 'il', 'la', 'lo', 'le', 'i', 'gli', 'un', 'una', 'e', 'ma', 'per', 'con', 'su', 'in', 'a', 'da', 'del', 'della', 'delle', 'dei', 'degli', 'è', 'non', 'che', 'se', 'come', 'più', 'meno', 'questo', 'questa', 'questi', 'queste', 'quel', 'quella', 'quelli', 'quelle', 'dove', 'quando', 'cosa', 'chi', 'c\'è', 'ci', 'si', 'ne', 'sono', 'stato', 'stata', 'stati', 'state', 'essere', 'avere', 'fare', 'dire', 'volere'}

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
        confidence = min(scores[best] / 10.0, 1.0)
        return best, confidence
    
    def extract(self, text: str) -> TopicResult:
        keywords = self.extract_keywords(text)
        category, confidence = self.detect_category(text)
        main_topic = keywords[0] if keywords else category
        return TopicResult(main_topic=main_topic, category=category, keywords=keywords[:5], confidence=confidence)
TOPICS
echo "✅ topics.py aggiornato"

# 3. CORREZIONE strategist.txt (prompt più dettagliato)
echo ""
echo "📝 Aggiornamento prompt strategist.txt..."
cat > prompts/strategist.txt << 'PROMPT'
# iCRAWLER STRATEGIST - PROMPT OTTIMIZZATO v2.0

Sei iCrawler, un Social Media Strategist con 10 anni di esperienza.

## INPUT
- TOPIC: {main_topic}
- CATEGORIA: {category}
- PAROLE CHIAVE: {keywords}
- DESCRIZIONE: {description}
- DATA: {date}
- PIATTAFORME: {platforms}

## HASHTAG POOL FORNITO
{hashtags_pool}

## RICHIESTA

Genera un piano social professionale per {platforms} seguendo questa struttura:

### 📊 Analisi
- Target: definisci il pubblico ideale (età, interessi, stile di vita)
- Mood: descrivi l'atmosfera e le emozioni evocate
- Concetto chiave: una frase che riassume il messaggio
- Obiettivo comunicativo: (awareness, engagement, conversione)

### 📱 Contenuti per ogni piattaforma

Per OGNI piattaforma ({platforms}), crea contenuti UNICI e DIVERSIFICATI:

#### 📝 Caption
- Hook: 1 frase originale e accattivante (NON copiare da altre piattaforme)
- Corpo: 3-4 frasi che raccontano il valore
- CTA: 1 azione chiara ("Salva", "Commenta", "Link in bio", "Registrati")

#### 🖼️ Visual (descrivi in modo dettagliato)
- Soggetto: cosa viene mostrato
- Composizione: inquadratura, angolazione
- Stile: colori, luce, atmosfera
- Elementi grafici: testi, overlay, logo

#### 🏷️ Hashtag (scegli DAL POOL fornito)
- Scegli 5 hashtag per Instagram (miscela di settore + nicchia)
- Scegli 3 hashtag per LinkedIn (professionali)
- Scegli 2-3 hashtag per X (diretti e concisi)
- **NON inventare hashtag**, usa quelli del pool

#### 💬 Mention
- 3 placeholder realistici (@NomeBrand, @NomePartner, @NomeInfluencer)

### 📱 Stories (5 frame con progressione logica)
1. Attenzione: hook visivo forte
2. Informazione: cosa c'è da sapere
3. Valore: perché interessa al target
4. Prova sociale: "Lo fanno già in 200!"
5. CTA: "Link in bio per... / Iscriviti ora / Scopri di più"

### 📅 Calendario Teaser (3 giorni prima)
- Giorno -3: Mistero ("Sta arrivando qualcosa di speciale...")
- Giorno -2: Valore ("Ecco cosa scoprirai")
- Giorno -1: Urgenza ("Ultimi posti! Non aspettare")

### 📋 Riassunto Operativo
- Orari consigliati per ogni piattaforma (es. LinkedIn: 10:00, Instagram: 13:00 o 19:00, X: 9:00)
- 3 priorità operative per il lancio
- Tempistiche risposta commenti

## REGOLE D'ORO
- Italiano corretto, zero errori grammaticali
- Caption DIVERSE per ogni piattaforma (NON copiare)
- Hashtag: scegli DAL POOL fornito, **NON inventare**
- Emoji: massimo 2-3 per post
- Sii concreto, professionale, operativo
- Menziona sempre il topic principale nel corpo della caption
PROMPT
echo "✅ strategist.txt aggiornato"

# 4. CREA UN ALIAS PER AVVIARE ICRAWLER
echo ""
echo "🔗 Creazione alias per avvio rapido..."
grep -q "alias icrawler" ~/.zshrc || echo 'alias icrawler="cd ~/Documents/ICHS && source venv/bin/activate && python main.py"' >> ~/.zshrc
source ~/.zshrc 2>/dev/null
echo "✅ Alias aggiunto: ora puoi usare 'icrawler'"

# 5. RIEPILOGO FINALE
echo ""
echo "========================================"
echo "✅ TUTTE LE CORREZIONI APPLICATE!"
echo ""
echo "📌 PER TESTARE SUBITO:"
echo "   python main.py --desc \"bellezza in bicicletta\" --platforms \"Instagram,LinkedIn,X\""
echo ""
echo "   oppure (alias):"
echo "   icrawler --desc \"bellezza in bicicletta\" --platforms \"Instagram,LinkedIn,X\""
echo "========================================"
