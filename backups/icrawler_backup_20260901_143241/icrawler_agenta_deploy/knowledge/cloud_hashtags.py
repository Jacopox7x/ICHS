import requests

def get_hashtags_from_cloud(topic, count=10):
    try:
        url = "https://api.ritekit.com/v1/stats/hashtag-suggestions"
        params = {"text": topic}
        response = requests.get(url, params=params, timeout=3)
        if response.status_code == 200:
            data = response.json()
            hashtags = []
            for item in data.get('data', []):
                if 'hashtag' in item:
                    hashtags.append(item['hashtag'])
            if hashtags:
                return hashtags[:count]
    except:
        pass
    
    base = topic.replace(" ", "").lower()
    return [
        f"#{base}", f"#{base}2026", f"#{base}Event",
        f"#{base}Community", f"#{base}Innovation",
        f"#{base}Life", f"#{base}Daily", f"#{base}World",
        f"#{base}Experience", f"#{base}Vibes"
    ][:count]

if __name__ == "__main__":
    print("Test AI summit:", get_hashtags_from_cloud("AI summit"))
    print("Test capodanno:", get_hashtags_from_cloud("capodanno"))
