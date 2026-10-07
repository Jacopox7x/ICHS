"""Test inspiration_research sul brief Sapori dal Mondo"""
from inspiration_research import InspirationResearch

research = InspirationResearch()

print("=" * 70)
print("RICERCA ISPIRAZIONE — 'Sapori dal Mondo'")
print("=" * 70)

# TEST 1: Cooperative che fanno cene solidali
print("\n" + "─" * 70)
print("RICERCA 1: Cooperative con cene solidali multiculturali")
print("─" * 70)
result = research.find_viral_events("cena solidale multiculturale migranti")
print(f"Trovati {len(result['examples'])} esempi")
print(f"Formati: {result['formati_suggeriti']}")
for i, r in enumerate(result['examples'][:5], 1):
    print(f"\n[{i}] {r['title'][:80]}")
    print(f"    {r['url']}")

# TEST 2: Hashtag locali Cremona
print("\n" + "─" * 70)
print("RICERCA 2: Hashtag locali Cremona + eventi/cultura")
print("─" * 70)
result = research.find_local_hashtags("cremona", "eventi cultura")
print(f"Hashtag locali: {result['hashtags_locali']}")
print(f"Altri hashtag: {result['hashtags_altri'][:10]}")

# TEST 3: Cooperative simili a CreAzioni Migranti
print("\n" + "─" * 70)
print("RICERCA 3: Cooperative con progetti su donne migranti")
print("─" * 70)
result = research.find_similar_coops("donne migranti laboratori italiano", location="italia")
print(f"Trovate {len(result['results'])} cooperative")
print(f"Hashtag menzionati: {result['hashtags_trovati']}")
for i, r in enumerate(result['results'][:5], 1):
    print(f"\n[{i}] {r['title'][:80]}")
    print(f"    {r['url']}")

# TEST 4: Analisi competitor specifico
print("\n" + "─" * 70)
print("RICERCA 4: Come comunicano altre coop simili")
print("─" * 70)
result = research.analyze_coop_social("CreAzioni Migranti")
print(f"Platforms: {result['platforms']}")
print(f"Hashtag trovati: {result['hashtags']}")
print(f"Fonti: {len(result['results'])}")

print("\n" + "=" * 70)
