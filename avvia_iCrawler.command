#!/bin/bash
# Vai nella cartella del progetto
cd "$(dirname "$0")"

echo "======================================"
echo "🚀 AVVIO DI iCRAWLER (ALL-IN-ONE) 🚀"
echo "======================================"

# 1. Controlla e avvia SearXNG
echo "🌐 Controllo SearXNG (Docker)..."
if [ ! "$(docker ps -q -f name=searxng)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=searxng)" ]; then
        docker start searxng > /dev/null
    else
        docker run -d --name searxng -p 8888:8080 searxng/searxng > /dev/null
    fi
    echo "   -> SearXNG avviato."
else
    echo "   -> SearXNG già in esecuzione."
fi

# 2. Attiva l'ambiente virtuale
echo "🐍 Attivazione ambiente Python..."
source venv/bin/activate

# 3. Reset e Init Cognee (solo se necessario)
echo "🧠 Inizializzazione Cognee..."
# Cancella il DB vecchio per evitare mismatch (opzionale, ma sicuro)
if [ -f "venv/lib/python3.12/site-packages/cognee/.cognee_system/databases/cognee_db" ]; then
    rm -f venv/lib/python3.12/site-packages/cognee/.cognee_system/databases/cognee_db
fi
python3 init_cognee.py > /dev/null 2>&1
echo "   -> Cognee pronto."

# 4. Avvia il server UI
echo "🖥️  Avvio del server iCrawler..."
python3 ui_server.py &

# 5. Aspetta che il server sia pronto e apri il browser
sleep 3
open "http://localhost:8080"

echo "======================================"
echo "✅ TUTTO PRONTO! Premi Ctrl+C per chiudere."
echo "======================================"

# Mantiene il terminale aperto in attesa del server
wait
