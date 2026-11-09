FROM phi3.5

# Aumenta la finestra di contesto per gestire testi più lunghi
PARAMETER num_ctx 8192

# Aumenta la penalità per le ripetizioni (default 1.1, alziamo a 1.3)
PARAMETER repeat_penalty 1.3

# Amplia la finestra di controllo delle ripetizioni (default 64, alziamo a 512)
PARAMETER repeat_last_n 512

# Limita il numero massimo di token generati per prevenire loop infiniti
PARAMETER num_predict 4096