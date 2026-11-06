from typing import Dict
from .qwen_extractor import extract_with_qwen
from .regex_extractor import extract_with_regex
from .post_processor import post_process

def extract_facts(text: str) -> Dict[str, str]:
    """Factory: prova Qwen, fallback regex, post-processing SISTEMICO"""
    
    # 1. Prova Qwen
    result = extract_with_qwen(text)
    if result and isinstance(result, dict):
        # Assicura tutti i campi
        for field in ['event_name', 'date', 'location', 'target', 'objective', 'hashtag']:
            if field not in result:
                result[field] = 'DA DEFINIRE'
        
        # Arricchisci con campi fissi
        result.update({
            'organizer': 'DA DEFINIRE',
            'time': 'DA DEFINIRE',
            'venue': 'DA DEFINIRE',
            'speaker': 'DA DEFINIRE',
            'budget': 'DA DEFINIRE',
            'link': 'DA DEFINIRE'
        })
        
        # 2. POST-PROCESSING SISTEMICO (location SEMPRE da qui)
        return post_process(result, text)
    
    # 3. Fallback regex + post-processing
    regex_result = extract_with_regex(text)
    return post_process(regex_result, text)

def extract_facts_enhanced(text: str) -> Dict[str, str]:
    return extract_facts(text)
