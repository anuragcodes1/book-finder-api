"""Output formatting utilities."""

from models.book import Book


def format_results(books: list[Book], author_name: str) -> str:
    """
    Format book results for display.
    
    Args:
        books: List of Book objects
        author_name: The author name that was searched
        
    Returns:
        Formatted string for display
    """
    output = []
    output.append(f"Found {len(books)} books by {author_name}:")
    output.append("=" * 80)
    
    for i, book in enumerate(books, 1):
        year = book.published_year if book.published_year else "Unknown"
        output.append(f"\n{i}. {book.title}")
        output.append(f"   Published: {year}")
        output.append(f"   URL: {book.url}")
        output.append(f"   Source: {book.source}")
    
    return "\n".join(output)


def format_json(books: list[Book]) -> list[dict]:
    """
    Format books as JSON-serializable dictionaries.
    
    Args:
        books: List of Book objects
        
    Returns:
        List of dictionaries
    """
    return [
        {
            "title": book.title,
            "published_year": book.published_year,
            "url": book.url,
            "source": book.source,
            "thumbnail": book.thumbnail
        }
        for book in books
    ]
