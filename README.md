# iCrawler

Generatore di piani social a partire da un brief in linguaggio naturale.
Usa GLiNER (locale) per estrarre entita, Ollama + llama3.2 per generare
il piano, un Validator per controllare che il piano contenga le entita.

## Requisiti

- macOS con Apple Silicon (testato su MacBook Air M1, 8 GB)
- Python 3.12
- Ollama installato
- Modello llama3.2:3b scaricato (`ollama pull llama3.2:3b`)

## Setup

    cd ~/Documents/ICHS
    python3.12 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    # Scarica il modello GLiNER (2.3 GB, una volta sola)
    python3 -c "from gliner import GLiNER; GLiNER.from_pretrained('urchade/gliner_multi-v2.1')"

## Avvio

    # Terminale 1
    ollama serve

    # Terminale 2
    cd ~/Documents/ICHS && source venv/bin/activate
    uvicorn gliner_service:app --host 127.0.0.1 --port 8000

    # Terminale 3
    cd ~/Documents/ICHS && source venv/bin/activate
    python3 icrawler_simple.py

Oppure, se l'alias e configurato:

    icrawler

## Architettura

    brief -> GLiNER -> prompt_builder -> Ollama -> JSON -> Validator -> piano

- gliner_service.py: microservizio FastAPI per estrazione entita
- gliner_client.py: client HTTP verso il microservizio
- prompt_builder.py: costruisce il prompt con entita e regole
- validator.py: verifica che il piano contenga le entita estratte
- icrawler_simple.py: entrypoint CLI

## Documentazione

Vedi docs/ per le specifiche di Eidolopoiesis e Visual Parser.
