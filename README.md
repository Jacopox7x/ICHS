# ICHS — iCrawler Hybrid Strategist

Generatore di piani social + validatore visivo per brand di moda.

Estrae entità con GLiNER, arricchisce il prompt con hashtag semantici (Nomic),
genera il piano con Ollama (qwen2.5:3b per la strategia, phi3.5-fixed per la
narrativa, moondream per la vision). Valida immagini+caption con un rules
engine deterministico (stagionale, brand, coerenza visiva) e recupera le
linee guida del brand da Cognee (memoria vettoriale).

## Stato
- **v3.11.0** (12 novembre 2026): Vision Validator + Brand Memory Cosper
  - Rules engine deterministico (stagionale, brand, coerenza visiva)
  - Brand Cosper in Cognee (manifesto + style guide + lexicon)
  - Test suite end-to-end (5/5, P/R/F1 = 1.00)
  - Test rules-only (logica pura, 5/5)
- **v3.10.0** (9 novembre 2026): packaging base, clean install
- **v3.8** (26 ottobre 2026): stabile per uso personale
- **v4.0** (obiettivo dicembre 2026): loop di riformulazione + app Tauri

Vedi `docs/AVVIO.md` per l'avvio, `docs/BACKLOG.md` per il debito noto.

## Requisiti
- macOS con Apple Silicon (testato su M1, 8 GB RAM)
- Python 3.12
- OrbStack (o Docker) per SearXNG
- Ollama con i modelli:
  - `qwen2.5:3b` — strategia social
  - `phi3.5-fixed` — Cognee + motivazione Art Director
  - `moondream` — descrizione visiva delle immagini
  - `qwen2.5vl:3b` — OCR fallback (se Apple Vision non disponibile)
  - `nomic-embed-text` — embeddings per Cognee
- GLiNER `urchade/gliner_multi-v2.1` in cache (~2.3 GB)
- Cognee 1.6.6 (memoria vettoriale brand)

## Setup
```bash
cd ~/Documents/ICHS
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Modelli Ollama
ollama pull qwen2.5:3b
ollama pull phi3.5
ollama pull moondream
ollama pull qwen2.5vl:3b
ollama pull nomic-embed-text

# GLiNER (primo avvio scarica ~2.3 GB)
python3 -c "from gliner import GLiNER; GLiNER.from_pretrained('urchade/gliner_multi-v2.1')"

# SearXNG (in OrbStack/Docker)
docker run -d --name searxng -p 8888:8080 searxng/searxng

# Carica il brand Cosper in Cognee (una tantum)
./venv/bin/python scripts/ingest_brand_guidelines.py
```

## Avvio
```bash
# Avvia UI + GLiNER + SearXNG
./start_all.sh
# UI su http://127.0.0.1:8080

# Solo UI (se gli altri servizi sono già attivi)
./venv/bin/python ui_server.py
```

## Architettura

### Strategist (genera piano editoriale)
```
brief -> GLiNER (:8000) estrae entità
      -> SemanticHashtagEngine (Nomic) -> hashtag pertinenti
      -> PromptBuilder (prompts/strategist.txt)
      -> Ollama (:11434) qwen2.5:3b -> JSON piano
      -> Validator -> post-processing regex
      -> piano markdown -> workspaces/{sandbox}/output_plan_*.txt
```

### Vision Validator (Art Director — valida immagine + caption + brand)
```
POST /vision/validate-content (file + proposed_caption + brand_id)
  |
  v
1. Moondream descrive l'immagine
2. Cognee recupera le linee guida del brand (dataset '{brand_id}')
3. Open-Meteo fornisce temperatura reale per la città del brand
4. SearXNG recupera hashtag di tendenza
5. Rules engine deterministico:
   - _classifica_caption (estivo/invernale/neutro)
   - _valuta_stagione (caption vs meteo vs mese)
   - _valuta_brand (Cosper: no trekking/sportivo/tecnico)
   - _check_coerenza_visiva (caption estiva + img cappotto = blocca)
6. approvato = stagione_ok AND brand_ok AND visiva_ok
7. Phi-3.5 scrive la motivazione narrativa (se tronca, fallback a motivo tecnico)
  |
  v
JSON {descrizione_visiva, contesto_usato, verdetto{approvato, motivazione, ...}}
```

### Brand Memory (Cognee)
```
data/cosper/brand_manifesto.md  -
data/cosper/style_guide.md      |-> scripts/ingest_brand_guidelines.py
data/cosper/lexicon.md          -    -> Cognee dataset 'cosper' (GLiNER extractor)
                                   -> recuperato a runtime via cognee_manager.get_cognee_context()
```

## Test
```bash
# Logica pura (istantaneo, niente Moondream): deve dare 5/5
./venv/bin/python scripts/test_rules_only.py

# End-to-end (con immagini + Moondream, ~22s/caso): deve dare 5/5 con P/R/F1 = 1.00
./venv/bin/python scripts/test_validation.py

# Genera immagini sintetiche per i test 2-5 (una tantum)
./venv/bin/python scripts/generate_test_images.py
```

I 5 casi di test verificano:
| # | Caption | Brand | Atteso | Regola attivata |
|---|---------|-------|--------|-----------------|
| 1 | Costume estivo + cappotto in img | cosper | False | Stagionale + Visiva |
| 2 | Lana, inverno | cosper | True | Tutte ok |
| 3 | Trekking, montagna | cosper | False | Brand |
| 4 | Maglione, lana | cosper | True | Tutte ok |
| 5 | Costume a Natale | cosper | False | Stagionale (mese) |

## Moduli principali
- `ui_server.py` — FastAPI app, endpoint UI e API
- `icrawler_simple.py` — Strategist (genera piano editoriale JSON)
- `vision_router.py` — Validatore Art Director con rules engine
- `cognee_manager.py` — Recupero contesto brand da Cognee (thread-safe)
- `prompt_builder.py` — Template prompt da `prompts/strategist.txt`
- `hashtag_suggester.py` + `semantic_hashtags.py` — Generazione hashtag
- `quality_gate.py` — Controllo allucinazioni (entità non nel brief)
- `validator.py` — Validatore minimale output strategist
- `gliner_service.py` + `gliner_client.py` — NER locale (porta 8000)
- `memory.py` + `cognee_ingest.py` — Memoria Cognee
- `cascading_rag.py` — RAG gerarchico + SearXNG
- `scripts/ingest_brand_guidelines.py` — Carica brand in Cognee
- `scripts/test_validation.py` — Test suite end-to-end
- `scripts/test_rules_only.py` — Test logica pura
- `scripts/generate_test_images.py` — Genera immagini sintetiche di test

## Documentazione
- `docs/AVVIO.md` — istruzioni avvio dettagliate
- `docs/BACKLOG.md` — debito tecnico e roadmap
- `data/cosper/` — linee guida brand Cosper (manifesto, style guide, lexicon)
- `validation/` — 5 immagini di test + results.csv

## Versioning
- `v3.11.0` (12 novembre 2026): Vision Validator + Brand Memory Cosper
- `v3.10.0` (9 novembre 2026): packaging base, clean install
- `v3.8` (26 ottobre 2026): stabile per uso personale
- `v4.0` (obiettivo dicembre 2026): loop di riformulazione + app Tauri

Milestone tecniche intermedie del packaging (non sono versioni prodotto):
- `v0.5.1-packaging`, `v0.5.2-requirements`, `v0.5.3-clean-install`

## License
Private — Jacopo Galati
