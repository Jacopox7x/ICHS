"""
Test Validator iCrawler V1.5
"""

from validator import Validator

# Brief di esempio
brief = {
    "data": "15 novembre 2026",
    "luogo": "Centro Congressi, Torino",
    "target": "Marketing manager, imprenditori",
    "hashtag_autorizzati": ["#DigitalMarketing", "#Torino"],
    "budget": None,
    "link": None,
    "kpi": None
}

validator = Validator()

# Test 1: Output valido
print("TEST 1: Output valido")
output_valido = """
ANALISI
- Target: Marketing manager, imprenditori

INSTAGRAM
Hook: ...
Corpo: ...
Hashtag: #DigitalMarketing, #Torino

CALENDARIO
Giorno -2: ...
Giorno -1: ...
"""
result = validator.validate(output_valido, brief)
print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}\n")

# Test 2: Data mancante
print("TEST 2: Data mancante")
output_senza_data = """
ANALISI
- Target: Marketing manager, imprenditori

INSTAGRAM
Hook: ...
Corpo: ...
Hashtag: #DigitalMarketing, #Torino

CALENDARIO
Giorno -2: ...
Giorno -1: ...
"""
result = validator.validate(output_senza_data, brief)
print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}\n")

# Test 3: Hashtag non autorizzato
print("TEST 3: Hashtag non autorizzato")
output_hashtag_inventato = """
ANALISI
- Target: Marketing manager, imprenditori

INSTAGRAM
Hook: ...
Corpo: ...
Hashtag: #FakeHashtag, #DigitalMarketing

CALENDARIO
Giorno -2: ...
Giorno -1: ...
"""
result = validator.validate(output_hashtag_inventato, brief)
print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}\n")

# Test 4: Stories mancanti
print("TEST 4: Stories mancanti")
output_stories_mancanti = """
ANALISI
- Target: Marketing manager, imprenditori

STORIES
Frame 1: ...
Frame 2: ...
"""
result = validator.validate(output_stories_mancanti, brief)
print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}\n")
