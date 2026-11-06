import asyncio
import cognee

async def main():
    print("📥 Aggiunta dati di test a Cognee...")
    # Aggiungiamo un testo di esempio sul nostro cliente
    await cognee.add("Cosper è un'azienda di upcycling con sede a Cremona. Promuove la sostenibilità e la mobilità dolce.")
    
    print("🧠 Cognizione in corso (creazione del grafo)...")
    await cognee.cognify()
    
    print("✅ Cognee inizializzato e pronto per le ricerche!")

if __name__ == "__main__":
    asyncio.run(main())
