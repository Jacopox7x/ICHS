import json
import networkx as nx
from pathlib import Path
from gliner_client import extract_entities, entities_to_dict

GRAPH_FILE = Path("graph_data.json")

def build_graph_from_text(text: str, cliente: str = "cosper"):
    """Estrae entità e costruisce un grafo locale."""
    print(f"🕸️ Costruzione grafo per il cliente: {cliente}")
    
    # 1. Estraiamo le entità con GLiNER
    raw_entities = extract_entities(text)
    if not raw_entities:
        return {"error": "Nessuna entità trovata"}
        
    entities = entities_to_dict(raw_entities)
    
    # 2. Creiamo un grafo diretto
    G = nx.DiGraph()
    
    # Aggiungiamo il nodo centrale del cliente
    G.add_node(cliente, type="organization", label=cliente)
    
    # Aggiungiamo i nodi delle entità e i collegamenti
    for category, values in entities.items():
        if isinstance(values, str):
            values = [values]
        for val in values:
            if not val or val == "Non specificato":
                continue
            G.add_node(val, type=category, label=val)
            G.add_edge(cliente, val, relation="ha_entità")
            
    # 3. Salviamo il grafo in un file JSON per la UI
    data = nx.node_link_data(G)
    
    # Se il file esiste, uniamo i nuovi dati (opzionale, per ora sovrascriviamo)
    GRAPH_FILE.write_text(json.dumps(data, indent=2))
    print(f"✅ Grafo salvato: {len(G.nodes)} nodi, {len(G.edges)} archi.")
    return data

def get_graph_data():
    """Restituisce i dati del grafo formattati per la UI."""
    if not GRAPH_FILE.exists():
        return {"nodes": [], "edges": []}
        
    data = json.loads(GRAPH_FILE.read_text())
    
    # Formattiamo per il frontend
    nodes = []
    for n in data.get("nodes", []):
        nodes.append({
            "id": str(n["id"]),
            "label": n.get("label", str(n["id"]))
        })
        
    edges = []
    for e in data.get("links", []):
        edges.append({
            "from": str(e["source"]),
            "to": str(e["target"])
        })
        
    return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    # Test rapido
    testo_test = "Cosper è una cooperativa sociale a Cremona. Si rivolge a famiglie e giovani."
    build_graph_from_text(testo_test)
    print(get_graph_data())

def build_manual_graph(nodes: list, cliente: str = "cosper"):
    """Costruisce un grafo manuale a partire da una lista di nodi."""
    G = nx.DiGraph()
    G.add_node(cliente, type="organization", label=cliente)
    for n in nodes:
        G.add_node(n, type="entity", label=n)
        G.add_edge(cliente, n, relation="collegato_a")
        
    data = nx.node_link_data(G)
    GRAPH_FILE.write_text(json.dumps(data, indent=2))
    print(f"✅ Grafo manuale salvato: {len(G.nodes)} nodi.")
    return get_graph_data()
