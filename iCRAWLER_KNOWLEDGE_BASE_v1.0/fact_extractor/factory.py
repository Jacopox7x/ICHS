from typing import Dict
from .qwen_extractor import extract_with_qwen
from .regex_extractor import extract_with_regex
from .post_processor import post_process

def extract_facts(text: str) -> Dict[str, str]:
    try:
        result = extract_with_qwen(text)
        if result and isinstance(result, dict):
            for field in ['event_name', 'date', 'location', 'target', 'objective', 'hashtag']:
                if field not in result:
                    result[field] = 'DA DEFINIRE'
            result.update({
                'organizer': 'DA DEFINIRE',
                'time': 'DA DEFINIRE',
                'venue': 'DA DEFINIRE',
                'speaker': 'DA DEFINIRE',
                'budget': 'DA DEFINIRE',
                'link': 'DA DEFINIRE'
            })
            return post_process(result, text)
    except Exception as e:
        print(f"⚠️ Qwen extraction fallita: {e}, uso regex")
    
    regex_result = extract_with_regex(text)
    return post_process(regex_result, text)

def extract_facts_enhanced(text: str) -> Dict[str, str]:
    return extract_facts(text)
