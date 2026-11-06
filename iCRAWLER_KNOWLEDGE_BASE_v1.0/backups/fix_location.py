import re

with open('fact_extractor_enhanced.py', 'r') as f:
    content = f.read()

# Migliora il pattern per location: cattura città con nome composto (es. "a Bologna", "in Roma")
old_location = r'''    location_patterns = [
        r'a\s+([A-Z][a-z]+)(?=\s|\.|,|$|-|,)
        r'in\s+([A-Z][a-z]+)(?=\s|\.|,|$|-|,)'''
    
new_location = '''    location_patterns = [
        r'a\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\s|\.|,|$|-)',
        r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\s|\.|,|$|-)',
        r'location:\s*([^.,;]+)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\s*\.|\s*,|\s*$)'''

# Sostituisci
content = content.replace(old_location, new_location)

# 2. Aggiungi "networking" e "pitch" alla lista objective_keywords
old_keywords = '''objective_keywords = ['attirare', 'promuovere', 'raccogliere', 'formare', 'sensibilizzare', 'creare', 'coinvolgere', 'aggiornamento', 'aggiornare', 'informare', 'fare networking', 'incontrare', 'sviluppare']'''
new_keywords = '''objective_keywords = ['attirare', 'promuovere', 'raccogliere', 'formare', 'sensibilizzare', 'creare', 'coinvolgere', 'aggiornamento', 'aggiornare', 'informare', 'fare networking', 'incontrare', 'sviluppare', 'networking', 'pitch']'''

content = content.replace(old_keywords, new_keywords)

with open('fact_extractor_enhanced.py', 'w') as f:
    f.write(content)

print("✅ Fix applicato: location migliorata, nuove parole chiave aggiunte")
