import asyncio
from dotenv import load_dotenv
load_dotenv(".env.cognee")
import cognee

async def test():
    print("🧠 Ingestione testo di prova...")
    await cognee.prune.prune_system(metadata=True)
    await cognee.add("Cosper è una cooperativa sociale. Tono di voce professionale e caldo, si rivolge a famiglie e giovani.", dataset_name="test")
    print("🕸️ Costruzione grafo...")
    await cognee.cognify(datasets=["test"])
    print("🔍 Ricerca...")
    results = await cognee.search(query_text="Chi è Cosper?", query_type=cognee.SearchType.GRAPH_COMPLETION)
    for r in results:
        print(f"[Risultato] {r}")

if __name__ == "__main__":
    asyncio.run(test())
