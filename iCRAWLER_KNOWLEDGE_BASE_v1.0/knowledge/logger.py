"""
iCRAWLER — Sistema di Logging
"""

import json
from datetime import datetime
from pathlib import Path

class ICrawlerLogger:
    def __init__(self, log_file="logs/icrawler.log"):
        self.log_file = log_file
        Path("logs").mkdir(exist_ok=True)
    
    def log(self, event_type, data):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def get_history(self, limit=50):
        if not Path(self.log_file).exists():
            return []
        with open(self.log_file, "r") as f:
            lines = f.readlines()
        return [json.loads(line) for line in lines[-limit:]]
