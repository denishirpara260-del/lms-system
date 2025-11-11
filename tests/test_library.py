import unittest
from library import Library
from models.book import Book

class TestLibrary(unittest.TestCase):
    def setUp(self):
        self.lib = Library(":memory:")

    def test_add_book(self):
        book = Book("1", "Python", "Guido")
        self.lib.add_book(book)
        self.assertEqual(len(self.lib.list_books()), 1)

if __name__ == "__main__":
    unittest.main()
