#!/bin/bash
# Esegue tutti i test e salva i log

echo "🕷️ iCRAWLER - TEST SUITE"
echo "================================"
echo ""

# Usa il percorso assoluto
ICRAWLER_CMD="$HOME/Documents/ICHS/icrawler"

# Se non esiste, prova a usare l'alias
if [ ! -f "$ICRAWLER_CMD" ]; then
    echo "⚠️ Script non trovato, uso alias..."
    ICRAWLER_CMD="icrawler"
fi

# Array dei test (solo quelli che hanno senso)
tests=(
    "brief_minimale.txt"
    "brief_lungo.txt"
    "brief_perfetto.txt"
    "brief_festa.txt"
)

# Crea directory per i log
mkdir -p tests/logs

for test in "${tests[@]}"; do
    echo "📋 Test: $test"
    echo "--------------------------------"
    
    # Esegui con --quick per velocizzare
    $ICRAWLER_CMD tests/$test --quick 2>&1 | tee tests/logs/${test}.log
    echo ""
done

echo "================================"
echo "✅ Test completati!"
echo "📁 Log salvati in tests/logs/"
