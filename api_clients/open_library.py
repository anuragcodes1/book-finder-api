"""Open Library API client."""

import requests
from typing import Optional
from models.book import Book


class OpenLibraryClient:
    """Client for interacting with the Open Library API."""
    
    BASE_URL = "https://openlibrary.org"
    SEARCH_URL = f"{BASE_URL}/search.json"
    
    def get_books_by_author(self, author_name: str) -> list[Book]:
        """
        Fetch books by author from Open Library.
        
        Args:
            author_name: The name of the author
            
        Returns:
            List of Book objects
        """
        try:
            params = {
                "author": author_name,
                "limit": 100
            }
            
            response = requests.get(self.SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_response(data)
        
        except requests.RequestException as e:
            print(f"Error fetching from Open Library: {e}")
            return []
    
    def _parse_response(self, data: dict) -> list[Book]:
        """Parse Open Library API response into Book objects."""
        books = []
        
        for doc in data.get("docs", []):
            title = doc.get("title")
            if not title:
                continue
            
            # Get the first published year
            published_year = self._extract_year(doc)
            
            # Construct URL using the key
            key = doc.get("key", "")
            url = f"{self.BASE_URL}{key}" if key else self.BASE_URL
            
            books.append(Book(
                title=title,
                published_year=published_year,
                url=url,
                source="open_library"
            ))
        
        return books
    
    def _extract_year(self, doc: dict) -> Optional[int]:
        """Extract publication year from document."""
        # Try first_publish_year
        year = doc.get("first_publish_year")
        if year:
            return int(year)
        
        # Try publish_year list
        publish_years = doc.get("publish_year", [])
        if publish_years:
            try:
                return int(publish_years[0])
            except (ValueError, IndexError):
                pass
        
        return None
