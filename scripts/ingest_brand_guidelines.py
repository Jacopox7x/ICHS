"""
ingest_brand_guidelines.py v2 — Carica in Cognee il brand Cosper strutturato.
Legge data/cosper/*.md e li inserisce nel dataset 'cosper' di Cognee con GLiNER.
"""

import asyncio
import os
import sys
from pathlib import Path

import cognee

os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL"] = "phi3.5-fixed"
os.environ["LLM_ENDPOINT"] = "http://localhost:11434"
os.environ["LLM_API_KEY"] = "ollama"
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/api/embed"
os.environ["EMBEDDING_DIMENSIONS"] = "768"

BRAND_DIR = Path(__file__).resolve().parent.parent / "data" / "cosper"
BRAND_FILES = ["brand_manifesto.md", "style_guide.md", "lexicon.md"]


def load_brand_text() -> str:
    if not BRAND_DIR.exists():
        print(f"❌ Directory brand non trovata: {BRAND_DIR}")
        sys.exit(1)
    chunks = []
    for fname in BRAND_FILES:
        fpath = BRAND_DIR / fname
        if not fpath.exists():
            print(f"⚠️  File mancante: {fpath}")
            continue
        content = fpath.read_text(encoding="utf-8").strip()
        if content:
            chunks.append(f"=== {fname} ===\n{content}\n")
    if not chunks:
        print("❌ Nessun file brand trovato.")
        sys.exit(1)
    return "\n".join(chunks)


async def main():
    brand_text = load_brand_text()
    print(f"📚 Caricato brand Cosper: {len(brand_text)} caratteri da {len(BRAND_FILES)} file.")
    print(f"   Directory: {BRAND_DIR}")
    print("\n🧠 Ingestione in Cognee (dataset='cosper')...")
    await cognee.add(brand_text, dataset_name="cosper")
    try:
        await cognee.cognify(extractor="gliner_demo")
        print("✅ Ingestione completata con GLiNER.")
    except TypeError:
        print("   (Uso fallback: graph_model=None)")
        await cognee.cognify(graph_model=None)
        print("✅ Ingestione completata con GLiNER (fallback).")

    print("\n🔍 Verifica: ricerca 'linee guida Cosper'...")
    try:
        results = await cognee.search(
            query_text="linee guida Cosper abbigliamento eleganza urbana",
            datasets=["cosper"],
            query_type=cognee.SearchType.CHUNKS,
        )
        if results:
            print(f"   ✓ Trovati {len(results)} chunk.")
            first = results[0]
            preview = str(first.get("text", first)[:200]) if isinstance(first, dict) else str(first)[:200]
            print(f"   Anteprima: {preview}...")
        else:
            print("   ⚠️  Nessun risultato. Verifica che l'ingest sia andato a buon fine.")
    except Exception as e:
        print(f"   ⚠️  Verifica fallita: {e}")


if __name__ == "__main__":
    asyncio.run(main())
