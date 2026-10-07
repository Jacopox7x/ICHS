from validator import Validator

brief = {
    "data": "5 settembre 2026",
    "luogo": "Parco Sempione, Milano",
    "target": "Adulti 25-55 anni, amanti del benessere",
    "hashtag_autorizzati": [],  # Nessun hashtag autorizzato
    "budget": None,
    "link": None,
    "kpi": None
}

output = """
### INSTAGRAM
**Hook:** Abbraccia la pace e il benessere del tuo interno attraverso l'arte della meditazione yoga. #YogaNelParcoMilano
**Corpo:** Scopri un nuovo percorso di rilassamento nel cuore verdeggiante dello Sempione Park, Milano. Traccia la tua strada verso il benessere e una mente più chiara con i nostri sessioni yoga curate speciale del 5 settembre 2026. #YogaMilano
**Hashtag:** #YogaMilano, #BenessereNelParco, #Meditazione5Settembre2026
"""

validator = Validator()
result = validator.validate(output, brief)

print("=" * 60)
print("🧪 VALIDAZIONE YOGA")
print("=" * 60)
print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}")
print("=" * 60)
