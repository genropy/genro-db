"""Test suite for BookStore example."""

import pytest
import sys
from pathlib import Path

# Add examples/bookstore to path
bookstore_path = Path(__file__).parent.parent / "examples" / "bookstore"
sys.path.insert(0, str(bookstore_path))

from bookstore_manager import BookStore


@pytest.fixture
def bookstore():
    """Create bookstore with sample data for each test."""
    store = BookStore(db_path=":memory:")
    store.import_from_csv()
    yield store
    store.close()


@pytest.fixture
def empty_bookstore():
    """Create empty bookstore for testing."""
    store = BookStore(db_path=":memory:")
    yield store
    store.close()


class TestBookStoreCreation:
    """Test bookstore creation and initialization."""

    def test_create_bookstore(self):
        """Test creating a bookstore."""
        store = BookStore(db_path=":memory:")
        assert store is not None
        assert store.maindb is not None
        store.close()

    def test_tables_exist(self, empty_bookstore):
        """Test that tables are created."""
        assert hasattr(empty_bookstore.maindb.tables, 'shelf')
        assert hasattr(empty_bookstore.maindb.tables, 'book')


class TestDataImport:
    """Test CSV data import."""

    def test_import_csv(self, bookstore):
        """Test importing CSV data."""
        stats = bookstore.get_stats()
        assert stats['total_shelves'] == 10
        assert stats['total_books'] == 55
        assert stats['total_pages'] == 45800
        assert stats['total_genres'] == 11

    def test_shelves_imported(self, bookstore):
        """Test that shelves are imported correctly."""
        shelves = bookstore.maindb.tables.shelf.list()
        assert len(shelves) == 10
        shelf_codes = [s['code'] for s in shelves]
        assert 'A1' in shelf_codes
        assert 'B1' in shelf_codes


class TestShelfOperations:
    """Test shelf-related operations."""

    def test_list_shelves(self, bookstore):
        """Test listing all shelves."""
        shelves = bookstore.maindb.tables.shelf.list()
        assert len(shelves) == 10
        assert all('code' in s and 'name' in s for s in shelves)

    def test_get_shelf(self, bookstore):
        """Test getting a specific shelf by code (primary key)."""
        # ShelfTable uses 'code' as primary key via pkey attribute
        shelves = bookstore.maindb.tables.shelf.list()
        first_shelf = shelves[0]

        # Get by primary key (code)
        shelf = bookstore.maindb.tables.shelf.get(first_shelf['code'])
        assert shelf is not None
        assert shelf['code'] == first_shelf['code']
        assert 'name' in shelf

    def test_list_books_on_shelf(self, bookstore):
        """Test listing books on a specific shelf."""
        books = bookstore.maindb.tables.shelf.list_books('A1')
        assert len(books) > 0
        assert all(book['shelf_code'] == 'A1' for book in books)

    def test_count_books_on_shelf(self, bookstore):
        """Test counting books on a shelf."""
        count = bookstore.maindb.tables.shelf.count_books('A1')
        books = bookstore.maindb.tables.shelf.list_books('A1')
        assert count == len(books)

    def test_shelf_not_found(self, bookstore):
        """Test error when shelf doesn't exist."""
        with pytest.raises(KeyError, match="not found"):
            bookstore.maindb.tables.shelf.list_books('INVALID')


class TestBookOperations:
    """Test book-related operations."""

    def test_list_books(self, bookstore):
        """Test listing all books."""
        books = bookstore.maindb.tables.book.list()
        assert len(books) == 55
        assert all('title' in b and 'author' in b for b in books)

    def test_get_book(self, bookstore):
        """Test getting a specific book."""
        books = bookstore.maindb.tables.book.list()
        first_book = books[0]
        fetched = bookstore.maindb.tables.book.get(first_book['id'])
        assert fetched['id'] == first_book['id']
        assert fetched['title'] == first_book['title']

    def test_list_by_author(self, bookstore):
        """Test searching books by author."""
        # Search for partial match
        books = bookstore.maindb.tables.book.list_by_author('Austen')
        assert len(books) > 0
        assert all('Austen' in book['author'] for book in books)

    def test_list_by_genre(self, bookstore):
        """Test listing books by genre."""
        books = bookstore.maindb.tables.book.list_by_genre('Fiction')
        assert len(books) > 0
        assert all(book['genre'] == 'Fiction' for book in books)

    def test_get_genres(self, bookstore):
        """Test getting all genres."""
        genres = bookstore.get_genres()
        assert len(genres) == 11
        assert 'Fiction' in genres
        assert 'Science' in genres


class TestBookCRUD:
    """Test CRUD operations on books."""

    def test_insert_book(self, empty_bookstore):
        """Test inserting a new book."""
        # First insert a shelf
        empty_bookstore.maindb.tables.shelf.insert(record={
            "code": "TEST",
            "name": "Test Shelf"
        })

        # Insert book
        book_id = empty_bookstore.maindb.tables.book.insert(record={
            "title": "Test Book",
            "author": "Test Author",
            "publisher": "Test Publisher",
            "pages": 100,
            "genre": "Test",
            "shelf_code": "TEST"
        })

        assert book_id is not None

        # Verify it was inserted
        book = empty_bookstore.maindb.tables.book.get(book_id)
        assert book['title'] == "Test Book"
        assert book['pages'] == 100

    def test_update_book(self, bookstore):
        """Test updating a book."""
        books = bookstore.maindb.tables.book.list()
        book = books[0].copy()

        # Update pages
        original_pages = book['pages']
        book['pages'] = original_pages + 50

        bookstore.maindb.tables.book.update(record=book)

        # Verify update
        updated = bookstore.maindb.tables.book.get(book['id'])
        assert updated['pages'] == original_pages + 50

    def test_delete_book(self, bookstore):
        """Test deleting a book."""
        books = bookstore.maindb.tables.book.list()
        initial_count = len(books)
        book_to_delete = books[0]

        # Delete
        bookstore.maindb.tables.book.delete(record={"id": book_to_delete['id']})

        # Verify deletion
        remaining = bookstore.maindb.tables.book.list()
        assert len(remaining) == initial_count - 1

        # Verify it's really gone
        with pytest.raises(KeyError):
            bookstore.maindb.tables.book.get(book_to_delete['id'])

    def test_move_book(self, bookstore):
        """Test moving a book to different shelf."""
        book = bookstore.maindb.tables.book.list()[0]
        original_shelf = book['shelf_code']

        # Find a different shelf
        shelves = bookstore.maindb.tables.shelf.list()
        new_shelf = next(s['code'] for s in shelves if s['code'] != original_shelf)

        # Move book
        bookstore.maindb.tables.book.move(book['id'], new_shelf)

        # Verify move
        updated = bookstore.maindb.tables.book.get(book['id'])
        assert updated['shelf_code'] == new_shelf


class TestStatistics:
    """Test statistics methods."""

    def test_get_stats(self, bookstore):
        """Test getting bookstore statistics."""
        stats = bookstore.get_stats()

        assert 'total_shelves' in stats
        assert 'total_books' in stats
        assert 'total_pages' in stats
        assert 'total_genres' in stats

        assert stats['total_shelves'] > 0
        assert stats['total_books'] > 0
        assert stats['total_pages'] > 0

    def test_stats_empty_store(self, empty_bookstore):
        """Test statistics on empty bookstore."""
        stats = empty_bookstore.get_stats()

        assert stats['total_shelves'] == 0
        assert stats['total_books'] == 0
        assert stats['total_pages'] == 0
        assert stats['total_genres'] == 0
