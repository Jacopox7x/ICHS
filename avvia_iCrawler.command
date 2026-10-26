#!/bin/bash
cd "$HOME/Documents/ICHS" || exit 1
source venv/bin/activate

if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    ollama serve > /tmp/ollama.log 2>&1 &
fi

if ! curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    nohup uvicorn gliner_service:app --host 127.0.0.1 --port 8000 > /tmp/gliner.log 2>&1 &
fi

if ! curl -s http://127.0.0.1:8080/health > /dev/null 2>&1; then
    nohup uvicorn ui_server:app --host 127.0.0.1 --port 8080 > /tmp/ui.log 2>&1 &
fi

for i in {1..30}; do
    if curl -s http://127.0.0.1:8080/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

open -a iCrawler

osascript -e 'tell application "Terminal" to close front window' & exit 0
