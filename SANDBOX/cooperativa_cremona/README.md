# Sandbox — CreAzioni Migranti

Sandbox contestuale per la cooperativa sociale **CreAzioni Migranti** (Cremona).

## Struttura

- `context.json` — Identità, contatti, valori, shop
- `lessico.json` — Parole chiave, da evitare, frasi modello
- `runner.py` — Orchestrazione: brief → iCrawler → output contestualizzato
- `content_generator.py` — Genera post social (IG, FB, Storie)
- `site_optimizer.py` — Genera testi per il sito
- `output_writer.py` — Salva output in Markdown
- `esempi/` — Brief di test

## Uso

### 1. Genera un piano social

    python3 runner.py esempi/brief_01.txt > output.json

### 2. Genera contenuti social

    python3 content_generator.py output.json

### 3. Genera testi per il sito

    python3 site_optimizer.py

### 4. Salva in Markdown

    python3 output_writer.py output.json

## Contesto

- **Nome:** CreAzioni Migranti
- **Tipo:** Sartoria sociale
- **Casa madre:** COSPER
- **Sede:** Via Bonomelli 11, 26100 Cremona
- **Contatti:** +39 388 822 6958 | creazioni.migranti@cosper.coop
- **Instagram:** @creazionimigranti
- **Sito:** creazionimigranti.org

## Tono di voce

Caldo e accogliente, ma concreto. Mai pietistico o vittimistico.
