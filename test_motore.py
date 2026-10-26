from icrawler_simple import ICrawler

print("🚀 Inizializzazione motore...")
c = ICrawler()

brief = "Lavori in Corso: un progetto a Cremona per l'inclusione attiva e il lavoro delle persone con disabilità, con riparazione di bici."

print("\n⏳ Generazione in corso (attendi Ollama)...")
risultato = c.generate_strategy(brief, mode='social', sandbox='cosper')

print("\n" + "="*50)
print("🎯 RISULTATO FINALE:")
print("="*50)
print(risultato)
