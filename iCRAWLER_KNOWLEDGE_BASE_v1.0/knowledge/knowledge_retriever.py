#!/usr/bin/env python3

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "knowledge_base.db"


class KnowledgeRetriever:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def retrieve(self, platform=None):
        context = {}
        cur = self.conn.cursor()

        if platform:
            cur.execute("""
                SELECT * FROM platform_rules
                WHERE platform=?
                ORDER BY priority DESC
            """, (platform,))
            context["platform_rules"] = [dict(x) for x in cur.fetchall()]

        for table in [
            "style_rules",
            "content_rules",
            "hashtag_rules",
            "visual_rules",
            "cta_rules",
            "anti_patterns",
            "validation_rules"
        ]:
            cur.execute(f"""
                SELECT * FROM {table}
                ORDER BY priority DESC
            """)
            context[table] = [dict(x) for x in cur.fetchall()]

        return context

    def retrieve_from_weknora(self, query: str, top_k: int = 5, max_chars: int = 3000) -> str:
        """Recupera contesto da WeKnora (RAG). Fallback graceful se non disponibile."""
        try:
            plugin_path = Path.home() / "Documents/ICHS/icrawler_weknora/plugin"
            if str(plugin_path) not in sys.path:
                sys.path.insert(0, str(plugin_path))

            from weknora_client import WeKnoraClient

            client = WeKnoraClient()
            if not client.health():
                return ""

            kb_id = client.find_kb_id("iCrawler")
            if not kb_id:
                return ""

            return client.get_context(query, [kb_id], top_k=top_k, max_chars=max_chars)

        except Exception as e:
            print(f"⚠️  WeKnora non disponibile: {e}")
            return ""

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    r = KnowledgeRetriever()
    data = r.retrieve("instagram")

    print("=== KNOWLEDGE RETRIEVER ===")
    for table, rows in data.items():
        print(f"{table}: {len(rows)}")

    print()
    print("=== TEST WEKNORA ===")
    context = r.retrieve_from_weknora("tono di voce CreAzioni Migranti", top_k=3, max_chars=800)
    print(f"Contesto: {len(context)} caratteri")
    if context:
        print(context[:500])
    else:
        print("(vuoto)")

    r.close()
