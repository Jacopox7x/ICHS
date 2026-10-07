"""
WeKnoraClient — Client Python per retrieval da WeKnora
======================================================
Usa l'endpoint /api/v1/knowledge-search per recuperare chunk 
senza passare per l'LLM (che è lento).
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Dict, Optional

WEKNORA_BASE_URL = os.getenv("WEKNORA_BASE_URL", "http://localhost:8080")
WEKNORA_API_KEY = os.getenv("WEKNORA_API_KEY", "")


class WeKnoraClient:
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or WEKNORA_BASE_URL
        self.api_key = api_key or WEKNORA_API_KEY
        if not self.api_key:
            raise ValueError("WEKNORA_API_KEY non configurata")

    def _post(self, endpoint: str, payload: dict, timeout: int = 10) -> dict:
        """POST generico con gestione errori."""
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.read().decode('utf-8')[:200]}"}
        except urllib.error.URLError as e:
            return {"error": f"Connessione fallita: {e}"}

    def _get(self, endpoint: str, timeout: int = 10) -> dict:
        """GET generico."""
        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(
            url,
            headers={"X-API-Key": self.api_key},
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.read().decode('utf-8')[:200]}"}
        except urllib.error.URLError as e:
            return {"error": f"Connessione fallita: {e}"}

    # ─────────────────────────────────────────
    # API PUBBLICHE
    # ─────────────────────────────────────────
    def health(self) -> bool:
        """Verifica che WeKnora sia raggiungibile."""
        try:
            result = self._get("/health")
            return result.get("status") == "ok"
        except Exception:
            return False

    def list_knowledge_bases(self) -> List[Dict]:
        """Lista tutte le KB."""
        result = self._get("/api/v1/knowledge-bases")
        if "error" in result:
            return []
        return result.get("data", [])

    def find_kb_id(self, name_contains: str) -> Optional[str]:
        """Trova una KB per nome (case-insensitive)."""
        for kb in self.list_knowledge_bases():
            if name_contains.lower() in kb.get("name", "").lower():
                return kb["id"]
        return None

    def search(
        self,
        query: str,
        kb_ids: List[str],
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Retrieval puro: ritorna i chunk rilevanti, senza LLM.
        
        Args:
            query: testo di ricerca
            kb_ids: lista di ID delle KB da interrogare
            top_k: numero massimo di chunk
        
        Returns:
            Lista di chunk con content, score, knowledge_title, ecc.
        """
        payload = {
            "query": query,
            "knowledge_base_ids": kb_ids,
            "top_k": top_k,
        }
        result = self._post("/api/v1/knowledge-search", payload)
        if "error" in result:
            print(f"⚠️  Search error: {result['error']}")
            return []
        return result.get("data", [])

    def get_context(
        self,
        query: str,
        kb_ids: List[str],
        top_k: int = 5,
        max_chars: int = 3000,
    ) -> str:
        """
        Ritorna il contesto concatenato dai chunk, pronto per un prompt LLM.
        
        Args:
            query: domanda
            kb_ids: KB da interrogare
            top_k: numero di chunk
            max_chars: lunghezza massima del contesto concatenato
        
        Returns:
            Stringa con i chunk separati da "---"
        """
        chunks = self.search(query, kb_ids, top_k)
        if not chunks:
            return ""

        parts = []
        total = 0
        for c in chunks:
            content = c.get("content", "").strip()
            title = c.get("knowledge_title", "")
            if not content:
                continue
            block = f"[{title}]\n{content}"
            
            # Se supera il limite, tronca l'ultimo blocco
            remaining = max_chars - total
            if remaining <= 0:
                break
            if len(block) > remaining:
                block = block[:remaining] + "... [troncato]"
                parts.append(block)
                break
            
            parts.append(block)
            total += len(block)

        return "\n\n---\n\n".join(parts)


# ─────────────────────────────────────────
# TEST
# ─────────────────────────────────────────
if __name__ == "__main__":
    client = WeKnoraClient()

    print("═" * 60)
    print("TEST WeKnoraClient")
    print("═" * 60)

    # 1. Health
    print(f"\n1. Health: {'✅ OK' if client.health() else '❌ FAIL'}")

    # 2. Lista KB
    kbs = client.list_knowledge_bases()
    print(f"\n2. KB trovate: {len(kbs)}")
    for kb in kbs:
        print(f"   - {kb['name']} (ID: {kb['id'][:12]}...)")

    if not kbs:
        print("⚠️  Nessuna KB, esci.")
        exit(0)

    kb_id = kbs[0]["id"]

    # 3. Search
    print(f"\n3. Test search su 'tono di voce CreAzioni Migranti'")
    chunks = client.search("tono di voce CreAzioni Migranti", [kb_id], top_k=3)
    print(f"   Chunk trovati: {len(chunks)}")
    for c in chunks[:3]:
        title = c.get("knowledge_title", "?")
        score = c.get("score", 0)
        content = c.get("content", "")[:100].replace("\n", " ")
        print(f"   [{score:.4f}] {title}")
        print(f"      {content}...")

    # 4. Get context
    print(f"\n4. Test get_context (max 500 char)")
    ctx = client.get_context("tono di voce", [kb_id], top_k=2, max_chars=500)
    print(f"   Contesto: {len(ctx)} caratteri")
    print(f"   Primi 200: {ctx[:200]}...")

    print("\n" + "═" * 60)
