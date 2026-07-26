# google_search.py
"""
Google Search integration for Atlas
Performs web searches using Google Custom Search API
"""

import os
import requests
import json

class GoogleSearch:
    def __init__(self, api_key=None, search_engine_id=None):
        """Initialize Google Search with API credentials"""
        self.api_key = api_key or self.load_api_key()
        self.search_engine_id = search_engine_id or self.load_search_engine_id()
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def load_api_key(self):
        """Load Google Search API key from config file"""
        config_file = os.path.join('materials', 'api_keys.txt')
        try:
            with open(config_file, 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_SEARCH_API_KEY='):
                        return line.split('=', 1)[1].strip()
        except Exception as e:
            print(f"[GoogleSearch] Error loading API key: {e}")
        return None
    
    def load_search_engine_id(self):
        """Load Google Search Engine ID from config file"""
        config_file = os.path.join('materials', 'api_keys.txt')
        try:
            with open(config_file, 'r') as f:
                for line in f:
                    if line.startswith('SEARCH_ENGINE_ID='):
                        return line.split('=', 1)[1].strip()
        except Exception as e:
            print(f"[GoogleSearch] Error loading Search Engine ID: {e}")
        return None
    
    def search(self, query, num_results=5):
        """
        Perform a Google search
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return (max 10)
        
        Returns:
            list: List of search results with title, link, and snippet
        """
        if not self.api_key or not self.search_engine_id:
            print("[GoogleSearch] API credentials not configured")
            return []
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)
            }
            
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                if 'items' in data:
                    for item in data['items']:
                        results.append({
                            'title': item.get('title', ''),
                            'link': item.get('link', ''),
                            'snippet': item.get('snippet', '')
                        })
                
                print(f"[GoogleSearch] Found {len(results)} results for: {query}")
                return results
            else:
                print(f"[GoogleSearch] Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[GoogleSearch] Search error: {e}")
            return []
    
    def search_and_summarize(self, query, num_results=3):
        """
        Search and return a formatted summary
        
        Args:
            query (str): Search query
            num_results (int): Number of results
        
        Returns:
            str: Formatted summary of search results
        """
        results = self.search(query, num_results)
        
        if not results:
            return f"No results found for: {query}"
        
        summary = f"Search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['title']}\n"
            summary += f"   {result['snippet']}\n"
            summary += f"   Link: {result['link']}\n\n"
        
        return summary.strip()


# Test function
if __name__ == "__main__":
    search = GoogleSearch()
    results = search.search_and_summarize("Python programming", num_results=3)
    print(results)
