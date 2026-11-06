import asyncio
import os
import cognee
from dotenv import load_dotenv

load_dotenv('.env')

async def main():
    # Facciamo una domanda che richiede di collegare i due documenti
    domanda = "Chi è il CEO di Neon Threads e qual è il budget per il social marketing?"
    
    print(f"❓ Domanda: {domanda}")
    print("🔍 Ricerca nel Knowledge Graph e generazione della risposta con Phi 3.5...\n")
    
    # Eseguiamo la ricerca
    results = await cognee.search(domanda)
    
    print("\n--- RISPOSTA ---")
    for res in results:
        print(res)
    print("----------------")

if __name__ == "__main__":
    asyncio.run(main())
