with open("icrawler_simple.py", "r", encoding="utf-8") as f:
    code = f.read()

# Sostituiamo l'esempio di JSON rotto con la versione "escapata" per Python
old_json = '{"subject": "...", "preheader": "...", "saluto": "...", "corpo": "...", "cta": "..."}'
new_json = '{{"subject": "...", "preheader": "...", "saluto": "...", "corpo": "...", "cta": "..."}}'

if old_json in code:
    code = code.replace(old_json, new_json)
    with open("icrawler_simple.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Errore delle graffe (f-string) risolto!")
else:
    # Fallback se la stringa non è identica al 100%
    code = code.replace('{"subject":', '{{"subject":')
    code = code.replace('"cta": "..."}', '"cta": "..."}}')
    with open("icrawler_simple.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Fix applicato con metodo alternativo.")
