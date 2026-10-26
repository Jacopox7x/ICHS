# iCrawler 3.5 — Istruzioni di avvio

**Data**: 15 ottobre 2026
**Stato**: prototipo funzionante, uso personale
**Destinazione**: app desktop (Tauri), poi mobile (Android)

---

## Cosa fa iCrawler

Trasforma un brief in linguaggio naturale in un piano social strutturato
(Instagram, LinkedIn, X, Facebook, TikTok, Stories, Calendario, KPI).

Pipeline:
    brief → GLiNER (entità) → prompt_builder → Ollama → JSON → Validator → piano

Il valore aggiunto rispetto a un chatbot generico:
- estrae entità dichiarate (non le inventa)
- ignora i placeholder (`DA DEFINIRE` non diventa "1000 euro")
- verifica che il piano contenga le entità estratte
- rispetta regole specifiche per piattaforma

---

## Prerequisiti

Tutto già installato. Verifica solo che esistano:

1. **Python 3.12** con il venv creato
2. **Ollama** installato con modello `llama3.2:3b`
3. **Modello GLiNER** `urchade/gliner_multi-v2.1` in cache (2.3 GB)
4. **Token HuggingFace** configurato (non necessario per l'avvio, serve solo per download)

---

## Verifica prima di iniziare (opzionale, 30 secondi)

Apri un terminale e lancia:

    cd ~/Documents/ICHS && source venv/bin/activate && python3 --version

Ti aspetti `Python 3.12.15`.

    which python3

Ti aspetti `/Users/jacopogalati/Documents/ICHS/venv/bin/python3`.

Se uno dei due controlli fallisce, il venv non è a posto. Vedi "Problemi comuni" in fondo.

---

## Avvio rapido (la via normale)

Apri **un solo terminale** e lancia:

    icrawler

L'alias esiste già in `~/.zshrc`. Fa tutto:
1. Entra in `~/Documents/ICHS`, attiva il venv
2. Controlla se Ollama è attivo; se no, lo avvia in background
3. Controlla se GLiNER è attivo; se no, lo avvia e aspetta che sia pronto
4. Avvia il server UI
5. Apre il browser su `http://127.0.0.1:8080`

Aspetta 10-15 secondi (il modello GLiNER deve caricarsi in memoria).
Quando vedi `[3/3] Avvio server UI...` e il browser si apre, sei pronto.

Per usare il browser manualmente: `http://127.0.0.1:8080`

---

## Avvio manuale (per debug)

Se l'alias non funziona o vuoi vedere i log di ogni servizio, servono
**tre terminali separati**.

### Terminale 1 — Ollama

    ollama serve

Ti aspetti:

    time=... level=INFO msg="Listening on 127.0.0.1:11434"

Lascia il terminale aperto.

### Terminale 2 — Microservizio GLiNER

    cd ~/Documents/ICHS && source venv/bin/activate
    uvicorn gliner_service:app --host 127.0.0.1 --port 8000

Ti aspetti:

    2026-... [INFO] Caricando modello urchade/gliner_multi-v2.1 ...
    2026-... [INFO] Modello caricato e pronto.
    INFO:     Uvicorn running on http://127.0.0.1:8000

Il caricamento richiede 5-15 secondi. Lascia il terminale aperto.

### Terminale 3 — UI server

    cd ~/Documents/ICHS && source venv/bin/activate
    uvicorn ui_server:app --host 127.0.0.1 --port 8080

Ti aspetti:

    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:8080

Apri il browser su `http://127.0.0.1:8080`.

---

## Uso della UI

### Generare un piano

1. Incolla il brief nel campo di testo
2. (Opzionale) Clicca **"Anteprima entità"** per vedere cosa GLiNER ha capito
3. Clicca **"Genera piano"**
4. Aspetta 30-60 secondi
5. Il piano appare sotto, e viene salvato automaticamente in
   `output_plan_*.txt`

### Pulsanti disponibili

- **Carica esempio** — riempie il brief con un esempio funzionante
- **Svuota** — pulisce i campi
- **Anteprima entità** — mostra le entità estratte prima di generare
- **Genera piano** — genera il piano completo
- **Rigenera** — riprova con lo stesso brief (utile se il primo tentativo è deludente)
- **Copia** — copia il piano negli appunti
- **Scarica .md** — scarica il piano come file markdown
- **Storico piani generati** (in fondo) — lista degli ultimi 20 piani salvati

### Formato del brief

Due modalità, entrambe supportate:

**Formato strutturato** (consigliato per dati precisi):

    event_name: Tech Summit 2026
    date: 15 marzo
    location: Milano
    target: startup e investitori fintech
    objective: promuovere l'evento
    budget: 50000 euro
    hashtag: #TechSummit26

**Formato libero** (il modello deduce le entità dal testo):

    Tech Summit 2026 si terrà a Milano il 15 marzo. L'evento è
    dedicato a startup e investitori del settore fintech.

Per i campi che non conosci ancora, scrivi `DA DEFINIRE`. Il sistema
li ignora e non inventa valori.

---

## Spegnimento

### Con l'avvio rapido (`icrawler`)

Premi `Ctrl+C` nel terminale dove è in esecuzione. Questo ferma la UI
e il microservizio GLiNER. Ollama resta attivo (non fa danno).

### Con l'avvio manuale (tre terminali)

In ciascun terminale, premi `Ctrl+C`.

### Fermare tutto da un solo comando

    pkill -f uvicorn    # ferma GLiNER e UI server
    pkill ollama        # ferma Ollama (opzionale)

---

## Verifica che tutto sia attivo

In qualsiasi momento, tre comandi rapidi:

    curl -s http://127.0.0.1:8000/health
    # atteso: {"status":"ok","model_loaded":true,...}

    curl -s http://127.0.0.1:11434/api/tags | head -c 100
    # atteso: JSON con la lista dei modelli

    curl -s http://127.0.0.1:8080/health
    # atteso: {"status":"ok","gliner_alive":true}

Se uno dei tre non risponde, il servizio corrispondente è spento.

---

## Problemi comuni

### "ModuleNotFoundError" all'avvio

Il venv non è attivo. Lancia:

    cd ~/Documents/ICHS && source venv/bin/activate

Il prompt deve mostrare `(venv)` all'inizio. Se non lo mostra, il venv
non si è attivato.

### "Connection refused" sulla porta 8000

Il microservizio GLiNER non è attivo. Avvialo nel Terminale 2.

### "model 'llama3.2:3b' not found"

Ollama non ha il modello. Scaricalo:

    ollama pull llama3.2:3b

### "Out of host capacity" (non applicabile, solo per Oracle Cloud)

Non riguarda questa configurazione locale.

### La UI si apre ma "Genera piano" non risponde

Controlla la console del browser (tasto destro → Ispeziona → Console).
Gli errori comuni:
- `Failed to fetch` → il server UI è spento
- `500 Internal Server Error` → guarda i log del server UI (Terminale 3)

### Il piano viene generato ma il budget è inventato

Controlla che il brief contenga il budget o `DA DEFINIRE`. Se contiene
un valore, il modello lo userà. Se contiene `DA DEFINIRE`, dovrebbe
essere ignorato.

### Il piano è lento (> 90 secondi)

Normale con llama3.2:3b su MacBook Air. Per accelerare:
- chiudi Chrome con molte tab aperte (occupa RAM)
- chiudi VS Code
- il Mac ha 8 GB di RAM, il sistema ne usa già 2-3

---

## Struttura dei file

    ~/Documents/ICHS/
    ├── icrawler_simple.py       entrypoint CLI
    ├── ui_server.py             server UI (FastAPI)
    ├── ui.html                  interfaccia web
    ├── gliner_service.py        microservizio GLiNER
    ├── gliner_client.py         client HTTP verso GLiNER
    ├── prompt_builder.py        costruisce il prompt
    ├── validator.py             verifica il piano
    ├── config.py                configurazione (modello, host)
    ├── rss_reader.py            lettore RSS (non integrato)
    ├── start_icrawler.sh        launcher automatico
    ├── requirements.txt         dipendenze del venv
    ├── prompts/
    │   └── strategist.txt       template del prompt
    ├── docs/
    │   ├── AVVIO.md             questo file
    │   ├── GLOSSARIO.md         vocabolario condiviso
    │   ├── eidolopoiesis_spec_v0.1.md
    │   └── visual_parser_spec_v0.1.md
    ├── context/                 decisioni architetturali
    ├── output_plan_*.txt        piani generati
    └── venv/                    ambiente Python (non esportabile)

---

## Configurazione

Tutto in `config.py`:

    OLLAMA_MODEL = "llama3.2:3b"
    OLLAMA_HOST = "http://localhost:11434"
    PROMPT_DIR = "prompts"
    MAX_TOKENS = 4096
    TEMPERATURE = 0.2

Per cambiare modello: modifica `OLLAMA_MODEL` e riavvia il server UI.
Se il modello non è scaricato, `ollama pull <nome>` prima.

---

## Versioning

- **v3.5** (15 ottobre 2026): core completo, UI web funzionante,
  tre fix applicati (placeholder, LinkedIn, calendario). Uso personale.
- **v4.0** (obiettivo: entro dicembre 2026): app desktop con Tauri,
  bundle singolo, avvio con doppio click.
- **v5.0** (data da definire): app mobile (Android o Flutter).

---

## Note

- Il sistema consuma ~6 GB di RAM con tutti e tre i servizi attivi.
  Su MacBook Air 8 GB è al limite: chiudi le altre applicazioni pesanti.
- I piani generati si accumulano in `output_plan_*.txt`. Spostali
  periodicamente in `outputs_storici/` per tenere la cartella pulita.
- Il modello GLiNER (2.3 GB) è in `~/.cache/huggingface/`. Non va
  cancellato a meno che tu non voglia riscaricarlo.
- Ollama e i suoi modelli sono in `~/.ollama/`. Stesso discorso.

