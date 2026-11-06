import json
import re
import subprocess
from typing import List, Dict

class HashtagGenerator:
    def __init__(self):
        self.pools = {
            'professionale': ['#Business', '#Leadership', '#Strategy', '#Growth', '#Success'],
            'leisure': ['#Party', '#Divertimento', '#Amici', '#Weekend', '#Vibes'],
            'generale': ['#Evento', '#Innovazione', '#Networking', '#Community', '#Experience']
        }
    
    def extract_from_brief(self, text: str) -> List[str]:
        return re.findall(r'#\w+', text)
    
    def generate_with_qwen(self, facts: Dict[str, str]) -> List[str]:
        """Genera hashtag NATURALI con Qwen - NO giochi di parole forzati"""
        prompt = f"""Genera 15 hashtag per questo evento.

REGOLE IMPORTANTI:
1. Usa hashtag che le persone userebbero DAVVERO
2. NIENTE giochi di parole forzati o creativi a tutti i costi
3. Usa combinazioni di parole comuni e naturali
4. Mescola italiano e inglese in modo spontaneo
5. Ogni hashtag deve sembrare "ovvio" in retrospettiva

Esempi di hashtag NATURALI (non forzati):
#BirraArtigianale #BolognaEvent #CulturaDellaBirra #BirraBologna

Evento: {facts.get('event_name')}
Luogo: {facts.get('location')}
Target: {facts.get('target')}
Obiettivo: {facts.get('objective')}

Rispondi SOLO con JSON: {{"hashtags": ["#tag1", ...]}}"""
        
        try:
            payload = json.dumps({
                "model": "qwen3.5:4b",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.3}  # Più bassa per meno creatività forzata
            })
            
            result = subprocess.run(
                ["curl", "-s", "-X", "POST", "http://localhost:11434/api/chat",
                 "-H", "Content-Type: application/json", "-d", payload],
                capture_output=True, text=True, timeout=90
            )
            
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                content = data.get("message", {}).get("content", "")
                json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    return parsed.get("hashtags", [])
        except:
            pass
        return []
    
    def generate_fallback(self, facts: Dict[str, str]) -> List[str]:
        hashtags = []
        event = facts.get('event_name', '')
        if event and event != 'DA DEFINIRE':
            words = re.findall(r'[A-Za-z]+', event)
            if words:
                hashtags.append('#' + ''.join(words[:3]))
                if len(words) >= 2:
                    hashtags.append('#' + ''.join(words[:2]))
        location = facts.get('location', '')
        if location and location != 'DA DEFINIRE':
            hashtags.append(f'#{location}')
        target = facts.get('target', '')
        if target and target != 'DA DEFINIRE':
            for word in target.split():
                if len(word) > 3:
                    hashtags.append('#' + word.capitalize())
        objective = facts.get('objective', '')
        if objective and objective != 'DA DEFINIRE':
            words = re.findall(r'[A-Za-z]{4,}', objective)
            for word in words[:2]:
                if word.lower() not in ['promuovere', 'cultura', 'evento']:
                    hashtags.append('#' + word.capitalize())
        text = str(facts).lower()
        if any(kw in text for kw in ['festa', 'party', 'divertimento']):
            hashtags.extend(self.pools['leisure'])
        else:
            hashtags.extend(self.pools['professionale'])
        hashtags.extend(self.pools['generale'])
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
            print("🔍 Hashtag dal brief (priorità 1)")
            return hashtags[:15]
        
        # 2. Qwen (temperatura 0.3, no creatività forzata)
        print("🎨 Generazione hashtag naturali con Qwen... (fino a 90s)")
        hashtags = self.generate_with_qwen(facts)
        if hashtags:
            print(f"✅ {len(hashtags)} hashtag generati")
            return hashtags[:15]
        
        # 3. Fallback
        print("🔍 Hashtag fallback (priorità 3)")
        return self.generate_fallback(facts)[:15]

def generate_hashtags(text: str, facts: Dict[str, str]) -> List[str]:
    return HashtagGenerator().generate(text, facts)
