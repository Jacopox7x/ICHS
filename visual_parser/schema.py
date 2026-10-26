from pydantic import BaseModel, Field
from typing import List

class EntitaVisiva(BaseModel):
    tipo: str = Field(description="Cosa è (es. persona, sedia, finestra)")
    quantita: int = Field(default=1, description="Quante ce ne sono")
    posizione: str = Field(description="Dove si trova (es. centro, sfondo, destra)")
    certezza: str = Field(description="alta, media, bassa")

class AttributoVisivo(BaseModel):
    categoria: str = Field(description="es. colore, texture, materiale")
    valore: str = Field(description="es. rosso scuro, ruvido, metallo")

class OsservazioneL1_L2(BaseModel):
    """
    Output vincolante del Parser Visivo.
    Solo misura (L1) e classificazione (L2). Nessuna inferenza (L3).
    """
    descrizione_generica: str = Field(description="Cosa si vede in generale, in modo puramente denotativo.")
    entita: List[EntitaVisiva] = Field(description="Oggetti e soggetti visibili")
    attributi: List[AttributoVisivo] = Field(description="Colori, texture, materiali visibili")
    testo_visibile: str = Field(default="", description="Eventuale testo presente nell'immagine (OCR)")
    
    # Il vincolo epistemologico: il Parser deve dichiarare i propri limiti
    non_inferences: List[str] = Field(
        description="Lista obbligatoria di cose che NON si possono dedurre dall'immagine (es. 'Non posso sapere il nome della persona', 'Non posso dedurre il significato simbolico del colore')."
    )
