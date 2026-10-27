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
