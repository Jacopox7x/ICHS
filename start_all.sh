#!/bin/bash
cd "$(dirname "$0")" || exit 1
source venv/bin/activate

echo "🚀 Avvio di iCrawler..."

# 1. Ollama
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "  -> Avvio Ollama..."
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 2
fi

# 2. SearXNG
if ! curl -s http://127.0.0.1:8888/ > /dev/null 2>&1; then
    echo "  -> Avvio SearXNG..."
    uvx simplexng > /tmp/searxng.log 2>&1 &
    sleep 2
fi

# 3. GLiNER
if ! curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "  -> Avvio GLiNER..."
    uvicorn gliner_service:app --host 127.0.0.1 --port 8000 > /tmp/gliner.log 2>&1 &
fi

# 4. UI Server
if ! curl -s http://127.0.0.1:8080/health > /dev/null 2>&1; then
    echo "  -> Avvio UI Server..."
    uvicorn ui_server:app --host 127.0.0.1 --port 8080 > /tmp/ui.log 2>&1 &
fi

echo -n "  -> Attendo che la UI sia pronta"
for i in {1..30}; do
    if curl -s http://127.0.0.1:8080/health > /dev/null 2>&1; then
        echo " ✅"
        echo "🎉 iCrawler è pronto all'uso!"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo " ❌ Timeout. Controlla i log in /tmp/"
exit 1
