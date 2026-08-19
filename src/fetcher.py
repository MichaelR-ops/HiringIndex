"""Web fetching for HTML career pages."""

import requests
from bs4 import BeautifulSoup


def fetch_career_page(url: str, timeout: int = 10) -> BeautifulSoup:
    """
    Fetch a career page from a URL and return parsed HTML.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        BeautifulSoup object with parsed HTML
        
    Raises:
        requests.RequestException: If request fails
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    
    return BeautifulSoup(response.text, "html.parser")
