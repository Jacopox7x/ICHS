import re
import shutil
import os

FILE_PATH = "icrawler_simple.py"
BACKUP_PATH = "icrawler_simple.py.bak_newsletter"

print("🔄 Creazione backup di sicurezza...")
shutil.copyfile(FILE_PATH, BACKUP_PATH)

with open(FILE_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Sostituisci il modello con phi3.5
print("🤖 Aggiornamento modello a phi3.5...")
code = code.replace("model='qwen3:4b'", "model='phi3.5'")
code = code.replace('model="qwen3:4b"', 'model="phi3.5"')
# Fallback se usavi un altro modello
code = code.replace("model='gemma2:2b'", "model='phi3.5'")

# 2. Inietta il pulisci-backtick
print("🧹 Iniezione pulisci-markdown...")
old_output_line = 'output = response["message"]["content"]'
new_output_block = '''output = response["message"]["content"]
            # Pulisce i backtick di markdown se presenti
            if output.strip().startswith("```"):
                output = output.replace("```json", "").replace("```", "").strip()'''

if old_output_line in code and "Pulisce i backtick" not in code:
    # Gestisce l'indentazione corretta in base al contesto
    code = code.replace('            ' + old_output_line, new_output_block)
    code = code.replace('        ' + old_output_line, new_output_block.replace('\n            ', '\n        '))

# 3. Aggiungi la funzione per la Newsletter
print("📰 Aggiunta funzionalità Newsletter...")
newsletter_func = '''

def genera_newsletter(self, brief_cliente, contesto_rag=""):
    """
    Genera una newsletter completa basata sul brief e sul contesto.
    """
    prompt = f"""
    Sei un esperto Email Marketing Manager.
    Scrivi una newsletter coinvolgente basata su questo brief:
    {brief_cliente}
    
    Contesto aggiuntivo (Knowledge Base):
    {contesto_rag}
    
    La newsletter deve includere:
    1. Un oggetto (Subject) accattivante (max 50 caratteri).
    2. Un Preheader (max 90 caratteri).
    3. Un saluto iniziale.
    4. Un corpo del testo strutturato in 2-3 paragrafi con eventuali bullet point.
    5. Una Call To Action (CTA) chiara.
    
    Rispondi ESCLUSIVAMENTE con un oggetto JSON valido con questa struttura:
    {
        "subject": "testo",
        "preheader": "testo",
        "saluto": "testo",
        "corpo": "testo",
        "cta": "testo"
    }
    """
    
    try:
        response = ollama.chat(
            model='phi3.5',
            messages=[{"role": "user", "content": prompt}]
        )
        output = response["message"]["content"]
        if output.strip().startswith("```"):
            output = output.replace("```json", "").replace("```", "").strip()
        return output
    except Exception as e:
        return f"Errore durante la generazione della newsletter: {e}"
'''

# Aggiungi la funzione in fondo alla classe (o al file)
if "def genera_newsletter" not in code:
    code += newsletter_func

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Patch completata con successo!")
print(f"Backup salvato in: {BACKUP_PATH}")
