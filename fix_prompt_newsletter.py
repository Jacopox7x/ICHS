import re

with open("icrawler_simple.py", "r", encoding="utf-8") as f:
    code = f.read()

# Troviamo e sostituiamo il prompt della newsletter
old_prompt_regex = r'prompt = f"""[\s\S]*?Sei un esperto Email Marketing Manager\.[\s\S]*?"""'

new_prompt = '''prompt = f"""
    Sei un esperto Email Marketing Manager.
    Il tuo compito è scrivere una newsletter basata RIGOROSAMENTE su questo brief:
    
    BRIEF: {brief_cliente}
    
    REGOLE FONDAMENTALI:
    1. Devi parlare ESCLUSIVAMENTE dell'argomento menzionato nel BRIEF.
    2. Non inventare prodotti, servizi o argomenti (es. niente caffè o tè se il brief parla di e-bike).
    3. Usa un tono adatto al brief.
    
    Rispondi SOLO con un oggetto JSON valido con questa struttura:
    {{
        "subject": "Un oggetto accattivante (max 50 caratteri)",
        "preheader": "Un sottotitolo (max 90 caratteri)",
        "saluto": "Un saluto iniziale",
        "corpo": "Il testo della newsletter (2-3 paragrafi)",
        "cta": "La call to action finale"
    }}
    """'''

if re.search(old_prompt_regex, code):
    code = re.sub(old_prompt_regex, new_prompt, code)
    with open("icrawler_simple.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Prompt della newsletter aggiornato e reso 'a prova di allucinazione'!")
else:
    print("⚠️ Impossibile trovare il blocco esatto del prompt. Mandami il codice della funzione.")
