# src/giphy_api.py
import requests
import time

class GiphyAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.giphy.com/v1/gifs"
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        self._cache = {}  # Simple cache for responses
        self._cache_duration = 300  # Cache duration in seconds (5 minutes)

    def _rate_limit(self):
        """Implement simple rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def _get_cached_response(self, cache_key):
        """Get a cached response if it exists and is not expired"""
        if cache_key in self._cache:
            timestamp, data = self._cache[cache_key]
            if time.time() - timestamp < self._cache_duration:
                return data
            else:
                del self._cache[cache_key]
        return None

    def _cache_response(self, cache_key, data):
        """Cache a response with the current timestamp"""
        self._cache[cache_key] = (time.time(), data)

    def _extract_gif_urls(self, data, size='fixed_height'):
        """Extract GIF URLs from API response data"""
        gifs = []
        for item in data.get('data', []):
            gif_url = item.get('images', {}).get(size, {}).get('url')
            if gif_url:
                gifs.append(gif_url)
        return gifs

    def search_gifs(self, query, limit=5):
        """Search for GIFs using the GIPHY API"""
        cache_key = f"search_{query}_{limit}"
        cached_result = self._get_cached_response(cache_key)
        if cached_result:
            return cached_result

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
            
            # Extract GIF URLs
            gifs = self._extract_gif_urls(data)
            
            # Cache the results
            self._cache_response(cache_key, gifs)
            
            return gifs
            
        except Exception as e:
            print(f"Error searching for GIFs: {str(e)}")
            return []  # Return empty list instead of failing

    def get_trending_gifs(self, limit=15):
        """Get trending GIFs from GIPHY"""
        cache_key = f"trending_{limit}"
        cached_result = self._get_cached_response(cache_key)
        if cached_result:
            return cached_result

        self._rate_limit()  # Apply rate limiting
        
        try:
            params = {
                'api_key': self.api_key,
                'limit': limit,
                'rating': 'pg'
            }
            
            response = requests.get(f"{self.base_url}/trending", params=params)
            
            # Handle rate limiting response
            if response.status_code == 429:
                print("Rate limited for trending GIFs. Waiting before retry...")
                time.sleep(1)  # Wait for 1 second before retrying
                return []
                
            response.raise_for_status()
            data = response.json()
            
            # Extract GIF URLs
            gifs = self._extract_gif_urls(data)
            
            # Cache the results
            self._cache_response(cache_key, gifs)
            
            return gifs
            
        except Exception as e:
            print(f"Error getting trending GIFs: {str(e)}")
            return []  # Return empty list instead of failing

# Example usage:
if __name__ == "__main__":
    # Replace with your actual Giphy API key
    api_key = "dTQTdmW2kntqOKJ1jFfhatYeSoo3PWe7"
    giphy = GiphyAPI(api_key)
    
    # Test search
    gif_urls = giphy.search_gifs("happy", limit=5)
    print("Search results:", gif_urls)
    
    # Test trending
    trending_urls = giphy.get_trending_gifs(limit=5)
    print("Trending GIFs:", trending_urls)