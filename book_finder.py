#!/usr/bin/env python3
"""
Book Finder - Search for books by author using Open Library and Google Books APIs
"""

from api_clients.open_library import OpenLibraryClient
from api_clients.google_books import GoogleBooksClient
from models.book import Book
from utils.formatter import format_results


def search_books_by_author(author_name: str) -> list[Book]:
    """
    Search for books by author using multiple APIs.
    
    Args:
        author_name: The name of the author to search for
        
    Returns:
        List of Book objects with combined results from all APIs
    """
    all_books = []
    
    # Fetch from Open Library
    open_library = OpenLibraryClient()
    ol_books = open_library.get_books_by_author(author_name)
    all_books.extend(ol_books)
    
    # Fetch from Google Books
    google_books = GoogleBooksClient()
    gb_books = google_books.get_books_by_author(author_name)
    all_books.extend(gb_books)
    
    # Remove duplicates based on title similarity
    unique_books = _deduplicate_books(all_books)
    
    return sorted(unique_books, key=lambda x: x.published_year or 0, reverse=True)


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
