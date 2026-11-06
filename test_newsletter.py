import ollama

def genera_newsletter(brief):
    prompt = f"""Sei un esperto Email Marketing Manager. Scrivi una newsletter per: {brief}
    Rispondi SOLO con un JSON valido con chiavi: subject, preheader, saluto, corpo, cta."""
    
    response = ollama.chat(
        model='phi3.5',
        messages=[{"role": "user", "content": prompt}]
    )
    out = response["message"]["content"]
    if out.strip().startswith("```"):
        out = out.replace("```json", "").replace("```", "").strip()
    return out

print(genera_newsletter("Lancio del nuovo servizio di upcycling di Cosper a Cremona."))
