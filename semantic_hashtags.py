import ollama
import numpy as np
import json

class SemanticHashtagEngine:
    def __init__(self, db_path="hashtags_db.json"):
        with open(db_path, "r") as f:
            self.db = json.load(f)
        self._cache = {}

    def _get_embedding(self, text):
        if text in self._cache:
            return self._cache[text]
        response = ollama.embeddings(model="nomic-embed-text", prompt=text)
        vec = np.array(response["embedding"])
        self._cache[text] = vec
        return vec

    def _cosine_similarity(self, v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def get_top_hashtags(self, brief: str, top_k: int = 5, min_similarity: float = 0.60):
        brief_vec = self._get_embedding(brief)
        results = []
        
        for item in self.db:
            tag_vec = self._get_embedding(item["desc"])
            sim = float(self._cosine_similarity(brief_vec, tag_vec))
            results.append((item["tag"], sim))
            
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Filtriamo per soglia e limitiamo a top_k
        filtered = [(tag, score) for tag, score in results if score >= min_similarity]
        
        # Se non supera la soglia, meglio non dare hashtag piuttosto che dare quelli sbagliati
        return filtered[:top_k]

if __name__ == "__main__":
    engine = SemanticHashtagEngine()
    
    brief_bici = "Lavori in Corso: un progetto a Cremona per l'inclusione attiva e il lavoro delle persone con disabilità, con riparazione di bici."
    brief_cena = "Cena di gala con degustazione di vini pregiati e piatti gourmet dello chef."
    
    print(f"🚲 Brief BICI:")
    for tag, score in engine.get_top_hashtags(brief_bici):
        print(f"  {tag} ({score:.2%})")
        
    print(f"\n🍷 Brief CENA:")
    for tag, score in engine.get_top_hashtags(brief_cena):
        print(f"  {tag} ({score:.2%})")
