from __future__ import annotations
import json  #read/write json data
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass # __init__, __eq__
from typing import List, Dict, Optional, Any
import os
import sys # cmd
import functools
import unittest

class LibraryError(Exception):
    """Base exception for library errors."""

class BookNotAvailableError(LibraryError):
    pass

class BookNotFoundError(LibraryError):
    pass

class MemberNotFoundError(LibraryError):
    pass

def logged(func):
    """Simple decorator that logs entry/exit of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[LOG] Finished {func.__name__}")
        return result
    return wrapper

# small context manager for file operations (demonstration)
@contextmanager
def atomic_write(path: str, mode: str = "w"):
    """Context manager that writes to a temp file and then renames it.
    Safer write for persistence.
    """
    tmp = f"{path}.tmp"
    try:
        f = open(tmp, mode, encoding="utf-8")
        yield f
    finally:
        try:
            f.close()
            os.replace(tmp, path)
        except Exception:
            if os.path.exists(tmp):
                os.remove(tmp)

class Book:
    """Represents a book in the library."""

    def __init__(self, book_id: str, title: str, author: str, available: bool = True):
        self.book_id = book_id
        self.title = title
        self.author = author
        self._available = available

    @property
    def book_id(self) -> str:
        return self._book_id

    @book_id.setter
    def book_id(self, value: Any) -> None:
        if value is None or str(value).strip() == "":
            raise ValueError("book_id cannot be empty")
        self._book_id = str(value)

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if not isinstance(value, str) or value.strip() == "":
            raise ValueError("title must be a non-empty string")
        self._title = value.strip()

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, value: str) -> None:
        if not isinstance(value, str) or value.strip() == "":
            raise ValueError("author must be a non-empty string")
        self._author = value.strip()

    @property
    def available(self) -> bool:
        return self._available

    def borrow(self) -> None:
        """Mark book as borrowed; raise if not available."""
        if not self._available:
            raise BookNotAvailableError(f"Book '{self.title}' is not available")
        self._available = False

    def return_book(self) -> None:
        """Mark book as returned."""
        self._available = True

    def to_dict(self) -> Dict[str, Any]:
        return {"book_id": self.book_id, "title": self.title, "author": self.author, "available": self.available}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Book":
        return cls(d["book_id"], d["title"], d["author"], d.get("available", True))

    # operator overloading
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self.book_id == other.book_id

    def __lt__(self, other: "Book") -> bool:
        return self.title.lower() < other.title.lower()

    def __repr__(self) -> str:
        return f"Book({self.book_id!r}, {self.title!r}, {self.author!r}, available={self.available})"


class Person(ABC):
    """Abstract base for people in the library."""

    def __init__(self, name: str, person_id: str):
        self._name = name
        self._person_id = str(person_id)

    @abstractmethod
    def get_role(self) -> str:
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def person_id(self) -> str:
        return self._person_id


class Member(Person):
    """Library member who can borrow books."""

    def __init__(self, name: str, member_id: str):
        super().__init__(name, member_id)
        self.borrowed_books: List[str] = []

    def get_role(self) -> str:
        return "Member"

    def borrow_book(self, book: Book) -> None:
        if book.book_id in self.borrowed_books:
            # already borrowed
            return
        self.borrowed_books.append(book.book_id)

    def return_book(self, book: Book) -> None:
        if book.book_id in self.borrowed_books:
            self.borrowed_books.remove(book.book_id)

    def __add__(self, other: "Member") -> "Member":
        if not isinstance(other, Member):
            return NotImplemented
        merged = Member(f"{self.name}&{other.name}", f"{self.person_id}+{other.person_id}")
        merged.borrowed_books = list(set(self.borrowed_books + other.borrowed_books))
        return merged

    def __repr__(self) -> str:
        return f"Member({self.name!r}, {self.person_id!r}, borrowed={self.borrowed_books!r})"


class Librarian(Person):
    """Library staff."""

    def get_role(self) -> str:
        return "Librarian"

# -------------------- Library Class --------------------
class Library:
    """Main library manager handling books, members, and persistence."""

    def __init__(self, data_file: str = "library_data.json") -> None:
        self.data_file = data_file
        self.books: List[Book] = []
        self.members: List[Member] = []
        self.load_data()

    def next_book_id(self):
        numbers = []
        for b in self.books:
            if b.book_id.startswith("B") and b.book_id[1:].isdigit():
                numbers.append(int(b.book_id[1:]))
        if not numbers:
            return "B1"
        return f"B{max(numbers) + 1}"


    def next_member_id(self):
        numbers = []
        for m in self.members:
            if m.person_id.startswith("M") and m.person_id[1:].isdigit():
                numbers.append(int(m.person_id[1:]))
        if not numbers:
            return "M1"
        return f"M{max(numbers) + 1}"


    # persistence
    @logged
    def save_data(self) -> None:
        data = {
            "books": [b.to_dict() for b in self.books],
            "members": [{"name": m.name, "member_id": m.person_id, "borrowed_books": m.borrowed_books} for m in self.members],
        }
        # use atomic_write context manager
        with atomic_write(self.data_file, "w") as f:
            json.dump(data, f, indent=4)    

    @logged
    def load_data(self) -> None:
        if not os.path.exists(self.data_file):
            return
        with open(self.data_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return
        self.books = [Book.from_dict(d) for d in data.get("books", [])]
        self.members = [Member(m["name"], m["member_id"]) for m in data.get("members", [])]
        # restore borrowed lists
        member_map = {m.person_id: m for m in self.members}
        for mdata in data.get("members", []):
            mid = mdata.get("member_id")
            if mid in member_map:
                member_map[mid].borrowed_books = mdata.get("borrowed_books", [])

    def add_book(self, book: Book) -> None:
        if any(b.book_id == book.book_id for b in self.books):
            raise ValueError("Book with that ID already exists")
        self.books.append(book)
        self.save_data()

    def remove_book(self, book_id: str) -> None:
        for b in list(self.books):
            if b.book_id == str(book_id):
                self.books.remove(b)
                self.save_data()
                return
        raise BookNotFoundError("Book not found")

    def register_member(self, member: Member) -> None:
        if any(m.person_id == member.person_id for m in self.members):
            raise ValueError("Member with that ID already exists")
        self.members.append(member)
        self.save_data()

    def find_book(self, book_id: str) -> Book:
        for b in self.books:
            if b.book_id == str(book_id):
                return b
        raise BookNotFoundError("Book not found")

    def find_member(self, member_id: str) -> Member:
        for m in self.members:
            if m.person_id == str(member_id):
                return m
        raise MemberNotFoundError("Member not found")

    @logged
    def borrow_book(self, member_id: str, book_id: str) -> None:
        member = self.find_member(member_id)
        book = self.find_book(book_id)
        book.borrow()
        member.borrow_book(book)
        self.save_data()

    @logged
    def return_book(self, member_id: str, book_id: str) -> None:
        member = self.find_member(member_id)
        book = self.find_book(book_id)
        book.return_book()
        member.return_book(book)
        self.save_data()

    @staticmethod
    def list_available_books(books: List[Book]) -> List[Book]:
        """Return available books (demonstrates staticmethod)."""
        return [b for b in books if b.available]

    @classmethod
    def from_file(cls, data_file: str) -> "Library":
        """Construct a Library instance pointing to a specific data file."""
        return cls(data_file)

    def search_books(self, query: str) -> List[Book]:
        q = query.lower()
        matches = [b for b in self.books if q in b.title.lower() or q in b.author.lower()]
        return sorted(matches, key=lambda x: x.title)


# -------------------- Console UI --------------------
MENU = """
Library Menu:
1. Add book
2. Remove book
3. Register member
4. Borrow book
5. Return book
6. List all books
7. List available books
8. Search books
9. List all members
10. List borrowed books
11. Exit
"""

def prompt(text: str) -> str:
    try:
        return input(text)
    except KeyboardInterrupt:
        print()
        return ""

def run_console(library: Library) -> None:
    while True:
        print(MENU)
        choice = prompt("Enter choice: ").strip()
        if choice == "1":  
            title = prompt("Title: ")
            author = prompt("Author: ")
            bid = library.next_book_id()  
            try:
                library.add_book(Book(bid, title, author))
                print(f"Book added with ID {bid}.")
            except Exception as e:
                print("Error:", e)
        elif choice == "2":
            bid = prompt("Book ID to remove: ")
            try:
                library.remove_book(bid)
                print("Removed.")
            except Exception as e:
                print("Error:", e)
        elif choice == "3":  
            name = prompt("Name: ")
            mid = library.next_member_id()  
            try:
                library.register_member(Member(name, mid))
                print(f"Member registered with ID {mid}.")
            except Exception as e:
                print("Error:", e)
        elif choice == "4":
            mid = prompt("Member ID: ")
            bid = prompt("Book ID: ")
            try:
                library.borrow_book(mid, bid)
                print("Borrowed.")
            except Exception as e:
                print("Error:", e)
        elif choice == "5":
            mid = prompt("Member ID: ")
            bid = prompt("Book ID: ")
            try:
                library.return_book(mid, bid)
                print("Returned.")
            except Exception as e:
                print("Error:", e)
        elif choice == "6":
            for b in sorted(library.books):
                print(b)
        elif choice == "7":
            for b in library.list_available_books(library.books):
                print(b)
        elif choice == "8":
            q = prompt("Search query: ")
            for b in library.search_books(q):
                print(b)

        elif choice == "9":
            print("\nAll Members:")
            if not library.members:
                print("No members registered.")
            for m in library.members:
                borrowed_titles = [
                    library.find_book(bid).title
                    for bid in m.borrowed_books
                    if any(b.book_id == bid for b in library.books)
                ]
                print(f"Member: {m.name} ({m.person_id}) | Borrowed: {borrowed_titles or 'None'}")

        elif choice == "10":
            print("\nBorrowed Books:")
            found = False
            for m in library.members:
                for bid in m.borrowed_books:
                    try:
                        b = library.find_book(bid)
                        print(f"Book '{b.title}' borrowed by {m.name} ({m.person_id})")
                        found = True
                    except BookNotFoundError:
                        pass
            if not found:
                print("No borrowed books currently.")
        elif choice == "11":
            print("Goodbye")
            break
        else:
            print("Invalid choice")

# -------------------- Unit Tests --------------------
class TestLibrary(unittest.TestCase):
    def setUp(self):
        # use a temp data file to avoid clobbering real data
        self.test_file = "test_library_data.json"
        # remove if exists
        try:
            os.remove(self.test_file)
        except Exception:
            pass
        self.lib = Library(self.test_file)

    def tearDown(self):
        try:
            os.remove(self.test_file)
        except Exception:
            pass

    def test_add_and_find_book(self):
        b = Book("1", "A Title", "An Author")
        self.lib.add_book(b)
        found = self.lib.find_book("1")
        self.assertEqual(found, b)

    def test_register_and_find_member(self):
        m = Member("Alice", "m1")
        self.lib.register_member(m)
        found = self.lib.find_member("m1")
        self.assertEqual(found.person_id, "m1")

    def test_borrow_and_return(self):
        b = Book("2", "B Title", "B Author")
        m = Member("Bob", "m2")
        self.lib.add_book(b)
        self.lib.register_member(m)
        self.lib.borrow_book("m2", "2")
        self.assertFalse(self.lib.find_book("2").available)
        self.assertIn("2", self.lib.find_member("m2").borrowed_books)
        self.lib.return_book("m2", "2")
        self.assertTrue(self.lib.find_book("2").available)

    def test_search(self):
        self.lib.add_book(Book("3", "Python Programming", "Guido"))
        self.lib.add_book(Book("4", "Learn C++", "Bjarne"))
        matches = self.lib.search_books("python")
        self.assertEqual(len(matches), 1)

# -------------------- Entrypoint --------------------
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # run tests
        unittest.main(argv=[sys.argv[0]])
    else:
        lib = Library()
        run_console(lib)
