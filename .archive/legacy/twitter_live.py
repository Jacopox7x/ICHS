import os
from serpapi import GoogleSearch
from typing import List

class TwitterLive:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")

    def get_tweets(self, topic: str, limit: int = 5) -> List[str]:
        params = {
            "engine": "twitter",
            "q": topic,
            "api_key": self.api_key
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        tweets = []
        for tweet in results.get("tweets", [])[:limit]:
            tweets.append(tweet.get("text", ""))
        return tweets
