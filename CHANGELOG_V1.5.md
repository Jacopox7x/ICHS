# iCRAWLER V1.5
## Changelog - 16 agosto 2026

## OBIETTIVO

Evoluzione di iCrawler da generatore basato esclusivamente su LLM a sistema
con generazione, gestione dati e validazione automatica dell'output.

---

## 1. PROMPT STRATEGIST

File:
`prompts/strategist.txt`

Stato:
✅ Blindato

Funzioni principali:
- Utilizzo esclusivo delle informazioni presenti nel brief
- Divieto di inventare dati
- Controllo rigoroso degli hashtag autorizzati
- Gestione esplicita dell'assenza di budget
- Gestione esplicita dell'assenza di KPI
- Gestione dell'assenza di link
- Struttura obbligatoria dell'output
- 5 Stories obbligatorie
- 2 teaser obbligatori
- Thread X di almeno 5 tweet
- Controllo finale dei dati

Il prompt è stato trasformato da semplice istruzione creativa
a layer di controllo del modello.

---

## 2. HASHTAG CLOUD

File:
`hashtag_cloud.py`

Stato:
🟡 Implementato, test cloud da completare

Architettura:

Brief
  ↓
Hashtag autorizzati
  ↓
Cloud JSON
  ↓
Fallback locale
  ↓
Nessun hashtag autorizzato

Funzioni:
- Recupero hashtag da JSON remoto
- Fallback locale
- Categorie tematiche
- Gestione errore di connessione
- Cache della risposta cloud
- Fallback automatico

Categorie attualmente previste:
- food
- tech
- cultura
- sport
- moda
- musica
- beneficenza
- business
- networking
- default

---

## 3. VALIDATOR

File:
`validator.py`

Stato:
✅ Implementato

Versione:
V1.5

Controlli attivi:

- Data
- Luogo
- Target
- Hashtag
- Struttura
- Stories
- Teaser
- Budget
- Link
- KPI
- Qualità minima
- Contaminazione
- Nome evento

Il validator non genera contenuti.

Il validator verifica l'output prodotto dal modello.

Architettura:

BRIEF
  ↓
PROMPT BUILDER
  ↓
LLM
  ↓
OUTPUT
  ↓
VALIDATOR
  ↓
VALID / INVALID

---

## 4. PRINCIPIO ARCHITETTURALE

iCrawler non si affida più esclusivamente al modello.

Il sistema utilizza tre livelli:

1. Istruzioni
2. Generazione
3. Validazione

La responsabilità viene quindi separata:

LLM:
generazione del contenuto

Python:
controllo delle regole

Questo riduce il rischio di:
- allucinazioni
- dati inventati
- hashtag non autorizzati
- link inventati
- budget inventati
- KPI inventati
- contaminazione da informazioni esterne al brief

---

## 5. TEST

Test effettuati durante lo sviluppo:

- Brief normali
- Brief senza hashtag
- Brief senza budget
- Brief senza link
- Brief senza KPI
- Hashtag inventati
- Date errate
- Luoghi alterati
- Target alterati
- Link inventati
- Output contaminati
- Output autoreferenziali
- Struttura incompleta

Il validator è stato corretto sulla base degli errori emersi durante i test.

---

## 6. FILE PRINCIPALI

ICHS/

├── hashtag_cloud.py
├── validator.py
├── prompt_builder.py
├── icrawler_simple.py
└── prompts/
    └── strategist.txt

---

## 7. STATO DEL PROGETTO

| Componente | Stato |
|------------|-------|
| Strategist prompt | ✅ |
| Regole anti-allucinazione | ✅ |
| Hashtag fallback | ✅ |
| Hashtag cloud | 🟡 |
| Validator | ✅ |
| Controllo struttura | ✅ |
| Controllo hashtag | ✅ |
| Controllo dati | ✅ |
| Controllo budget | ✅ |
| Controllo link | ✅ |
| Controllo KPI | ✅ |
| Test adversarial | 🟡 |
| Test end-to-end | 🟡 |
| OCR | ⏳ |
| Analisi visuale | ⏳ |
| APK Android | ⏳ |
| Multilingua | ⏳ |

---

## 8. PROSSIMO STEP

Non aggiungere nuove funzionalità prima di aver completato:

1. Test reale hashtag cloud
2. Test fallback cloud offline
3. Test end-to-end
4. Batteria adversarial
5. Misurazione false positive
6. Misurazione false negative

Solo successivamente procedere con nuove funzionalità.

---

## VERSIONE

iCrawler V1.5

Stato:
VALIDATOR IMPLEMENTATO

Data:
16 agosto 2026
