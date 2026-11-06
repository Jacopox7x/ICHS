import requests
import json
import time

# Configurazione (cambia la porta se il tuo SearXNG usa un'altra, es. 8888)
SEARXNG_URL = "http://localhost:8888/search"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3.5:latest"

def web_reach(query):
    print(f"🌐 1. Ricerca web in corso per: '{query}'...")
    
    # Facciamo la richiesta a SearXNG (chiedendo il formato JSON)
    params = {
        'q': query,
        'format': 'json'
    }
    
    try:
        response = requests.get(SEARXNG_URL, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get('results', [])
    except Exception as e:
        print(f"❌ Errore di connessione a SearXNG: {e}")
        print("Assicurati che Docker sia acceso e che SearXNG giri sulla porta 8080.")
        return

    if not results:
        print("⚠️ Nessun risultato trovato sul web.")
        return

    # Prendiamo i primi 3 risultati per non saturare il contesto
    top_results = results[:3]
    context = ""
    print("📄 2. Risultati trovati. Estrazione del contesto:")
    for i, r in enumerate(top_results):
        print(f"   - {r.get('title')}")
        context += f"- {r.get('title')}: {r.get('content')}\n"

    # Costruiamo il prompt per l'LLM
    prompt = f"""Sei un assistente esperto di moda e social media.
Usa le seguenti informazioni trovate sul web per rispondere alla domanda dell'utente. 
Se le informazioni non sono sufficienti, dillo chiaramente.

Informazioni dal web:
{context}

Domanda: {query}
Risposta:"""

    print(f"\n🧠 3. Invio a Ollama ({MODEL}) per la sintesi...")
    
    # Chiamata a Ollama
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3}
    }
    
    start_time = time.time()
    llm_response = requests.post(OLLAMA_URL, json=payload)
    elapsed = time.time() - start_time

    if llm_response.status_code == 200:
        risposta_finale = llm_response.json().get('response', '').strip()
        print("\n" + "="*50)
        print("🎯 RISPOSTA FINALE:")
        print(risposta_finale)
        print("="*50)
        print(f"⏱️ Tempo di generazione: {elapsed:.2f} secondi")
    else:
        print("❌ Errore da Ollama:", llm_response.text)

if __name__ == "__main__":
    # Testiamo una query tipica del tuo lavoro
    web_reach("Quali sono i colori Pantone principali per l'autunno inverno 2026 2027?")
