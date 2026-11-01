import json
import sqlite3
import networkx as nx
from pathlib import Path
from gliner_client import extract_entities, entities_to_dict

DB_PATH = Path("memory.db")
GRAPH_PATH = Path("graph_data.json")

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS briefs 
                    (id INTEGER PRIMARY KEY, cliente TEXT, brief TEXT, piano TEXT)''')
    return conn

def save_brief(cliente: str, brief: str, piano: str):
    """Salva brief e piano nel database SQLite."""
    conn = _get_conn()
    conn.execute("INSERT INTO briefs (cliente, brief, piano) VALUES (?, ?, ?)", (cliente, brief, piano))
    conn.commit()
    conn.close()

def get_context_for_brief(brief: str, cliente: str) -> str:
    """Recupera gli ultimi piani per il cliente come contesto."""
    conn = _get_conn()
    rows = conn.execute("SELECT piano FROM briefs WHERE cliente = ? ORDER BY id DESC LIMIT 2", (cliente,)).fetchall()
    conn.close()
    if not rows:
        return ""
    return "\n\n=== PIANI PRECEDENTI ===\n" + "\n---\n".join([r[0][:500] for r in rows])

def build_and_save_graph(text: str, cliente: str):
    """Estrae entità con GLiNER, costruisce un grafo NetworkX e lo salva su JSON."""
    raw = extract_entities(text)
    if not raw:
        return
    
    entities = entities_to_dict(raw)
    
    G = nx.DiGraph()
    G.add_node(cliente, label=cliente, type="organization")
    
    for category, values in entities.items():
        if isinstance(values, str):
            values = [values]
        for val in values:
            if not val or val == "Non specificato":
                continue
            G.add_node(val, label=val, type=category)
            G.add_edge(cliente, val, relation="ha_entità")
            
    data = nx.node_link_data(G)
    GRAPH_PATH.write_text(json.dumps(data, indent=2))
    print(f"🕸️ Grafo salvato: {len(G.nodes)} nodi, {len(G.edges)} archi.")

def get_graph_data():
    """Restituisce i nodi e gli archi per la UI."""
    if not GRAPH_PATH.exists():
        return {"nodes": [], "edges": []}
    data = json.loads(GRAPH_PATH.read_text())
    
    nodes = [{"id": str(n["id"]), "label": n.get("label", str(n["id"]))} for n in data.get("nodes", [])]
    edges = [{"from": str(e["source"]), "to": str(e["target"])} for e in data.get("links", [])]
    
    return {"nodes": nodes, "edges": edges}
