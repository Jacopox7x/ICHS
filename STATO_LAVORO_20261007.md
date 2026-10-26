# Stato lavori iCrawler - 7 ottobre 2026

## Cosa funziona

- Venv: /Users/jacopogalati/Documents/ICHS/venv/ con Python 3.12.15
- Pacchetti: torch 2.14.1, gliner 0.2.29, fastapi, uvicorn, transformers, tiktoken, protobuf
- MPS attivo (GPU del Mac usata da torch)
- Modello GLiNER: urchade/gliner_multi-v2.1, 2.31 GB, in cache
- Microservizio: /Users/jacopogalati/Documents/ICHS/gliner_service.py
- Testati 3 endpoint, tutti passati

## Cosa non e fatto

- Integrazione GLiNER in icrawler_simple.py
- WeKnora Lite
- Plugin WeKnora -> GLiNER

## Prossimo passo

Chiudere iCrawler content strategy end-to-end con GLiNER:
1. Chiamare /extract da generate_strategy
2. Passare entita estratte al PromptBuilder
3. Validator verifica che il piano contenga le entita

Tempo stimato: mezza giornata.

## Come riprendere

Aprire terminale, poi:
cd /Users/jacopogalati/Documents/ICHS
source venv/bin/activate
uvicorn gliner_service:app --host 127.0.0.1 --port 8000

In un altro terminale:
curl http://127.0.0.1:8000/health

## Note

- Servizio occupa circa 3 GB RAM
- Primo caricamento dopo avvio: 5-15 secondi
- Ctrl+C per fermare uvicorn
- Il root / risponde Not Found, usare /docs o /health nel browser

fine file

## Sera tardi 7 ottobre - CICLO CHIUSO

### Fatto
- Integrazione GLiNER in icrawler_simple.py completata
- prompt_builder.py esteso per accettare entita GLiNER
- validator.py riscritto da zero (versione minimale)
- Test end-to-end passato: brief -> GLiNER -> prompt -> llama3.2 -> piano validato
- Il piano viene salvato automaticamente in output_plan_*.txt

### Stato attuale
- Microservizio GLiNER: ~/Documents/ICHS/gliner_service.py
- Client GLiNER: ~/Documents/ICHS/gliner_client.py
- icrawler_simple.py: integrato con gliner_client
- prompt_builder.py: accetta parametro entities
- validator.py: riscritto da zero, minimale
- Modello Ollama: llama3.2:3b

### Note
- validator.py.originale_rotto contiene la versione precedente
- validator.py.bak2, bak3, bak4 sono backup intermedi
- Nessuno di questi backup e affidabile, la versione corrente e l'unica funzionante

### Prossimo passo
- Decidere se migliorare la qualita del piano (modello piu grande? prompt ritarato?)
- Oppure integrare iCrawler con WordPress
- Oppure integrare GLiNER con WeKnora Lite
- Non tutti insieme. Uno alla volta.

### Avvio quando riprendo
Terminale 1: cd ~/Documents/ICHS && source venv/bin/activate && uvicorn gliner_service:app --host 127.0.0.1 --port 8000
Terminale 2: cd ~/Documents/ICHS && source venv/bin/activate && python3 icrawler_simple.py


## Aggiornamento 8 ottobre (pomeriggio)

### Fatto
- Installato autoscraper e feedparser nel venv
- Creato rss_reader.py (80 righe): legge feed RSS e formatta articoli
  per il prompt
- Testato su ANSA Tecnologia e Repubblica Tecnologia: funziona
- Verificato che ANSA e statico (HTML accessibile via requests),
  quindi AutoScraper sarebbe utilizzabile come fallback

### Non fatto (volutamente)
- rss_reader.py NON e integrato in iCrawler. E un modulo isolato.

### Problema aperto
- I feed generalisti (ANSA Tecnologia) contengono notizie del giorno,
  non informazioni sull'evento specifico del brief. Il contesto
  rischia di essere rumore.
- Serve una strategia: filtrare con GLiNER, o usare feed di settore
  specifici per categoria evento.

### Prossimo passo (domani, con calma)
- Decidere se e come usare rss_reader in iCrawler
- Opzione A: contesto passivo (rischio rumore)
- Opzione B: filtraggio con GLiNER (piu preciso)
- Opzione C: feed di settore invece di generalisti (piu solido ma
  richiede ricerca di feed specifici)

### File nuovi
- rss_reader.py
- test_autoscraper.py (per prova, si puo cancellare)


## Aggiornamento 8 ottobre (tardo pomeriggio)

### Fatto
- rss_reader.py esteso con filter_by_brief (filtro restrittivo)
- Filtro con min_common=1 testato:
  - Brief fintech -> 0 titoli (corretto, filtra rumore)
  - Brief AI -> 1 titolo rilevante (L'IA puo portare all'estinzione)
- rss_reader.py pronto per essere integrato in iCrawler

### Decisioni di design ancora aperte (prima di integrare)
1. Quali feed RSS usare? (non basta ANSA Tecnologia per ogni tipo di evento)
2. Dove mettere la lista dei feed? config.py, feeds.json, o altro?
3. Quando attivare il reach esterno? Sempre, o solo per brief scarni?

### Prossimo passo
- Prendere le 3 decisioni di design sopra
- Poi integrare rss_reader in icrawler_simple.py
- Poi test end-to-end con un brief che ha titoli RSS rilevanti

### File nuovi
- rss_reader.py (138 righe, con filter_by_brief)
- rss_reader.py.bak (versione precedente senza filtro)


## Test con brief ElectroBeach (8 ottobre)

Pipeline testata con successo su un brief reale di festival musicale.
Piano generato in ~40 secondi, tutte le sezioni compilate.

Punti di forza:
- Entita estratte correttamente (target, budget, luogo, date)
- Hashtag pertinenti
- Numeri del brief rispettati (5 DJ, 2 palchi, Viareggio, 18-35 anni)

Problemi rilevati:
- Bug "#... anni" nel campo hashtag (Instagram + Facebook): "anni"
  senza cancelletto, residuo del target
- LinkedIn usa lo stesso tono di Instagram (fuori contesto)
- KPI non citano il numero "1.500 partecipanti" dal brief
- Visual ripetuti tra piattaforme
- Calendario senza righe per giorno evento / giorno dopo

Da migliorare nel prompt (prossima sessione):
- Istruzioni specifiche per LinkedIn
- Richiesta di visual diversi per piattaforma
- Calendario esteso con live coverage e recap
- KPI con numeri espliciti dal brief


## Aggiornamento 8 ottobre (sera) - UI FUNZIONANTE

### Fatto
- ui_server.py + ui.html: interfaccia web locale su porta 8080
- start_icrawler.sh: script di avvio che lancia tutti e tre i servizi
- Alias "icrawler" in ~/.zshrc

### Come si usa
Dal terminale: icrawler
Poi browser su http://127.0.0.1:8080

### Servizi attivi
- Ollama porta 11434
- GLiNER porta 8000
- UI server porta 8080

### Test riuscito
Brief ElectroBeach -> piano completo generato in ~40 secondi.
Vedi nota precedente per i problemi rilevati nel piano.

### Da fare prossima sessione
1. Ritarare il prompt per risolvere:
   - bug "#anni" nel campo hashtag
   - LinkedIn fuori contesto (serve tono professionale)
   - visual ripetuti tra piattaforme
   - KPI senza numeri dal brief
   - calendario senza giorno evento / giorno dopo
2. Integrare rss_reader.py in icrawler_simple.py
3. (Futuro) portare iCrawler su Android come app locale

### File principali
- start_icrawler.sh    # launcher
- ui_server.py         # server UI
- ui.html              # pagina web
- icrawler_simple.py   # motore
- gliner_service.py    # microservizio GLiNER
- gliner_client.py     # client HTTP verso GLiNER
- rss_reader.py        # feed RSS (non integrato)
- validator.py         # validazione minimale
- config.py            # OLLAMA_MODEL = llama3.2:3b


## Test con brief "festa compleanno" (8 ottobre, seconda prova)

Brief con placeholder DA DEFINIRE (budget, hashtag, location ecc).
Il modello ha INVENTATO valori plausibili:
- Budget: 1000 euro (il brief non lo specificava)
- Hashtag: #FestaDiCompleanno, #MarcoCanta (inventati)

Questo NON era visibile nel test ElectroBeach perche il brief era
ricco di dati reali.

### Problema rilevato
I placeholder "DA DEFINIRE" vengono passati al modello come se
fossero valori reali. Il modello li interpreta come dati mancanti
e li riempie con valori plausibili invece di lasciarli vuoti.

### Fix necessari
1. In prompt_builder.py: filtrare i valori placeholder
   (DA DEFINIRE, N/A, -, ecc) PRIMA di passarli al prompt
2. In prompts/strategist.txt: aggiungere istruzione esplicita
   "non inventare informazioni mancanti, lascia vuoto"
3. Estendere il calendario per includere giorno evento e giorno +1
   (live coverage, recap)

### Altri problemi (uguali a ElectroBeach)
- LinkedIn usa lo stesso tono di Instagram (fuori contesto)
- Visual ripetuti tra piattaforme
- KPI generici senza numeri

### Nota
Il fix piu importante e il primo (placeholder): previene
allucinazioni su dati mancanti. Gli altri sono rifiniture.

## 15 ottobre - Tre fix completati e testati

Fix 1 (prompt_builder.py): filtro placeholder
Fix 2 (strategist.txt): regole valori mancanti, LinkedIn, visual, calendario
Fix 3 (icrawler_simple.py): parser calendario esteso

Risultati del test:
- Budget DA DEFINIRE ignorato da GLiNER, non inventato dal modello
- Hashtag solo con #, nessuna parola orfana
- Calendario a 4 righe (fix duplicato dopo doppia esecuzione)
- LinkedIn con tono diverso da Instagram

Piccola nota aperta:
- Budget "DA DEFINIRE" nel piano finale non diventa "non specificato".
  Non e un bug del fix, e un comportamento del modello che copia il
  placeholder. Fix da 5 minuti se serve.
