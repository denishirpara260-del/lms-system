class LibraryError(Exception):
    """Base exception for library errors."""

class BookNotAvailableError(LibraryError):
    pass


class BookNotFoundError(LibraryError):
    pass


class MemberNotFoundError(LibraryError):
    pass
