#!/bin/bash
echo "🛑 Spegnimento di iCrawler..."
pkill -f "uvicorn gliner_service:app" 2>/dev/null
pkill -f "uvicorn ui_server:app" 2>/dev/null
pkill -f "simplexng" 2>/dev/null
echo "✅ Processi iCrawler terminati. (Ollama lasciato attivo in background)."
