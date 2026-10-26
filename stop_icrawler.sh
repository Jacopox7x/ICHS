#!/bin/bash
pkill -f "uvicorn ui_server:app" 2>/dev/null
pkill -f "uvicorn gliner_service:app" 2>/dev/null
echo "Motore iCrawler arrestato (Ollama resta attivo)."
