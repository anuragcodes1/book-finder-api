"""Google Books API client."""

import requests
import logging
from typing import Optional, Dict, Any
from models.book import Book

logger = logging.getLogger(__name__)


class GoogleBooksClient:
    """Client for interacting with the Google Books API."""
    
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    TIMEOUT = 10
    MAX_RETRIES = 2
    
    def get_books_by_author(self, author_name: str) -> Dict[str, Any]:
        """
        Fetch books by author from Google Books.
        
        Args:
            author_name: The name of the author
            
        Returns:
            Dictionary with 'books' list and 'status' info
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                params = {
                    "q": f"inauthor:{author_name}",
                    "maxResults": 40
                }
                
                response = requests.get(
                    self.BASE_URL, 
                    params=params, 
                    timeout=self.TIMEOUT
                )
                response.raise_for_status()
                
                # Safely parse JSON
                try:
                    data = response.json()
                except ValueError as e:
                    logger.error(f"Google Books returned invalid JSON: {e}")
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
                logger.warning(f"Google Books timeout (attempt {attempt + 1}/{self.MAX_RETRIES})")
                if attempt == self.MAX_RETRIES - 1:
                    return {
                        "books": [],
                        "status": "error",
                        "error": "Request timeout"
                    }
            
            except requests.ConnectionError as e:
                logger.error(f"Google Books connection error: {e}")
                return {
                    "books": [],
                    "status": "error",
                    "error": "Connection failed"
                }
            
            except requests.HTTPError as e:
                status_code = e.response.status_code if e.response else None
                logger.error(f"Google Books HTTP error {status_code}: {e}")
                return {
                    "books": [],
                    "status": "error",
                    "error": f"API error (HTTP {status_code})"
                }
            
            except Exception as e:
                logger.error(f"Unexpected error with Google Books: {e}")
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
        """Parse Google Books API response into Book objects."""
        books = []
        
        try:
            items = data.get("items", [])
            if not isinstance(items, list):
                logger.error("Google Books 'items' field is not a list")
                return books
            
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                volume_info = item.get("volumeInfo", {})
                if not isinstance(volume_info, dict):
                    continue
                
                title = volume_info.get("title")
                if not title or not isinstance(title, str):
                    continue
                
                # Extract publication year
                published_year = self._extract_year(volume_info)
                
                # Get URL
                url = volume_info.get("infoLink") or volume_info.get("canonicalVolumeLink", "")
                if not url:
                    url = ""
                
                # Get cover image from imageLinks
                thumbnail = self._get_cover_url(volume_info)
                
                books.append(Book(
                    title=title.strip(),
                    published_year=published_year,
                    url=url,
                    source="google_books",
                    thumbnail=thumbnail
                ))
        
        except Exception as e:
            logger.error(f"Error parsing Google Books response: {e}")
        
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
    
    def _get_cover_url(self, volume_info: dict) -> Optional[str]:
        """Extract cover URL from Google Books volume info."""
        image_links = volume_info.get("imageLinks", {})
        if not isinstance(image_links, dict):
            return None
        
        # Try different sizes (prefer larger images)
        for size in ["large", "medium", "small", "thumbnail", "smallThumbnail"]:
            url = image_links.get(size)
            if url:
                # Upgrade to https if needed
                return url.replace("http://", "https://")
        
        return None
