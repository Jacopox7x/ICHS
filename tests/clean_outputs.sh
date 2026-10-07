#!/bin/bash
# Rimuove i file di output vecchi

echo "🧹 Pulizia file di output..."
echo "================================"

# Conta i file
count=$(ls -1 output_plan_*.txt 2>/dev/null | wc -l)
echo "File trovati: $count"

# Rimuovi
rm -f output_plan_*.txt
echo "✅ Puliti $count file"

# Rimuovi anche i file di cache
rm -rf cache/
echo "✅ Cache pulita"
