import duckdb
import json
from datetime import datetime
from typing import Dict, List, Optional

class OutputManager:
    def __init__(self, db_path: str = "icrawler_outputs.duckdb"):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self.init_tables()
    
    def init_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                plan_id VARCHAR PRIMARY KEY,
                brief TEXT,
                facts JSON,
                hashtags JSON,
                creative_lab JSON,
                full_plan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS hashtag_cache (
                cache_key VARCHAR PRIMARY KEY,
                hashtags JSON,
                category VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS plan_analytics (
                plan_id VARCHAR,
                platform VARCHAR,
                reach_estimate INTEGER,
                engagement_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def save_plan(self, plan_id: str, brief: str, facts: Dict, hashtags: List, creative_lab: Dict, full_plan: str) -> bool:
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO plans (plan_id, brief, facts, hashtags, creative_lab, full_plan)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (plan_id, brief, json.dumps(facts), json.dumps(hashtags), json.dumps(creative_lab), full_plan))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Errore salvataggio piano: {e}")
            return False
    
    def get_plan(self, plan_id: str) -> Optional[Dict]:
        result = self.conn.execute("""
            SELECT plan_id, brief, facts, hashtags, creative_lab, full_plan, created_at
            FROM plans WHERE plan_id = ?
        """, (plan_id,)).fetchone()
        if result:
            return {
                'plan_id': result[0],
                'brief': result[1],
                'facts': json.loads(result[2]),
                'hashtags': json.loads(result[3]),
                'creative_lab': json.loads(result[4]),
                'full_plan': result[5],
                'created_at': result[6]
            }
        return None
    
    def get_stats(self) -> Dict:
        total_plans = self.conn.execute("SELECT COUNT(*) FROM plans").fetchone()[0]
        total_hashtags_cached = self.conn.execute("SELECT COUNT(*) FROM hashtag_cache").fetchone()[0]
        total_analytics = self.conn.execute("SELECT COUNT(*) FROM plan_analytics").fetchone()[0]
        return {
            'total_plans': total_plans,
            'total_hashtags_cached': total_hashtags_cached,
            'total_analytics': total_analytics
        }
    
    def close(self):
        self.conn.close()

_output_manager = None
def get_output_manager():
    global _output_manager
    if _output_manager is None:
        _output_manager = OutputManager()
    return _output_manager
