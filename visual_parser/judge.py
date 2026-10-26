import re
from visual_parser.schema import OsservazioneL1_L2

# Parole che indicano un'inferenza (L3) e che non dovrebbero stare nel Parser (L1/L2)
PAROLE_VIETATE_L3 = [
    "simbolo", "significa", "rappresenta", "archetipo", 
    "sembra", "potrebbe", "probabilmente", "vuole dire", 
    "potere", "status", "emozione", "sentimento"
]

def verifica_epistemica(osservazione: OsservazioneL1_L2) -> tuple[bool, list[str]]:
    """
    Controlla che il Parser non abbia sconfinato nell'interpretazione (L3).
    Ritorna (True, []) se valido, (False, [errori]) se il Judge lo boccia.
    """
    errori = []
    
    # 1. Controllo campo obbligatorio non_inferences
    if not osservazione.non_inferences or len(osservazione.non_inferences) == 0:
        errori.append("VIOLAZIONE: Il campo 'non_inferences' è vuoto. Il Parser deve dichiarare i propri limiti.")
        
    # 2. Controllo parole inferenziali nei campi L1/L2
    testo_da_controllare = (osservazione.descrizione_generica + " " + 
                            " ".join([e.tipo for e in osservazione.entita]) + " " + 
                            " ".join([a.valore for a in osservazione.attributi])).lower()
                            
    for parola in PAROLE_VIETATE_L3:
        if re.search(r'\b' + parola + r'\b', testo_da_controllare):
            errori.append(f"VIOLAZIONE: Trovata parola inferenziale '{parola}'. Il Parser deve solo osservare.")
            
    return len(errori) == 0, errori


# Parole che indicano un'istruzione a fare inferenze (L3) nel prompt
PAROLE_INFERENZA_PROMPT = [
    "correggi", "deduci", "interpreta", "ipotizza", 
    "significato", "archetipo", "sembra", "probabilmente"
]

def verifica_prompt(prompt: str) -> tuple[bool, list[str]]:
    """
    Controlla che il prompt non contenga istruzioni che forzano 
    il modello a sconfinare nell'inferenza (L3).
    """
    errori = []
    prompt_lower = prompt.lower()
    
    for parola in PAROLE_INFERENZA_PROMPT:
        if parola in prompt_lower:
            errori.append(f"VIOLAZIONE PROMPT: La parola '{parola}' induce il modello a dedurre.")
            
    return len(errori) == 0, errori
