#!/bin/bash
# Test aggiuntivi con output completo

echo "🕷️ TEST AGGIUNTIVI (VERBOSE)"
echo "================================"

tests=(
    "brief_eu_date.txt"
    "brief_presso.txt"
    "brief_nome_lungo.txt"
    "brief_senza_target.txt"
    "brief_orario_completo.txt"
    "brief_obiettivo_senza_euro.txt"
    "brief_con_link.txt"
    "brief_target_eta.txt"
)

for test in "${tests[@]}"; do
    echo ""
    echo "📋 $test"
    echo "--------------------------------"
    icrawler tests/$test --quick
    echo ""
done

echo "================================"
echo "✅ Test completati!"
