import re
from typing import List, Dict

class HashtagGenerator:
    def __init__(self):
        self.pools = {
            'professionale': ['#Business', '#Leadership', '#Strategy', '#Growth', '#Success', '#Innovation', '#Digital', '#Future'],
            'leisure': ['#Party', '#Divertimento', '#Amici', '#Weekend', '#Vibes', '#Fun', '#Enjoy', '#GoodTimes'],
            'generale': ['#Evento', '#Innovazione', '#Networking', '#Community', '#Experience', '#Moments', '#Together']
        }
    
    def extract_from_brief(self, text: str) -> List[str]:
        return re.findall(r'#\w+', text)
    
    def generate_fallback(self, facts: Dict[str, str]) -> List[str]:
        hashtags = []
        
        # 1. Dal nome evento
        event = facts.get('event_name', '')
        if event and event != 'DA DEFINIRE':
            words = re.findall(r'[A-Za-z]+', event)
            if words:
                hashtags.append('#' + ''.join(words[:3]))
                if len(words) >= 2:
                    hashtags.append('#' + ''.join(words[:2]))
        
        # 2. Dalla location
        location = facts.get('location', '')
        if location and location != 'DA DEFINIRE':
            hashtags.append(f'#{location}')
            hashtags.append(f'#{location}Event')
        
        # 3. Dal target
        target = facts.get('target', '')
        if target and target != 'DA DEFINIRE':
            for word in target.split():
                if len(word) > 3:
                    hashtags.append('#' + word.capitalize())
        
        # 4. Dalla data (se presente)
        date = facts.get('date', '')
        if date and date != 'DA DEFINIRE':
            year_match = re.search(r'(\d{4})', date)
            if year_match:
                hashtags.append(f'#{year_match.group(1)}')
        
        # 5. Categoria
        text = str(facts).lower()
        if any(kw in text for kw in ['festa', 'party', 'divertimento']):
            hashtags.extend(self.pools['leisure'])
        else:
            hashtags.extend(self.pools['professionale'])
        
        # 6. Generali
        hashtags.extend(self.pools['generale'])
        
        # Rimuovi duplicati
        seen = set()
        unique = []
        for tag in hashtags:
            if tag not in seen:
                seen.add(tag)
                unique.append(tag)
        
        return unique[:15]
    
    def generate(self, text: str, facts: Dict[str, str]) -> List[str]:
        # 1. Hashtag dal brief
        hashtags = self.extract_from_brief(text)
        if hashtags:
            return hashtags[:15]
        # 2. Fallback (Qwen disabilitato)
        return self.generate_fallback(facts)[:15]

def generate_hashtags(text: str, facts: Dict[str, str]) -> List[str]:
    return HashtagGenerator().generate(text, facts)
