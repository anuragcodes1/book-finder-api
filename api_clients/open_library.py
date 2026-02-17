"""Open Library API client."""

import requests
import logging
from typing import Optional, Dict, Any
from models.book import Book

logger = logging.getLogger(__name__)


class OpenLibraryClient:
    """Client for interacting with the Open Library API."""
    
    BASE_URL = "https://openlibrary.org"
    SEARCH_URL = f"{BASE_URL}/search.json"
    TIMEOUT = 10
    MAX_RETRIES = 2
    
    def get_books_by_author(self, author_name: str) -> Dict[str, Any]:
        """
        Fetch books by author from Open Library.
        
        Args:
            author_name: The name of the author
            
        Returns:
            Dictionary with 'books' list and 'status' info
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                params = {
                    "author": author_name,
                    "limit": 100
                }
                
                response = requests.get(
                    self.SEARCH_URL, 
                    params=params, 
                    timeout=self.TIMEOUT
                )
                response.raise_for_status()
                
                # Safely parse JSON
                try:
                    data = response.json()
                except ValueError as e:
                    logger.error(f"Open Library returned invalid JSON: {e}")
                    return {
                        "books": [],
                        "status": "error",
                        "error": "Invalid response format"
                    }
                
                books = self._parse_response(data)
                return {
                    "books": books,
                    "status": "success",
                    "count": len(books)
                }
            
            except requests.Timeout:
                logger.warning(f"Open Library timeout (attempt {attempt + 1}/{self.MAX_RETRIES})")
                if attempt == self.MAX_RETRIES - 1:
                    return {
                        "books": [],
                        "status": "error",
                        "error": "Request timeout"
                    }
            
            except requests.ConnectionError as e:
                logger.error(f"Open Library connection error: {e}")
                return {
                    "books": [],
                    "status": "error",
                    "error": "Connection failed"
                }
            
            except requests.HTTPError as e:
                status_code = e.response.status_code if e.response else None
                logger.error(f"Open Library HTTP error {status_code}: {e}")
                return {
                    "books": [],
                    "status": "error",
                    "error": f"API error (HTTP {status_code})"
                }
            
            except Exception as e:
                logger.error(f"Unexpected error with Open Library: {e}")
                return {
                    "books": [],
                    "status": "error",
                    "error": "Unexpected error"
                }
        
        return {
            "books": [],
            "status": "error",
            "error": "Max retries exceeded"
        }
    
    def _parse_response(self, data: dict) -> list[Book]:
        """Parse Open Library API response into Book objects."""
        books = []
        
        try:
            docs = data.get("docs", [])
            if not isinstance(docs, list):
                logger.error("Open Library 'docs' field is not a list")
                return books
            
            for doc in docs:
                if not isinstance(doc, dict):
                    continue
                
                title = doc.get("title")
                if not title or not isinstance(title, str):
                    continue
                
                # Get the first published year
                published_year = self._extract_year(doc)
                
                # Construct URL using the key
                key = doc.get("key", "")
                url = f"{self.BASE_URL}{key}" if key else self.BASE_URL
                
                # Get cover image from Open Library Covers API
                thumbnail = None
                if key:
                    # Extract work/edition ID for cover
                    key_parts = key.split('/')
                    if len(key_parts) >= 3:
                        id_type = key_parts[1]  # 'works' or 'books'
                        id_value = key_parts[2]  # e.g., 'OL46125W'
                        if id_type in ['works', 'books']:
                            thumbnail = f"https://covers.openlibrary.org/b/olid/{id_value}-M.jpg"
                
                books.append(Book(
                    title=title.strip(),
                    published_year=published_year,
                    url=url,
                    source="open_library",
                    thumbnail=thumbnail
                ))
        
        except Exception as e:
            logger.error(f"Error parsing Open Library response: {e}")
        
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
