import re

with open("icrawler_simple.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Troviamo la funzione genera_newsletter
match = re.search(r'def genera_newsletter.*?prompt\s*=\s*f"""(.*?)"""', code, re.DOTALL)

if match:
    prompt_content = match.group(1)
    # 2. Sostituiamo TUTTE le graffe singole con doppie graffe all'interno della f-string
    # Questo impedisce a Python di interpretarle come variabili
    new_prompt_content = prompt_content.replace('{', '{{').replace('}', '}}')
    
    # 3. Sostituiamo il vecchio prompt con quello corretto nel codice originale
    code = code.replace(prompt_content, new_prompt_content)
    
    with open("icrawler_simple.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Fix completato! Le graffe della f-string ora sono corrette (doppie).")
else:
    print("❌ Impossibile trovare la funzione. Mandami il codice della funzione genera_newsletter.")
