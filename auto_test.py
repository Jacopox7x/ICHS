import asyncio
import os
import cognee
from dotenv import load_dotenv

load_dotenv('.env')

async def main():
    doc_path = os.getenv('DOCUMENTS_PATH')
    print(f"📂 Inizio elaborazione documenti da: {doc_path}")
    
    print("⏳ Fase 1: Lettura file e creazione chunk...")
    await cognee.add(doc_path)
    
    print("🧠 Fase 2: Estrazione entità e creazione Knowledge Graph (Ollama Phi 3.5 in azione)...")
    print("   [Monitora la RAM! Se il Mac rallenta, è normale, stiamo spingendo sugli 8GB.]")
    
    await cognee.cognify()
    
    print("✅ Fatto! Il Knowledge Graph è stato creato con successo.")
    print("Controlla la cartella nascosta .cognee_system/databases per vedere i file generati.")
    
if __name__ == "__main__":
    asyncio.run(main())
