from models.book import Book
from models.person import Member
from models.exceptions import (
    BookNotFoundError,
    MemberNotFoundError,
    BookNotAvailableError,
)
from database import Database


class Library:
    """Main library system class for managing books and members."""

    def __init__(self, db_name="library.db"):
        self.db = Database(db_name)

    # 1️⃣ Add a new book
    def add_book(self, book: Book):
        """Add a new book to the database."""
        self.db.add_book(book.to_dict())

    # 2️⃣ Remove an existing book
    def remove_book(self, book_id: str):
        """Remove a book by ID."""
        book = self.db.find_book(book_id)
        if not book:
            raise BookNotFoundError("Book not found")
        self.db.remove_book(book_id)

    # 3️⃣ Register a new member
    def register_member(self, member: Member):
        """Register a new library member."""
        with self.db.conn:
            self.db.conn.execute(
                "INSERT INTO members (member_id, name) VALUES (?, ?)",
                (member.person_id, member.name),
            )

    # 4️⃣ Borrow a book
    def borrow_book(self, member_id: str, book_id: str):
        """Mark a book as borrowed by a member."""
        member = self.find_member(member_id)
        book = self.find_book(book_id)

        if not book["available"]:
            raise BookNotAvailableError("Book is already borrowed")

        # Update book availability
        with self.db.conn:
            self.db.conn.execute(
                "UPDATE books SET available = 0 WHERE book_id = ?",
                (book_id,),
            )

            self.db.conn.execute(
                "INSERT INTO borrowed_books (member_id, book_id) VALUES (?, ?)",
                (member_id, book_id),
            )

    # 5️⃣ Return a book
    def return_book(self, member_id: str, book_id: str):
        """Return a borrowed book."""
        book = self.find_book(book_id)
        if not book:
            raise BookNotFoundError("Book not found")

        with self.db.conn:
            self.db.conn.execute(
                "UPDATE books SET available = 1 WHERE book_id = ?",
                (book_id,),
            )
            self.db.conn.execute(
                "DELETE FROM borrowed_books WHERE member_id = ? AND book_id = ?",
                (member_id, book_id),
            )

    # 6️⃣ List all books
    def list_books(self):
        """Return all books in the database."""
        return self.db.get_books()

    # 7️⃣ List available books
    def list_available_books(self):
        """Return only available books."""
        return [b for b in self.db.get_books() if b["available"]]

    # 8️⃣ Search books
    def search_books(self, query: str):
        """Search for books by title or author."""
        q = query.lower()
        return [
            b for b in self.db.get_books()
            if q in b["title"].lower() or q in b["author"].lower()
        ]

    # 9️⃣ List all members
    def list_members(self):
        """Return all registered members."""
        cur = self.db.conn.execute("SELECT * FROM members")
        return [{"member_id": m[0], "name": m[1]} for m in cur]

    # 🔟 List borrowed books
    def list_borrowed_books(self):
        """Return all borrowed books with member info."""
        cur = self.db.conn.execute("""
            SELECT b.book_id, b.title, b.author, m.member_id, m.name
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.book_id
            JOIN members m ON bb.member_id = m.member_id
        """)
        return [
            {
                "book_id": row[0],
                "title": row[1],
                "author": row[2],
                "member_id": row[3],
                "member_name": row[4],
            }
            for row in cur
        ]

    # Helper methods
    def find_book(self, book_id: str):
        """Find a book by ID."""
        book = self.db.find_book(book_id)
        if not book:
            raise BookNotFoundError("Book not found")
        return book

    def find_member(self, member_id: str):
        """Find a member by ID."""
        cur = self.db.conn.execute(
            "SELECT * FROM members WHERE member_id = ?",
            (member_id,),
        )
        member = cur.fetchone()
        if not member:
            raise MemberNotFoundError("Member not found")
        return {"member_id": member[0], "name": member[1]}
