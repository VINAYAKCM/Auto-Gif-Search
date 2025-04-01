# src/giphy_api.py
import requests
import time

class GiphyAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.giphy.com/v1/gifs"
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests

    def _rate_limit(self):
        """Implement simple rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def search_gifs(self, query, limit=5):
        """Search for GIFs using the GIPHY API"""
        self._rate_limit()  # Apply rate limiting
        
        try:
            params = {
                'api_key': self.api_key,
                'q': query,
                'limit': limit,
                'rating': 'pg',
                'lang': 'en'
            }
            
            response = requests.get(f"{self.base_url}/search", params=params)
            
            # Handle rate limiting response
            if response.status_code == 429:
                print(f"Rate limited for query: {query}. Waiting before retry...")
                time.sleep(1)  # Wait for 1 second before retrying
                return []
                
            response.raise_for_status()
            data = response.json()
            
            # Extract and return only the GIF URLs
            gifs = []
            for item in data.get('data', []):
                gif_url = item.get('images', {}).get('fixed_height', {}).get('url')
                if gif_url:
                    gifs.append(gif_url)
            
            return gifs
            
        except Exception as e:
            print(f"Error searching for GIFs: {str(e)}")
            return []  # Return empty list instead of failing

# Example usage:
if __name__ == "__main__":
    # Replace with your actual Giphy API key
    api_key = "dTQTdmW2kntqOKJ1jFfhatYeSoo3PWe7"
    giphy = GiphyAPI(api_key)
    gif_urls = giphy.search_gifs("happy", limit=5)
    print("Fetched GIF URLs:", gif_urls)