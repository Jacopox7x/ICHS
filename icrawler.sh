#!/bin/bash
set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$PROJECT_DIR/.pids"
LOG_DIR="/tmp"
PORT_UI=8080
PORT_GLINER=8000
PORT_OLLAMA=11434
PORT_SEARXNG=8888
mkdir -p "$PID_DIR"

check_port() { lsof -ti ":$1" > /dev/null 2>&1; }

wait_for_port() {
    local port=$1 name=$2 max=${3:-30} i=0
    while [ $i -lt $max ]; do
        if check_port "$port"; then echo "  ✅ $name (porta $port)"; return 0; fi
        sleep 1; i=$((i + 1))
    done
    echo "  ❌ $name: timeout"; return 1
}

health_check() {
    local url=$1 name=$2 max=${3:-10} i=0
    while [ $i -lt $max ]; do
        if curl -sf "$url" > /dev/null 2>&1; then return 0; fi
        sleep 1; i=$((i + 1))
    done
    echo "  ⚠️  $name: porta aperta ma /health non risponde"
    return 1
}

cmd_start() {
    cd "$PROJECT_DIR"
    source venv/bin/activate
    echo "🚀 Avvio di iCrawler..."
    if ! check_port $PORT_OLLAMA; then
        echo "  -> Avvio Ollama..."
        ollama serve > "$LOG_DIR/ollama.log" 2>&1 &
        echo $! > "$PID_DIR/ollama.pid"
        wait_for_port $PORT_OLLAMA "Ollama" 15
    else echo "  ⏭️  Ollama già attivo"; fi
    if ! check_port $PORT_SEARXNG; then
        echo "  -> Avvio SearXNG..."
        uvx simplexng > "$LOG_DIR/searxng.log" 2>&1 &
        echo $! > "$PID_DIR/searxng.pid"
        wait_for_port $PORT_SEARXNG "SearXNG" 15
    else echo "  ⏭️  SearXNG già attivo"; fi
    if ! check_port $PORT_GLINER; then
        echo "  -> Avvio GLiNER..."
        uvicorn gliner_service:app --host 127.0.0.1 --port $PORT_GLINER > "$LOG_DIR/gliner.log" 2>&1 &
        echo $! > "$PID_DIR/gliner.pid"
        wait_for_port $PORT_GLINER "GLiNER" 30
        health_check "http://127.0.0.1:$PORT_GLINER/health" "GLiNER" 10
    else echo "  ⏭️  GLiNER già attivo"; fi
    if ! check_port $PORT_UI; then
        echo "  -> Avvio UI Server..."
        uvicorn ui_server:app --host 127.0.0.1 --port $PORT_UI > "$LOG_DIR/ui.log" 2>&1 &
        echo $! > "$PID_DIR/ui.pid"
        wait_for_port $PORT_UI "UI Server" 60
        health_check "http://127.0.0.1:$PORT_UI/health" "UI Server" 10
    else echo "  ⏭️  UI Server già attivo"; fi
    echo ""
    echo "🎉 iCrawler pronto: http://127.0.0.1:$PORT_UI"
}

cmd_stop() {
    echo "🛑 Fermo iCrawler..."
    for svc in ui gliner searxng ollama; do
        pidfile="$PID_DIR/$svc.pid"
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            if kill -0 "$pid" 2>/dev/null; then
                echo "  -> Fermo $svc (PID $pid)"
                kill "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null
            fi
            rm -f "$pidfile"
        fi
    done
    pkill -f "uvicorn gliner_service:app" 2>/dev/null || true
    pkill -f "uvicorn ui_server:app" 2>/dev/null || true
    pkill -f "simplexng" 2>/dev/null || true
    echo "✅ Tutti i servizi fermati."
}

cmd_status() {
    echo "📊 Stato servizi iCrawler:"
    for entry in "UI:$PORT_UI" "GLiNER:$PORT_GLINER" "SearXNG:$PORT_SEARXNG" "Ollama:$PORT_OLLAMA"; do
        name="${entry%%:*}"; port="${entry##*:}"
        if check_port "$port"; then echo "  ✅ $name (porta $port)"
        else echo "  ❌ $name (porta $port)"; fi
    done
}

cmd_logs() {
    local svc=${1:-ui}
    local file="$LOG_DIR/$svc.log"
    if [ -f "$file" ]; then
        echo "=== Log $svc (Ctrl+C per uscire) ==="
        tail -f "$file"
    else
        echo "❌ Log non trovato: $file"
    fi
}

cmd_backup() {
    local ts=$(date +%Y%m%d_%H%M%S)
    local bdir="$PROJECT_DIR/backups/cognee_$ts"
    mkdir -p "$bdir"
    echo "💾 Backup Cognee DB..."
    local found=0
    for path in \
        "$PROJECT_DIR/venv/lib/python3.12/site-packages/cognee/.cognee_system/databases" \
        "$PROJECT_DIR/.cognee_system/databases" \
        "$HOME/.cognee_system/databases"; do
        if [ -d "$path" ]; then
            echo "  -> Trovato: $path"
            cp -R "$path"/* "$bdir/" 2>/dev/null || true
            found=1
        fi
    done
    if [ $found -eq 0 ]; then echo "  ⚠️  Nessun DB Cognee trovato."; fi
    if [ -d "$PROJECT_DIR/accademia_material" ]; then
        mkdir -p "$bdir/accademia_material"
        cp -R "$PROJECT_DIR/accademia_material"/* "$bdir/accademia_material/" 2>/dev/null || true
        echo "  -> accademia_material/ copiato"
    fi
    echo "✅ Backup: $bdir"
    du -sh "$bdir"
}

case "${1:-}" in
    start)   cmd_start ;;
    stop)    cmd_stop ;;
    restart) cmd_stop && cmd_start ;;
    status)  cmd_status ;;
    logs)    cmd_logs "${2:-ui}" ;;
    backup)  cmd_backup ;;
    *) echo "Uso: $0 {start|stop|restart|status|logs [svc]|backup}"; exit 1 ;;
esac
