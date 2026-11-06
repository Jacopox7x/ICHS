#!/usr/bin/env python3

import sqlite3
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

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    r = KnowledgeRetriever()
    data = r.retrieve("instagram")

    print("=== KNOWLEDGE RETRIEVER ===")
    for table, rows in data.items():
        print(f"{table}: {len(rows)}")
    r.close()
