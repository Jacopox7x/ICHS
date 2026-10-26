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
