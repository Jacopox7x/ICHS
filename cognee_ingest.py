import asyncio
import os
import cognee
from pathlib import Path

async def ingest_clients():
    print("🧹 Pulizia del database Cognee esistente...")
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

    workspaces_dir = Path("workspaces")
    
    for cliente_dir in workspaces_dir.iterdir():
        if not cliente_dir.is_dir(): continue
        
        cliente_name = cliente_dir.name
        print(f"\n📥 Ingestione per il cliente: {cliente_name}")
        
        # 1. Leggiamo il Voice Template
        voice_file = cliente_dir / "voice_template.txt"
        if voice_file.exists():
            voice_text = voice_file.read_text(encoding="utf-8")
            print(f"  -> Aggiungo voice_template.txt ({len(voice_text)} caratteri)")
            await cognee.add(voice_text, dataset_name=cliente_name)
            
        # 2. Leggiamo il context.json (se esiste)
        context_file = cliente_dir / "context.json"
        if context_file.exists():
            context_text = context_file.read_text(encoding="utf-8")
            print(f"  -> Aggiungo context.json ({len(context_text)} caratteri)")
            await cognee.add(context_text, dataset_name=cliente_name)

    print("\n🧠 Avvio Cognify (costruzione dei grafi). Potrebbe volerci un minuto...")
    # Nota: senza specificare extractor="gliner_demo", Cognee userà Ollama.
    # Dato che nel .env.cognee abbiamo impostato LLM_PROVIDER=ollama, userà Qwen.
    await cognee.cognify()
    
    print("\n✅ Ingestione completata! Il Knowledge Graph è pronto.")

if __name__ == "__main__":
    # Carica le variabili d'ambiente per Cognee
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_MODEL"] = "phi3.5-fixed"
    os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
    
    os.environ["EMBEDDING_PROVIDER"] = "ollama"
    os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
    os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/api/embed"
    os.environ["EMBEDDING_DIMENSIONS"] = "768"

    asyncio.run(ingest_clients())
