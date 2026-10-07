#!/bin/bash
# iCrawler V1.5 - Controllo pre-partenza
# Esegui con: bash ~/Documents/ICHS/check_pre_partenza.sh

echo ""
echo "=========================================="
echo "🕷️ iCRAWLER V1.5 - CONTROLLO PRE-PARTENZA"
echo "=========================================="
echo ""

# 1. File principali
echo "📁 FILE PRINCIPALI"
echo "------------------"
FILES=("icrawler_simple.py" "validator.py" "prompt_builder.py" "hashtag_cloud.py" "config.py")
for f in "${FILES[@]}"; do
    if [ -f ~/Documents/ICHS/$f ]; then
        echo "  ✅ $f"
    else
        echo "  ❌ $f MANCANTE"
    fi
done

# 2. Cartella prompts
echo ""
echo "📂 PROMPTS"
echo "----------"
if [ -f ~/Documents/ICHS/prompts/strategist.txt ]; then
    echo "  ✅ prompts/strategist.txt"
else
    echo "  ❌ prompts/strategist.txt MANCANTE"
fi

# 3. Validator - controlli attivi
echo ""
echo "✅ VALIDATOR - CONTROLLI ATTIVI"
echo "-------------------------------"
CONTROLLI=("check_data" "check_luogo" "check_target" "check_hashtags" "check_structure" "check_stories" "check_teaser" "check_budget" "check_links" "check_kpi" "check_quality" "check_contamination" "check_nome_evento")
for c in "${CONTROLLI[@]}"; do
    if grep -q "$c" ~/Documents/ICHS/validator.py 2>/dev/null; then
        echo "  ✅ $c"
    else
        echo "  ❌ $c NON TROVATO"
    fi
done

# 4. Hashtag cloud
echo ""
echo "☁️ HASHTAG CLOUD"
echo "----------------"
if grep -q "FALLBACK_HASHTAGS" ~/Documents/ICHS/hashtag_cloud.py 2>/dev/null; then
    echo "  ✅ Fallback presente"
else
    echo "  ❌ Fallback mancante"
fi

# 5. Modello Ollama
echo ""
echo "🧠 OLLAMA"
echo "---------"
if pgrep -x "ollama" > /dev/null; then
    echo "  ✅ Ollama in esecuzione"
else
    echo "  ⚠️ Ollama NON in esecuzione (avvia con: ollama serve)"
fi

# 6. Modelli disponibili
echo ""
echo "📦 MODELLI INSTALLATI"
echo "---------------------"
ollama list 2>/dev/null | grep -E "phi3.5|gemma|llava" || echo "  ⚠️ Nessun modello trovato"

# 7. Backup
echo ""
echo "💾 BACKUP"
echo "---------"
if [ -f ~/Documents/ICHS/icrawler_v1.5_backup_*.tar.gz 2>/dev/null ]; then
    echo "  ✅ Backup esistente"
else
    echo "  ⚠️ Nessun backup trovato (crea con: tar -czf icrawler_v1.5_backup_$(date +%Y%m%d).tar.gz .)"
fi

# 8. Changelog
echo ""
echo "📋 CHANGELOG"
echo "------------"
if [ -f ~/Documents/ICHS/CHANGELOG_V1.5.md ]; then
    echo "  ✅ CHANGELOG_V1.5.md"
else
    echo "  ❌ CHANGELOG mancante"
fi

echo ""
echo "=========================================="
echo "✅ CONTROLLO COMPLETATO"
echo "=========================================="
echo ""
