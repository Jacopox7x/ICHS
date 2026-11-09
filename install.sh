#!/bin/bash
set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

AUTO_YES=false
for arg in "$@"; do
    case $arg in -y|--yes) AUTO_YES=true ;; esac
done

ask_install() {
    local name=$1 cmd=$2
    if [ "$AUTO_YES" = true ]; then
        echo "  -> Installo $name (--yes)..."
        eval "$cmd"
    else
        read -p "  Installo $name? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then eval "$cmd"
        else echo "  ❌ $name richiesto. Esco."; exit 1; fi
    fi
}

echo "🔧 iCrawler — Installazione"
echo ""
echo "📋 Verifica prerequisiti..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trovato."; exit 1
fi
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  ✅ Python $PY_VERSION"

if command -v brew &> /dev/null; then echo "  ✅ Homebrew"
else echo "  ⚠️  Homebrew non trovato."; fi

if ! command -v ollama &> /dev/null; then
    if command -v brew &> /dev/null; then ask_install "Ollama" "brew install ollama"
    else echo "  ❌ Installa Ollama: https://ollama.com/download"; exit 1; fi
fi
echo "  ✅ Ollama"

if ! command -v uvx &> /dev/null; then
    if command -v brew &> /dev/null; then ask_install "uv (per SearXNG)" "brew install uv"; fi
fi

echo ""
echo "📥 Verifica modelli Ollama..."
for model in moondream phi3.5 nomic-embed-text; do
    if ollama list 2>/dev/null | grep -q "^$model"; then echo "  ✅ $model"
    else echo "  📥 Scarico $model..."; ollama pull "$model" || { echo "  ❌ Fallito"; exit 1; }; fi
done

# Build phi3.5-fixed se assente
if ! ollama list 2>/dev/null | grep -q "^phi3.5-fixed"; then
    if [ -f "Modelfile.phi3.dockerfile" ]; then
        echo "  🔧 Creo phi3.5-fixed da Modelfile..."
        ollama create phi3.5-fixed -f Modelfile.phi3.dockerfile || {
            echo "  ❌ Fallito"; exit 1; }
        echo "  ✅ phi3.5-fixed creato"
    fi
fi

echo ""
echo "🐍 Setup venv..."
if [ ! -d "venv" ]; then python3 -m venv venv; echo "  ✅ venv creato"
else echo "  ⏭️  venv esistente"; fi
source venv/bin/activate
pip install --upgrade pip --quiet

echo ""
echo "📦 Installazione dipendenze..."
if [ ! -f "requirements.txt" ]; then echo "  ❌ requirements.txt mancante"; exit 1; fi
pip install -r requirements.txt
echo "  ✅ Dipendenze installate"

echo ""
echo "⚙️  Configurazione..."
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "  ✅ .env creato"
else
    echo "  ⏭️  .env esistente"
fi

echo ""
echo "🧪 Verifica import..."
if python3 -c "import ui_server" 2>/tmp/import_error.log; then
    echo "  ✅ ui_server importa"
else
    echo "  ❌ Import fallito:"; tail -10 /tmp/import_error.log; exit 1
fi


echo ""
echo "🔎 Verifica SearXNG (Docker, opzionale)..."
if ! command -v docker &>/dev/null; then
    echo "  ⚠️  Docker assente. Hashtag di tendenza offline."
elif ! docker info >/dev/null 2>&1; then
    echo "  ⚠️  Docker non in esecuzione. Avvia Docker Desktop."
else
    echo "  ✅ Docker disponibile"
    docker pull searxng/searxng 2>&1 | tail -1
fi
echo ""
echo "🎉 Installazione completata!"
echo "  ./icrawler.sh start"
echo "  ./icrawler.sh status"
echo "  ./icrawler.sh backup"
