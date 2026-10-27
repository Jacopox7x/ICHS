# iCrawler

Generatore di piani social a partire da un brief in linguaggio naturale.
Estrae entità con GLiNER (locale), arricchisce il prompt con hashtag
semantici (Nomic), genera il piano con Ollama + qwen2.5:3b, valida e
pulisce l'output.

## Stato

- **v3.8** (26 ottobre 2026): stabile per uso personale
- **v3.9** (in pianificazione): Quality Gate, A/B Llama vs Qwen
- **v4.0** (obiettivo dicembre 2026): app desktop Tauri

Vedi `docs/AVVIO.md` per l'avvio, `docs/BACKLOG.md` per il debito noto.

## Requisiti

- macOS con Apple Silicon (testato su M1, 8 GB RAM)
- Python 3.12
- Ollama con `qwen2.5:3b` e `nomic-embed-text`
- GLiNER `urchade/gliner_multi-v2.1` in cache (~2.3 GB)

## Setup

    cd ~/Documents/ICHS
    python3.12 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    ollama pull qwen2.5:3b
    ollama pull nomic-embed-text
    python3 -c "from gliner import GLiNER; GLiNER.from_pretrained('urchade/gliner_multi-v2.1')"

## Avvio

Un solo comando:

    icrawler

UI su `http://127.0.0.1:8080`.

## Architettura

    brief
      -> GLiNER (:8000) estrae entita
      -> SemanticHashtagEngine (Nomic) -> hashtag pertinenti
      -> PromptBuilder (prompts/strategist.txt)
      -> Ollama (:11434) qwen2.5:3b
      -> JSON -> Validator -> post-processing regex
      -> piano markdown -> output_plan_*.txt

## Documentazione

- `docs/AVVIO.md` — istruzioni avvio dettagliate
- `docs/BACKLOG.md` — debito tecnico e roadmap

## Versioning

Git tag su ogni release. Vedi `git tag -l`.
