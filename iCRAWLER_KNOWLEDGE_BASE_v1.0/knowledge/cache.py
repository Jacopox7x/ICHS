"""
iCRAWLER — Cache per evitare rigenerazioni duplicate
"""

import hashlib
import json
from pathlib import Path

class ICrawlerCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        Path(cache_dir).mkdir(exist_ok=True)
    
    def get_key(self, brief, template):
        content = f"{brief}|{template}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, key):
        path = Path(self.cache_dir) / f"{key}.json"
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return None
    
    def set(self, key, value):
        path = Path(self.cache_dir) / f"{key}.json"
        with open(path, "w") as f:
            json.dump(value, f)
