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
