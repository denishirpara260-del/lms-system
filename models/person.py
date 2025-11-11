from abc import ABC, abstractmethod
from typing import List
from .book import Book


class Person(ABC):
    """Abstract base class for library users."""

    def __init__(self, name: str, person_id: str):
        self.name = name
        self.person_id = person_id

    @abstractmethod
    def get_role(self):
        pass

class Member(Person):
    def __init__(self, name: str, member_id: str):
        super().__init__(name, member_id)
        self.borrowed_books: List[str] = []

    def get_role(self):
        return "Member"

    def borrow_book(self, book: Book):
        self.borrowed_books.append(book.book_id)

    def return_book(self, book: Book):
        if book.book_id in self.borrowed_books:
            self.borrowed_books.remove(book.book_id)

        
class Librarian(Person):
    def get_role(self):
        return "Librarian"
