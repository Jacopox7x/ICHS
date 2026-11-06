with open("ui_server.py", "r", encoding="utf-8") as f:
    code = f.read()

# Se c'è "from fastapi import FastAPI", aggiungiamo anche Request
if "from fastapi import FastAPI" in code and "Request" not in code.split("from fastapi import")[1].split("\n")[0]:
    code = code.replace("from fastapi import FastAPI", "from fastapi import FastAPI, Request")
# Altrimenti, se non c'è proprio nulla, aggiungiamo l'import in cima
elif "from fastapi import Request" not in code:
    code = "from fastapi import Request\n" + code

with open("ui_server.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Import di 'Request' aggiunto con successo!")
