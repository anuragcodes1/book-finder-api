"""Google Books API client."""

import requests
from typing import Optional
from models.book import Book


class GoogleBooksClient:
    """Client for interacting with the Google Books API."""
    
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def get_books_by_author(self, author_name: str) -> list[Book]:
        """
        Fetch books by author from Google Books.
        
        Args:
            author_name: The name of the author
            
        Returns:
            List of Book objects
        """
        try:
            params = {
                "q": f"inauthor:{author_name}",
                "maxResults": 40
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_response(data)
        
        except requests.RequestException as e:
            print(f"Error fetching from Google Books: {e}")
            return []
    
    def _parse_response(self, data: dict) -> list[Book]:
        """Parse Google Books API response into Book objects."""
        books = []
        
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            
            title = volume_info.get("title")
            if not title:
                continue
            
            # Extract publication year
            published_year = self._extract_year(volume_info)
            
            # Get URL
            url = volume_info.get("infoLink") or volume_info.get("canonicalVolumeLink", "")
            
            books.append(Book(
                title=title,
                published_year=published_year,
                url=url,
                source="google_books"
            ))
        
        return books
    
    def _extract_year(self, volume_info: dict) -> Optional[int]:
        """Extract publication year from volume info."""
        published_date = volume_info.get("publishedDate", "")
        if published_date:
            try:
                # Published date can be YYYY, YYYY-MM, or YYYY-MM-DD
                year = published_date.split("-")[0]
                return int(year)
            except (ValueError, IndexError):
                pass
        
        return None
