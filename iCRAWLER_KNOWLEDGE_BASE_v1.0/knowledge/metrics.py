"""
iCRAWLER — Metriche e statistiche
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

class ICrawlerMetrics:
    def __init__(self, metrics_file="metrics/icrawler_metrics.json"):
        self.metrics_file = metrics_file
        Path("metrics").mkdir(exist_ok=True)
        self._init_metrics()
    
    def _init_metrics(self):
        if not Path(self.metrics_file).exists():
            self.data = {
                "total_generations": 0,
                "qwen_success": 0,
                "qwen_failures": 0,
                "fallback_used": 0,
                "avg_characters": 0,
                "avg_time": 0,
                "daily": {}
            }
            self._save()
        else:
            with open(self.metrics_file, "r") as f:
                self.data = json.load(f)
    
    def _save(self):
        with open(self.metrics_file, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def record_generation(self, chars, time_sec, qwen_used):
        self.data["total_generations"] += 1
        if qwen_used:
            self.data["qwen_success"] += 1
        else:
            self.data["fallback_used"] += 1
        
        # Media
        total = self.data["total_generations"]
        self.data["avg_characters"] = ((self.data["avg_characters"] * (total - 1)) + chars) / total
        self.data["avg_time"] = ((self.data["avg_time"] * (total - 1)) + time_sec) / total
        
        # Daily
        day = datetime.now().strftime("%Y-%m-%d")
        if day not in self.data["daily"]:
            self.data["daily"][day] = 0
        self.data["daily"][day] += 1
        
        self._save()
    
    def get_report(self):
        return f"""
📊 METRICHE iCRAWLER
═══════════════════════════════════
📁 Totale generazioni: {self.data['total_generations']}
✅ Qwen successi: {self.data['qwen_success']}
⚠️ Fallback usati: {self.data['fallback_used']}
📏 Media caratteri: {int(self.data['avg_characters'])}
⏱️ Media tempo: {self.data['avg_time']:.1f}s
📅 Oggi: {self.data['daily'].get(datetime.now().strftime('%Y-%m-%d'), 0)} piani
"""
