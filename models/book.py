from typing import Dict, Any
from .exceptions import BookNotAvailableError


class Book:
    """Represents a book in the library."""

    def __init__(self, book_id: str, title: str, author: str, available: bool = True):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.available = available

    def borrow(self):
        if not self.available:
            raise BookNotAvailableError(f"Book '{self.title}' is already borrowed.")
        self.available = False

    def return_book(self):
        self.available = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "available": self.available,
        }
