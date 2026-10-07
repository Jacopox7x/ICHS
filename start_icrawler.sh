#!/bin/bash
# Avvia Ollama in background se non è già in esecuzione
if ! pgrep -x "ollama" > /dev/null; then
    echo "🔄 Avvio Ollama..."
    ollama serve &
    sleep 5
else
    echo "✅ Ollama già in esecuzione"
fi

# Avvia iCrawler
echo "🕷️ Avvio iCrawler..."
cd ~/Documents/ICHS/dist
./iCrawler
