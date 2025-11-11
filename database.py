import sqlite3
from typing import List, Dict, Optional


class Database:
    def __init__(self, db_name: str = "library.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    # -------------------- TABLE CREATION --------------------
    def create_tables(self):
        """Create all required tables if they don't exist."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    book_id TEXT PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    available INTEGER
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    member_id TEXT PRIMARY KEY,
                    name TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS borrowed_books (
                    member_id TEXT,
                    book_id TEXT,
                    FOREIGN KEY(member_id) REFERENCES members(member_id),
                    FOREIGN KEY(book_id) REFERENCES books(book_id)
                )
            """)

    # -------------------- BOOKS --------------------
    def add_book(self, book: Dict):
        """Add a new book to the library."""
        with self.conn:
            self.conn.execute(
                "INSERT INTO books (book_id, title, author, available) VALUES (?, ?, ?, ?)",
                (book["book_id"], book["title"], book["author"], int(book.get("available", True))),
            )

    def remove_book(self, book_id: str):
        """Remove a book by ID."""
        with self.conn:
            self.conn.execute("DELETE FROM books WHERE book_id = ?", (book_id,))

    def get_books(self) -> List[Dict]:
        """Return all books."""
        cursor = self.conn.execute("SELECT * FROM books")
        rows = cursor.fetchall()
        return [        
            {"book_id": row[0], "title": row[1], "author": row[2], "available": bool(row[3])}
            for row in rows
        ]

    def search_books(self, query: str):
        """Search books by title or author (case-insensitive)."""
        cursor = self.conn.execute("""
            SELECT * FROM books
            WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ?
        """, (f"%{query.lower()}%", f"%{query.lower()}%"))
        rows = cursor.fetchall()
        return [
            {"book_id": r[0], "title": r[1], "author": r[2], "available": bool(r[3])}
            for r in rows
        ]


    def get_available_books(self) -> List[Dict]:
        """Return all books that are available."""
        cursor = self.conn.execute("SELECT * FROM books WHERE available = 1")
        rows = cursor.fetchall()
        return [
            {"book_id": row[0], "title": row[1], "author": row[2], "available": True}
            for row in rows
        ]

    def find_book(self, book_id: str) -> Optional[Dict]:
        """Find a specific book by ID."""
        cursor = self.conn.execute("SELECT * FROM books WHERE book_id=?", (book_id,))
        row = cursor.fetchone()
        return (
            {"book_id": row[0], "title": row[1], "author": row[2], "available": bool(row[3])}
            if row else None
        )


    def update_book_availability(self, book_id: str, available: bool):
        """Mark a book as available or unavailable."""
        with self.conn:
            self.conn.execute(
                "UPDATE books SET available = ? WHERE book_id = ?",
                (int(available), book_id)
            )

    # -------------------- MEMBERS --------------------
    def add_member(self, member: Dict):
        """Add a new library member."""
        with self.conn:
            self.conn.execute(
                "INSERT INTO members (member_id, name) VALUES (?, ?)",
                (member["member_id"], member["name"]),
            )

    def get_members(self) -> List[Dict]:
        """Return all library members."""
        cursor = self.conn.execute("SELECT * FROM members")
        rows = cursor.fetchall()
        return [{"member_id": row[0], "name": row[1]} for row in rows]

    def find_member(self, member_id: str) -> Optional[Dict]:
        """Find a specific member by ID."""
        cursor = self.conn.execute("SELECT * FROM members WHERE member_id=?", (member_id,))
        row = cursor.fetchone()
        return {"member_id": row[0], "name": row[1]} if row else None
    
    def get_borrowed_books(self):
        """Return list of borrowed books with member info."""
        cursor = self.conn.execute("""
            SELECT members.member_id, members.name, books.book_id, books.title, books.author
            FROM borrowed_books
            JOIN members ON borrowed_books.member_id = members.member_id
            JOIN books ON borrowed_books.book_id = books.book_id
        """)
        rows = cursor.fetchall()
        return [
            {
                "member_id": r[0],
                "member_name": r[1],
                "book_id": r[2],
                "title": r[3],
                "author": r[4]
            }
            for r in rows
        ]


    # -------------------- BORROW / RETURN --------------------


    def return_book(self, member_id: str, book_id: str):
        """Record that a member returned a book."""
        with self.conn:
            self.conn.execute(
                "DELETE FROM borrowed_books WHERE member_id = ? AND book_id = ?",
                (member_id, book_id),
            )
            self.update_book_availability(book_id, True)

    def get_borrowed_books(self) -> List[Dict]:
        """List all borrowed books with member info."""
        cursor = self.conn.execute("""
            SELECT b.book_id, b.title, b.author, m.member_id, m.name
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.book_id
            JOIN members m ON bb.member_id = m.member_id
        """)
        rows = cursor.fetchall()
        return [
            {
                "book_id": row[0],
                "title": row[1],
                "author": row[2],
                "member_id": row[3],
                "member_name": row[4],
            }
            for row in rows
        ]
