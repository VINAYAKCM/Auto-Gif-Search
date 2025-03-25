# src/giphy_api.py
import requests

class GiphyAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.giphy.com/v1/gifs"

    def search_gifs(self, query, limit=10):
        """
        Search for GIFs on Giphy using the provided query.
        Returns a list of GIF URLs.
        """
        params = {
            "q": query,
            "api_key": self.api_key,
            "limit": limit,
            "rating": "pg",  # Adjust rating as needed (e.g., "g", "pg-13")
            "lang": "en"
        }
        response = requests.get(f"{self.base_url}/search", params=params, headers={
            "User-Agent": "Mozilla/5.0"
        })
        response.raise_for_status()  # Raise an error if the request failed
        data = response.json()
        gifs = []
        # Extract GIF URLs from the response. Adjust image size as desired.
        for result in data.get("data", []):
            gif_url = result["images"]["fixed_height_small"]["url"]
            gifs.append(gif_url)
        return gifs

# Example usage:
if __name__ == "__main__":
    # Replace with your actual Giphy API key
    api_key = "dTQTdmW2kntqOKJ1jFfhatYeSoo3PWe7"
    giphy = GiphyAPI(api_key)
    gif_urls = giphy.search_gifs("happy", limit=5)
    print("Fetched GIF URLs:", gif_urls)