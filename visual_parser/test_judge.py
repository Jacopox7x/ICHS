from visual_parser.schema import OsservazioneL1_L2, EntitaVisiva, AttributoVisivo
from visual_parser.judge import verifica_epistemica

# CASO 1: Un bravo Parser (L1/L2)
osservazione_buona = OsservazioneL1_L2(
    descrizione_generica="Un uomo al centro di uno stadio con altre persone sullo sfondo.",
    entita=[
        EntitaVisiva(tipo="uomo", quantita=1, posizione="centro", certezza="alta"),
        EntitaVisiva(tipo="persone", quantita=10, posizione="sfondo", certezza="media")
    ],
    attributi=[
        AttributoVisivo(categoria="colore", valore="giacca scura"),
        AttributoVisivo(categoria="materiale", valore="prato erboso")
    ],
    non_inferences=[
        "Non posso sapere il nome della persona.",
        "Non posso dedurre lo status sociale dall'abbigliamento."
    ]
)

# CASO 2: Un Parser che sconfina (fa il Tessitore)
osservazione_cattiva = OsservazioneL1_L2(
    descrizione_generica="Un uomo importante al centro di uno stadio.",
    entita=[
        EntitaVisiva(tipo="leader", quantita=1, posizione="centro", certezza="alta") # Inferenza!
    ],
    attributi=[
        AttributoVisivo(categoria="colore", valore="giacca scura che rappresenta il potere") # Inferenza!
    ],
    non_inferences=[] # Violazione!
)

print("--- TEST 1: PARSER BUONO ---")
valido, errori = verifica_epistemica(osservazione_buona)
print(f"Approvato: {valido}")
for e in errori: print(f"  - {e}")

print("\n--- TEST 2: PARSER CATTIVO ---")
valido, errori = verifica_epistemica(osservazione_cattiva)
print(f"Approvato: {valido}")
for e in errori: print(f"  - {e}")
