"""Book data model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    """Represents a book with its metadata."""
    
    title: str
    published_year: Optional[int]
    url: str
    source: str  # 'open_library' or 'google_books'
    
    def __str__(self) -> str:
        year = self.published_year if self.published_year else "Unknown"
        return f"{self.title} ({year}) - {self.url}"
