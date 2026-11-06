import re

FILE_PATH = "icrawler_simple.py"

with open(FILE_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Funzione per pulire il JSON grezzo di Phi
newsletter_func = '''

def genera_newsletter(self, brief_cliente, contesto_rag=""):
    prompt = f"""
    Sei un esperto Email Marketing Manager.
    Scrivi una newsletter per: {brief_cliente}
    Contesto: {contesto_rag}
    
    Rispondi ESCLUSIVAMENTE con un JSON valido con queste chiavi minuscole:
    {"subject": "...", "preheader": "...", "saluto": "...", "corpo": "...", "cta": "..."}
    """
    
    try:
        response = ollama.chat(
            model='phi3.5',
            messages=[{"role": "user", "content": prompt}]
        )
        output = response["message"]["content"]
        
        # Pulizia 1: Rimuove i backtick markdown
        if output.strip().startswith("```"):
            output = output.replace("```json", "").replace("```", "").strip()
            
        # Pulizia 2: Forza le chiavi in minuscolo e sistema le virgolette finali
        output = output.replace('"CTA"', '"cta"').replace('"Subject"', '"subject"')
        if not output.endswith("}"):
            output = output.rsplit("}", 1)[0] + "}"
            
        return output
    except Exception as e:
        return f'{"errore": "Errore di generazione: {e}"}'
'''

if "def genera_newsletter" not in code:
    code += newsletter_func

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Funzione Newsletter integrata e JSON fixato!")
