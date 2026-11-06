from modules.search_agent import get_live_insights

facts = {
    'event_name': 'Fiera di Santa Maria a Crema',
    'location': 'Crema',
    'topic': 'fiera religiosa',
    'date': 'Marzo-Aprile 2026',
    'objective': 'attrarre devoti e creare divertimento'
}

insights = get_live_insights(facts)
print("🏷️ HASHTAG TRENDING:", insights.get('trending_hashtags'))
print("📰 NOTIZIE:")
for n in insights.get('news', []):
    print(f"  - {n['title']}")
print("🔑 KEYWORDS:", insights.get('keywords'))
print("🏟️ EVENTI CORRELATI:", insights.get('related_events'))
