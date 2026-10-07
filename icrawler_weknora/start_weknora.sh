#!/bin/bash
echo "🚀 Avvio WeKnora..."

# Verifica che Docker sia attivo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker non è attivo. Apri Docker Desktop e riprova."
    exit 1
fi

# Vai nella cartella di WeKnora
cd ~/Documents/ICHS/icrawler_weknora/WeKnora

# Avvia i container
docker compose up -d

# Aspetta 10 secondi
sleep 10

# Verifica stato
echo ""
echo "📊 Stato container:"
docker compose ps

echo ""
echo "🌐 Apri il browser su: http://localhost:80"
echo ""
echo "✅ WeKnora pronto!"
