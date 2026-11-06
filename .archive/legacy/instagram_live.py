from apify_client import ApifyClient
import os

class InstagramLive:
    def __init__(self):
        self.client = ApifyClient(os.getenv("APIFY_TOKEN"))

    def get_hashtag_posts(self, hashtag: str, limit: int = 10) -> list:
        """Recupera post reali da Instagram"""
        run_input = {
            "hashtags": [hashtag],
            "resultsLimit": limit,
        }
        run = self.client.actor("apify/instagram-hashtag-scraper").call(run_input=run_input)
        return [item for item in self.client.dataset(run["defaultDatasetId"]).iterate_items()]
