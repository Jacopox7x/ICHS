import ollama
import numpy as np
from gliner_client import extract_entities, entities_to_dict

class SummarizationAgent:
    def _get_embedding(self, text):
        response = ollama.embeddings(model="nomic-embed-text", prompt=text)
        return np.array(response["embedding"])

    def _cosine_similarity(self, v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def summarize(self, long_text: str, max_chunks: int = 5):
        print("📄 Suddivisione del testo in blocchi...")
        paragraphs = [p.strip() for p in long_text.split('\n') if len(p.strip()) > 50]
        if not paragraphs:
            paragraphs = [long_text[i:i+300] for i in range(0, len(long_text), 300)]

        if len(paragraphs) <= max_chunks:
            selected_chunks = paragraphs
        else:
            print(f"🧠 Calcolo embeddings per {len(paragraphs)} blocchi (Nomic)...")
            embeddings = [self._get_embedding(p) for p in paragraphs]
            centroid = np.mean(embeddings, axis=0)
            scores = [self._cosine_similarity(emb, centroid) for emb in embeddings]
            top_indices = np.argsort(scores)[-max_chunks:]
            top_indices.sort()
            selected_chunks = [paragraphs[i] for i in top_indices]

        print("🔍 Estrazione entità (GLiNER)...")
        raw_entities = extract_entities(long_text)
        entities = entities_to_dict(raw_entities) if raw_entities else {}

        print("✍️ Generazione del riassunto (Qwen)...")
        prompt = f"""Sei un analista esperto. Scrivi un riassunto fluido, chiaro e strutturato (max 200 parole) basandoti ESCLUSIVAMENTE sui fatti e sui passaggi forniti.

FATTI ESTRATTI (SRE Logic):
{entities}

PASSAGGI CHIAVE SELEZIONATI:
{chr(10).join(selected_chunks)}

REGOLE:
1. Non inventare nulla.
2. Usa un tono professionale e diretto.
3. Rispondi solo con il testo del riassunto, senza introduzioni."""

        response = ollama.chat(
            model="qwen2.5:3b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2, "num_ctx": 8192},
            keep_alive=0
        )
        
        return response["message"]["content"]
