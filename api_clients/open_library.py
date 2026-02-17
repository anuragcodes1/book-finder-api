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
    RESULTS_PER_PAGE = 100  # Fetch 100 per request for efficiency
    
    def get_books_by_author(self, author_name: str) -> Dict[str, Any]:
        """
        Fetch ALL books by author from Open Library using pagination.
        
        Args:
            author_name: The name of the author
            
        Returns:
            Dictionary with 'books' list and 'status' info
        """
        all_books = []
        offset = 0
        total_found = None
        
        while True:
            for attempt in range(self.MAX_RETRIES):
                try:
                    params = {
                        "author": author_name,
                        "limit": self.RESULTS_PER_PAGE,
                        "offset": offset
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
                        if len(all_books) > 0:
                            # Return what we have so far
                            break
                        return {
                            "books": [],
                            "status": "error",
                            "error": "Invalid response format"
                        }
                    
                    # Get total number of results on first request
                    if total_found is None:
                        total_found = data.get("numFound", 0)
                        logger.info(f"Open Library: Found {total_found} total books for {author_name}")
                    
                    # Parse books from this page
                    books = self._parse_response(data)
                    
                    if not books:
                        # No more results
                        logger.info(f"Open Library: Finished fetching at offset {offset}, total: {len(all_books)}")
                        break
                    
                    all_books.extend(books)
                    logger.info(f"Open Library: Fetched {len(books)} books at offset {offset}, total so far: {len(all_books)}")
                    
                    # Check if we've fetched everything
                    if len(all_books) >= total_found or len(books) < self.RESULTS_PER_PAGE:
                        logger.info(f"Open Library: Completed fetching all {len(all_books)} books")
                        break
                    
                    # Move to next page
                    offset += self.RESULTS_PER_PAGE
                    break  # Success, move to next page
                
                except requests.Timeout:
                    logger.warning(f"Open Library timeout at offset {offset} (attempt {attempt + 1}/{self.MAX_RETRIES})")
                    if attempt == self.MAX_RETRIES - 1:
                        if len(all_books) > 0:
                            # Return what we have
                            logger.info(f"Open Library: Returning {len(all_books)} books after timeout")
                            return {
                                "books": all_books,
                                "status": "partial",
                                "error": "Request timeout, partial results"
                            }
                        return {
                            "books": [],
                            "status": "error",
                            "error": "Request timeout"
                        }
                
                except requests.ConnectionError as e:
                    logger.error(f"Open Library connection error at offset {offset}: {e}")
                    if len(all_books) > 0:
                        return {
                            "books": all_books,
                            "status": "partial",
                            "error": "Connection failed, partial results"
                        }
                    return {
                        "books": [],
                        "status": "error",
                        "error": "Connection failed"
                    }
                
                except requests.HTTPError as e:
                    status_code = e.response.status_code if e.response else None
                    logger.error(f"Open Library HTTP error {status_code} at offset {offset}: {e}")
                    if len(all_books) > 0:
                        return {
                            "books": all_books,
                            "status": "partial",
                            "error": f"API error (HTTP {status_code}), partial results"
                        }
                    return {
                        "books": [],
                        "status": "error",
                        "error": f"API error (HTTP {status_code})"
                    }
                
                except Exception as e:
                    logger.error(f"Unexpected error with Open Library at offset {offset}: {e}")
                    if len(all_books) > 0:
                        return {
                            "books": all_books,
                            "status": "partial",
                            "error": "Unexpected error, partial results"
                        }
                    return {
                        "books": [],
                        "status": "error",
                        "error": "Unexpected error"
                    }
            
            # Break outer loop if we're done or hit an error
            if not books or len(all_books) >= (total_found or 0):
                break
        
        if len(all_books) == 0:
            return {
                "books": [],
                "status": "success",
                "count": 0
            }
        
        return {
            "books": all_books,
            "status": "success",
            "count": len(all_books)
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
                
                # Get cover image using multiple methods
                thumbnail = self._get_cover_url(doc, key)
                
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
    
    def _get_cover_url(self, doc: dict, key: str) -> Optional[str]:
        """Extract cover URL from Open Library document using multiple methods."""
        # Method 1: Use cover_i (cover ID) - most reliable
        cover_id = doc.get("cover_i")
        if cover_id:
            return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        
        # Method 2: Use cover_edition_key (OLID)
        cover_edition_key = doc.get("cover_edition_key")
        if cover_edition_key:
            return f"https://covers.openlibrary.org/b/olid/{cover_edition_key}-M.jpg"
        
        # Method 3: Use first edition_key from list
        edition_keys = doc.get("edition_key", [])
        if edition_keys and isinstance(edition_keys, list) and len(edition_keys) > 0:
            return f"https://covers.openlibrary.org/b/olid/{edition_keys[0]}-M.jpg"
        
        # Method 4: Extract from work/book key
        if key:
            key_parts = key.split('/')
            if len(key_parts) >= 3:
                id_value = key_parts[2]  # e.g., 'OL46125W'
                return f"https://covers.openlibrary.org/b/olid/{id_value}-M.jpg"
        
        return None
