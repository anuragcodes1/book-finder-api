#!/usr/bin/env python3
"""
Book Finder - Search for books by author using Open Library and Google Books APIs
"""

import logging
from typing import Dict, Any
from api_clients.open_library import OpenLibraryClient
from api_clients.google_books import GoogleBooksClient
from models.book import Book
from utils.formatter import format_results

logger = logging.getLogger(__name__)


def search_books_by_author(author_name: str) -> Dict[str, Any]:
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
    
    # Fetch from Open Library
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
    
    # Fetch from Google Books
    try:
        google_books = GoogleBooksClient()
        gb_result = google_books.get_books_by_author(author_name)
        all_books.extend(gb_result["books"])
        sources_status["google_books"] = {
            "status": gb_result["status"],
            "count": len(gb_result["books"])
        }
        if gb_result["status"] == "error":
            sources_status["google_books"]["error"] = gb_result.get("error", "Unknown error")
    except Exception as e:
        logger.error(f"Unexpected error calling Google Books: {e}")
        sources_status["google_books"] = {
            "status": "error",
            "count": 0,
            "error": "Service unavailable"
        }
    
    # Remove duplicates based on title similarity
    unique_books = _deduplicate_books(all_books)
    
    # Sort by publication year
    sorted_books = sorted(unique_books, key=lambda x: x.published_year or 0, reverse=True)
    
    return {
        "books": sorted_books,
        "sources": sources_status
    }


def _deduplicate_books(books: list[Book]) -> list[Book]:
    """Remove duplicate books based on title similarity."""
    seen = {}
    unique = []
    
    for book in books:
        normalized_title = book.title.lower().strip()
        if normalized_title not in seen:
            seen[normalized_title] = True
            unique.append(book)
    
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
