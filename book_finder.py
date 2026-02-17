#!/usr/bin/env python3
"""
Book Finder - Search for books by author using Open Library API
"""

import logging
import hashlib
from typing import Dict, Any
from api_clients.open_library import OpenLibraryClient
from models.book import Book
from utils.formatter import format_results

logger = logging.getLogger(__name__)

# Simple in-memory cache for consistent results
_cache = {}


def _get_cache_key(author_name: str) -> str:
    """Generate cache key for author."""
    return hashlib.md5(author_name.lower().strip().encode()).hexdigest()


def search_books_by_author(author_name: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    Search for books by author using multiple APIs.
    
    Args:
        author_name: The name of the author to search for
        
    Returns:
        Dictionary with books list and source status information
    """
    # Validate input
    if not author_name or not author_name.strip():
        return {
            "books": [],
            "sources": {},
            "error": "Author name cannot be empty"
        }
    
    author_name = author_name.strip()
    
    # Check cache first
    cache_key = _get_cache_key(author_name)
    if use_cache and cache_key in _cache:
        logger.info(f"Returning cached results for {author_name}")
        return _cache[cache_key]
    
    # Validate length
    if len(author_name) < 2:
        return {
            "books": [],
            "sources": {},
            "error": "Author name too short (minimum 2 characters)"
        }
    
    if len(author_name) > 200:
        return {
            "books": [],
            "sources": {},
            "error": "Author name too long (maximum 200 characters)"
        }
    
    all_books = []
    sources_status = {}
    
    # Fetch from Open Library only
    try:
        open_library = OpenLibraryClient()
        ol_result = open_library.get_books_by_author(author_name)
        all_books.extend(ol_result["books"])
        sources_status["open_library"] = {
            "status": ol_result["status"],
            "count": len(ol_result["books"])
        }
        if ol_result["status"] == "error":
            sources_status["open_library"]["error"] = ol_result.get("error", "Unknown error")
    except Exception as e:
        logger.error(f"Unexpected error calling Open Library: {e}")
        sources_status["open_library"] = {
            "status": "error",
            "count": 0,
            "error": "Service unavailable"
        }
    
    # No deduplication needed since we only have one source
    unique_books = all_books
    
    # Sort by publication year
    sorted_books = sorted(unique_books, key=lambda x: x.published_year or 0, reverse=True)
    
    result = {
        "books": sorted_books,
        "sources": sources_status
    }
    
    # Cache the result
    if use_cache:
        _cache[cache_key] = result
        logger.info(f"Cached results for {author_name}: {len(sorted_books)} books")
    
    return result


def _deduplicate_books(books: list[Book]) -> list[Book]:
    """
    Remove duplicate books based on title and year similarity.
    Uses consistent ordering to ensure same results every time.
    """
    seen = {}
    unique = []
    
    # Sort books first for consistent ordering (by source, then title)
    # This ensures same input always produces same output
    sorted_books = sorted(books, key=lambda x: (x.source, x.title.lower(), x.published_year or 0))
    
    for book in sorted_books:
        # Normalize title for comparison
        normalized_title = book.title.lower().strip()
        # Remove common punctuation and extra spaces
        normalized_title = ' '.join(normalized_title.split())
        
        # Create a key combining title and year for better deduplication
        # Books with same title but different years are likely different editions
        year_key = book.published_year if book.published_year else "unknown"
        dedup_key = f"{normalized_title}|{year_key}"
        
        if dedup_key not in seen:
            seen[dedup_key] = True
            unique.append(book)
        else:
            logger.debug(f"Duplicate found: {book.title} ({book.published_year}) from {book.source}")
    
    logger.info(f"Deduplication: {len(books)} -> {len(unique)} books ({len(books) - len(unique)} duplicates removed)")
    return unique


def main():
    """Main entry point for the book finder tool."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python book_finder.py <author_name>")
        sys.exit(1)
    
    author_name = " ".join(sys.argv[1:])
    print(f"Searching for books by: {author_name}\n")
    
    books = search_books_by_author(author_name)
    
    if not books:
        print(f"No books found for author: {author_name}")
        return
    
    print(format_results(books, author_name))


if __name__ == "__main__":
    main()
