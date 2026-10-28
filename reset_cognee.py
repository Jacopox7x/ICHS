import asyncio
from dotenv import load_dotenv
load_dotenv(".env.cognee")
import cognee

async def reset():
    print("🧹 Pulizia Cognee...")
    try:
        await cognee.prune.prune_data()
        await cognee.prune.prune_system(metadata=True)
        print("✅ Pulizia completata.")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    asyncio.run(reset())
