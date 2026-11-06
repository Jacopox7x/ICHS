import re

# 1. Ripara la funzione in icrawler_simple.py (rimuove il 'self' di troppo)
with open("icrawler_simple.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("def genera_newsletter(self, brief_cliente", "def genera_newsletter(brief_cliente")

with open("icrawler_simple.py", "w", encoding="utf-8") as f:
    f.write(code)

# 2. Aggiungi l'import in ui_server.py
with open("ui_server.py", "r", encoding="utf-8") as f:
    server_code = f.read()

if "from icrawler_simple import genera_newsletter" not in server_code:
    # Cerca la prima riga di import e aggiungi la nostra
    server_code = server_code.replace("import ollama", "import ollama\nfrom icrawler_simple import genera_newsletter")
    
    with open("ui_server.py", "w", encoding="utf-8") as f:
        f.write(server_code)

print("✅ Cavo ricollegato! La funzione ora è importabile.")
