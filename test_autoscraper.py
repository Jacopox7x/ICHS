from autoscraper import AutoScraper

def extract_from_url(url, example_title):
    """
    Dato un URL e un titolo di esempio presente nella pagina,
    impara a estrarre tutti i titoli simili.
    """
    scraper = AutoScraper()
    try:
        result = scraper.build(url, wanted_list=[example_title])
        return result
    except Exception as e:
        print(f"Errore su {url}: {e}")
        return []

# Prova su due siti generalisti che conosci
siti = [
    # (url, un titolo di esempio che sai essere nella pagina)
    ("https://www.ansa.it/sito/notizie/tecnologia/tecnologia.shtml", "Intelligenza artificiale"),
    ("https://www.repubblica.it/tecnologia/", "intelligenza artificiale"),
]

for url, esempio in siti:
    print(f"\n=== {url} ===")
    titoli = extract_from_url(url, esempio)
    for t in titoli[:5]:
        print(f"  - {t}")
