from cascading_rag import retrieve_context

print("🔍 Test di recupero RAG in corso...")
try:
    # Simuliamo una ricerca per il cliente Cosper
    risultati = retrieve_context("upcycling Cremona", "Cosper")
    print("✅ Recupero completato!")
    print(f"Risultato: {risultati}")
except Exception as e:
    print(f"❌ Errore: {e}")
