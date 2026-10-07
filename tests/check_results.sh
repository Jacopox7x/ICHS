#!/bin/bash
# Mostra i risultati dei test più recenti

echo "🕷️ RISULTATI TEST"
echo "================================"
echo ""

# Mostra gli ultimi output
ls -lt output_plan_*.txt | head -5 | while read file; do
    echo "📄 $file"
    echo "--------------------------------"
    head -20 "$file"
    echo "..."
    echo ""
done
