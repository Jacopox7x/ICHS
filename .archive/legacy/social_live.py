import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class SocialLive:
    def __init__(self):
        self.token = os.getenv("APIFY_TOKEN")
        self.base_url = "https://api.apify.com/v2"
        
        if not self.token:
            print("⚠️ APIFY_TOKEN non trovato nel file .env")
        else:
            print(f"✅ APIFY_TOKEN caricato: {self.token[:15]}...")

    def _call_actor(self, actor_id: str, input_data: dict) -> List[Dict]:
        if not self.token:
            return []

        url = f"{self.base_url}/actors/{actor_id}/run-sync-get-dataset-items"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            response = requests.post(url, json=input_data, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get('items', data)
        except Exception as e:
            print(f"⚠️ Errore Apify ({actor_id}): {e}")
            return []

    def get_instagram_posts(self, hashtag: str, limit: int = 10) -> List[Dict]:
        """Recupera post da Instagram per un hashtag"""
        input_data = {
            "hashtag": hashtag,
            "resultsLimit": limit,
        }
        # Usa l'actor alternativo funzionante
        return self._call_actor("dtrung/instagram-hashtag-scraper", input_data)

    def get_instagram_hashtags(self, topic: str, limit: int = 7) -> List[str]:
        """Recupera hashtag popolari da Instagram"""
        posts = self.get_instagram_posts(topic, limit=15)
        hashtags = []
        for post in posts:
            caption = post.get("caption") or post.get("text") or ""
            if caption:
                for word in caption.split():
                    if word.startswith('#') and len(word) > 1:
                        hashtags.append(word.lower())
        return list(dict.fromkeys(hashtags))[:limit]
