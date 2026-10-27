# Backlog iCrawler

## Da Content_Intelligence_Engine (subircodz, v0.2.0)
Riferimento: https://github.com/subircodz/Content_Intelligence_Engine

- [ ] v3.9: Quality Gate Python (check_pre_partenza.py) - sostituisce .sh fossile
- [ ] v3.9: Evidence Classification FULL/PARTIAL/WEAK/UNSUPPORTED in validator.py
- [ ] v3.9: WorkspaceConfig in workspaces/config.py
- [ ] v4.0: Search provider fallback (se integriamo web search)
- [ ] v4.0: Test deterministici separati da live (tests/run_all.sh)

## Da Panniantong/Agent-Reach (da valutare)
- [ ] Serve un vero "reach" social? Valutare integrazione esterna

## Debito tecnico noto (non urgente)
- [ ] tests/ ha 20 file + 3 script obsoleti (pre-v3.5)
- [ ] check_pre_partenza.sh cerca funzioni validator.py che non esistono più
- [ ] __pycache__ mescola cpython-312 e cpython-314 (residuo di un vecchio venv?)
- [ ] Backup .bak sparsi: archiviare in .archive/ o cancellare

## Debito residuo v3.8 (chiusa il 26 ottobre 2026)

- [ ] `_post_process_fields` è un cerotto che compensa i limiti di
  qwen2.5:3b (modello piccolo, ignora divieti negativi). Rimuovere
  quando si passa a qwen2.5:7b (v4.0), o quando il prompt usa solo
  esempi positivi astratti ("[Città]" invece di "Viareggio").
- [ ] Prompt `prompts/strategist.txt` contiene esempi concreti
  (Viareggio, ElectroBeach) che il modello copia su brief scarni.
  v3.9: sostituire con placeholder astratti.
- [ ] `check_pre_partenza.py` (Quality Gate) scritto ma NON integrato
  in `start_icrawler.sh`. v3.9: integrare + rimuovere il vecchio
  `check_pre_partenza.sh`.
- [ ] Test automatici: `tests/` ha 20 file + 3 script obsoleti
  (pre-v3.5). Consolidare in `tests/run_all.sh` con i 5 brief critici.
- [ ] A/B Llama3.2:3b vs Qwen2.5:3b (v3.9, vedi roadmap separata).

## Saggio/articolo non supportato in v3.8
- Brief non-evento (saggio, articolo, libro) producono piani social
  scarni (twitter/stories vuoti 4 volte su 4 su qwen2.5:3b).
- Non è un bug del codice: limite del modello 3B sul dominio non-evento.
- v3.9: ritestare con qwen2.5:7b (richiede >8 GB RAM, valutare hardware).
- v3.8: documentare come "best effort, non supportato ufficialmente".

## Prefissi Nomic provati e scartati (27 ottobre 2026)
- Esperimento: aggiunti prefissi "search_query:" (brief) e "search_document:"
  (hashtag) in semantic_hashtags.py secondo linee guida Nomic.
- Risultato: i punteggi si compattano (gap pertinenti/rumore scende da ~15
  a ~1-2 punti su BICI/CENA). Soglia 0.68 non ha più senso.
- Causa: con solo 8 hashtag nel db, i prefissi "search_document:" comprimono
  l'embedding verso altri document. Il beneficio Nomic si vede con corpus
  500-1000+ documenti.
- Decisione: rollback a v3.8.1 (senza prefissi). Rivalutare se hashtags_db
  cresce oltre 100 voci.
- Alternativa futura: ChromaDB con 500+ hashtag reali, poi riprovare prefissi.

## Fallback deterministico per sezioni vuote (v3.8.2, 27 ottobre 2026)
- qwen2.5:3b non produce sempre twitter/stories (specie su brief non-evento).
- _fill_missing_sections() genera template Python dai dati esistenti
  (hook, concept, target, visual) quando il modello salta la sezione.
- Output "meno creativo" ma "sempre completo". Scelta consapevole:
  meglio template che buco.
- v3.9: valutare two-stage generation se modello >3B disponibile.

## Memoria SQLite (v3.9.0, 27 ottobre 2026) — CHIUSA
- [x] memory.py: tabella plans, embedding Nomic, cosine similarity
- [x] Salvataggio automatico dopo ogni piano (id tracciato nei log)
- [x] Retrieval top-2 per cliente (soglia 0.65) iniettato nel prompt
- [x] Migrazione piani esistenti con filtro (91 piani importati, 1 scartato)
- [x] Test 1-4 verdi (migrazione, retrieval, end-to-end, retest 5 brief)
- [ ] v3.9.x: escludere brief identici (score > 0.99) dal retrieval
- [ ] v3.9.x: monitorare gonfiaggio output (brief_minimale +33%)
- [ ] v3.9.x: salvare brief originale in file separato (ora uso txt[:500])

## Memoria SQLite (v3.9.0, 27 ottobre 2026) — CHIUSA
- [x] memory.py: tabella plans, embedding Nomic, cosine similarity
- [x] Salvataggio automatico dopo ogni piano (id tracciato nei log)
- [x] Retrieval top-2 per cliente (soglia 0.65) iniettato nel prompt
- [x] Migrazione piani esistenti con filtro (91 piani importati, 1 scartato)
- [x] Test 1-4 verdi (migrazione, retrieval, end-to-end, retest 5 brief)
- [ ] v3.9.x: escludere brief identici (score > 0.99) dal retrieval
- [ ] v3.9.x: monitorare gonfiaggio output (brief_minimale +33%)
- [ ] v3.9.x: salvare brief originale in file separato (ora uso txt[:500])

## Cognee testato (27 ottobre 2026) — FATTIBILE
- [x] Installato `cognee[gliner]` con successo
- [x] Configurato Ollama (LLM + embedding) via `.env.cognee`
- [x] Test: brief Tech Summit → cognify → search → risposta corretta
      ("The budget for the event Tech Summit 2026 was 50000 euro.")
- [x] Grafo: 11 nodi, 13 edge
- [x] RAM: +165 MB rispetto a baseline (1.0 GB → 1.2 GB). Sostenibile.
- [ ] v3.9.1: integrare Cognee come quality gate pre-generazione
- [ ] v3.9.1: valutare Llama 3.2:3b per estrazione grafo (Cognee lo raccomanda;
      qwen2.5:3b ha warning su structured extraction)
- [ ] v3.9.1: fix tokenizer Nomic (HUGGINGFACE_TOKENIZER in .env.cognee)
- [ ] v4.0: valutare LightRAG come complemento (retrieval multi-hop)

## Cognee + Qwen 2.5:3b — test grafo reale (27 ottobre 2026, ore 11)
- Test: brief_festa.txt (Bologna, 20 settembre, famiglie/giovani, 1000 visitatori)
- Risultato: 13 nodi, 16 edge. Zero allucinazioni.
- Entità estratte correttamente: festa_di_quartiere, bologna, famiglie_e_giovani,
  1000_visitatori, commercianti_della_zona
- Relazioni sensate: begins_at, in, target_of, organized
- Warning "qwen2.5:3b limitato per graph extraction" è TEORICO su questo dataset.
  Qwen va bene per Cognee, almeno su brief strutturati.
- [ ] Prossimo test: get_gliner_demo_tasks() con label custom
      (evento, data, luogo, budget, target) invece delle label default
- [ ] Se label custom funzionano: integrare Cognee come quality gate v3.9.1
- [ ] Nota: 1000_visitatori classificato target_of invece di objective
      (con label custom si risolve)
