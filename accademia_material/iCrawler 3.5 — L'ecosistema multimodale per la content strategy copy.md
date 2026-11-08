bolt I C R A W L E R 3 . 5 · C O N T E N T E N G I N E
iCrawler 3.5
iCrawler 3.5
L'ecosistema multimodale
multimodale per la content
strategy
Dalla locandina all'articolo. In un unico respiro.
v 3 . 5 / / 2 0 2 6
v 3 . 5 / / 2 0 2 6

P R O B L E M A · 0 1 / 0 9
C O N T E N T S T R A T E G Y · G A P A N A L Y S I S
Il caos della Content Strategy
Quattro dolori che rallentano ogni content team oggi.
apps
apps Frammentazione
Troppi tool separati per Social, WordPress e ricerca. Tre
finestre aperte, tre workflow spezzati, tre contesti da
mantenere in sync a mano.
cloud_off
cloud_off Costi
API Cloud sempre più care per l'AI. Ogni chiamata a GPT-4 o
Claude è un costo ricorrente che scala con il volume dei
contenuti prodotti.
schedule
schedule Tempo perso
Il copia-incolla manuale tra PDF, immagini e post. Un brief
passa per 5 strumenti prima di diventare un articolo
pubblicato.
psychology_alt
psychology_alt Allucinazioni
L'AI inventa dati se non controllata. Senza fonte verificata,
ogni fatto generato è un rischio per la credibilità del brand.
0 2 / 0 9
I C R A W L E R 3 . 5

S O L U Z I O N E · 0 2 / 0 9
Un unico ecosistema. Locale.
iCrawler non è un generatore — è un Content Engine. Un sistema che
orchestrà parsing, estrazione, generazione e formattazione in un'unica
pipeline controllata.
Privacy e Zero costi API — gira interamente sul tuo Mac via Ollama.
Nessun dato lascia la macchina, nessun abbonamento cloud da pagare.
Multimodale — legge le immagini (OCR) e scrive testi. Capisce una
locandina, estrae titoli e dati, e li trasforma in articolo.
Dual Output — un solo brief, due formati: articolo WordPress strutturato e
piano social pronto.
5 MB
5 MB
peso app Tauri
0 €
0 €
costi API mensili
2 in 1
2 in 1
formato WP + Social
0 3 / 0 9
I C R A W L E R 3 . 5

03
P I P E L I N E · 0 3 / 0 9
/ / F L O W
Dal Brief al Piano in 3 Passi
Tre stadi, un unico flusso di dati — dal input grezzo al output pronto alla pubblicazione.
image
image
0 1 · I N P U T
Immagine o Testo
Qwen Vision OCR legge la locandina, lo
screenshot o il PDF. Estrae testo visivo,
layout e contesto spaziale.
→
memory
memory
0 2 · E L A B O R A Z I O N E
Entità + Prompt + Limiti
GLiNER identifica le entità chiave. Il
Prompt Builder assembla il brief
strutturato. Gli Execution Limits
mantengono l'AI nel corridoio dei fatti.
→
description
description
0 3 · O U T P U T
Articolo + Piano Social
Articolo WordPress strutturato (titolo,
paragrafi, tag) + piano social per
Instagram, LinkedIn, X, Facebook e
TikTok.
0 4 / 0 9
I C R A W L E R 3 . 5

04
A R C H I T E T T U R A · 0 4 / 0 9
/ / S T R U C T U R E
Progettato per durare
Tre decisioni architetturali che tengono il sistema solido quando scala.
folder_open
folder_open
folder_open
P I L A S T R O 0 1
P I L A S T R O 0 1
Multi-Tenant
Sandbox isolate per ogni cliente. COSPER,
Creazioni Migranti e gli altri brand hanno
dati, prompt e storico separati. Nessuna
contaminazione cross-tenant, nessuna fuga
di contesto tra progetti.
›
sandbox / isolate
record_voice_over
record_voice_over
record_voice_over
P I L A S T R O 0 2
P I L A S T R O 0 2
Tone of Voice
Un file di testo per dettare la personalità del
brand all'AI. Il ToV è una persona scrivibile,
non un prompt gigante: cambia il file,
cambia la voce di tutti gli output generati.
›
persona / brand
bolt
bolt
bolt
P I L A S T R O 0 3
P I L A S T R O 0 3
Dual Output
Genera l'articolo profondo e i post
promozionali insieme. Una sola esecuzione
del modello produce due formati con toni
diversi, ottimizzati per canale e audience.
›
article + social
0 5 / 0 9
I C R A W L E R 3 . 5

05
H A R D W A R E · 0 5 / 0 9
/ / M A C H I N E
Potenza da Workstation su
un Mac da 8 GB
Come fai stare un Content Engine AI su un MacBook Air senza farlo esplodere.
5 MB
5 MB
5 MB
peso app Tauri
/ / A P P
inventory_2
8 GB
8 GB
8 GB
RAM del Mac target
/ / R A M
memory
0
server necessari
/ / N O D E
dns_off
Tauri (Rust) — l'app desktop pesa solo 5 MB (Electron ne pesa 150). Il binario è nativo, il
footprint di memoria è dieci volte inferiore.
Gestione Sequenziale della RAM — i modelli (Vision e Testo) si passano il testimone e
si scaricano subito, con keep_alive=0. Nessun modello resta in memoria quando non serve.
Zero Server — architettura Edge Computing spinta al limite. Il Mac è il server, il client, il
nodo AI. Tutto in uno.
0 6 / 0 9
I C R A W L E R 3 . 5

0 7 / 0 9 · R O A D M A P
timeline R O A D M A P · 0 6 / 0 9
iCrawler diventa senziente (quasi)
Tre direzioni di sviluppo attive per la prossima major release.
N E X T R E L E A S E
N O D E 0 1 · A G E N T
Agent Reach (WeKnora)
L'AI non aspetta il brief, ma va a cercare i dati sul web e nei documenti aziendali. Il agente attiva ricerche autonome, raccoglie fonti, le filtra per
rilevanza e le porta nella pipeline di generazione.
travel_explore
travel_explore
Q 2 2 0 2 6
N O D E 0 2 · T R E N D S
Hashtag Live
Recupero dei trend in tempo reale per i post social. Il sistema pinga le API di Instagram, TikTok e X, estrae gli hashtag emergenti e li propone nel
piano social — sempre con fonte e volume di trending.
trending_up
trending_up
Q 3 2 0 2 6
N O D E 0 3 · P A T T E R N S
Pattern Strategici
Estrazione e ricombinazione di strutture narrative vincenti. Il Content Engine impara dai contenuti ad alta performance del cliente e genera nuovi
articoli usando gli stessi schemi retorici.
hub
hub
0 7 / 0 9 · F U T U R O
I C R A W L E R 3 . 5

0 8 / 0 9 · F I L O S O F I A
visibility F I L O S O F I A · 0 7 / 0 9
L'occhio che osserva, la mente che interpreta
⟁Eidolopoiesis — la costruzione del simbolo da parte della macchina.
visibility
visibility
hub
hub
gavel
gavel
L 1 / L 2
O S S E R VA Z I O N E
Il Parser estrae solo dati visivi, senza giudizio.
Pixel, linee, forme, testo riconosciuto. Nessuna interpretazione, nessuna ipotesi. Solo la materia prima del visibile.
L 3
I N T E R PR E TA Z I O N E
Il Tessitore crea relazioni e archetipi.
Collega entità, inferisce contesto, riconosce pattern narrativi. Trasforma dati grezzi in strutture di significato.
J U D G E
B A R R I E R A E T I CA
Una barriera che impedisce all'AI di spacciare ipotesi per fatti.
Ogni claim generato passa per un validity check. Se non ha fonte, non viene pubblicato come fatto — resta ipotesi
etichettata.
"La macchina non produce solo contenuti, ma 
La macchina non produce solo contenuti, ma densità simbolica
densità simbolica."
0 8 / 0 9 · E I D O L O P O I E S I S
I C R A W L E R 3 . 5

flag C H I U S U R A · 0 9 / 0 9
Pronti a riscrivere le
Pronti a riscrivere le
Pronti a riscrivere le
Pronti a riscrivere le
regole
regole
regole
regole?
Grazie per l'attenzione.

