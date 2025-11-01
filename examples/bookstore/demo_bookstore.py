#!/usr/bin/env python3
"""Test script for BookStore database operations."""

from bookstore_manager import BookStore


def main():
    """Test bookstore functionality."""
    print("=" * 60)
    print("BOOKSTORE DATABASE TEST")
    print("=" * 60)

    # 1. Create bookstore with in-memory database
    print("\n1. Creating bookstore...")
    bookstore = BookStore(db_path=":memory:")
    print("   ✓ BookStore created")

    # 2. Import sample data
    print("\n2. Importing sample data from CSV...")
    bookstore.import_from_csv()
    print("   ✓ Data imported")

    # 3. Get statistics
    print("\n3. Getting bookstore statistics...")
    stats = bookstore.get_stats()
    print(f"   - Total shelves: {stats['total_shelves']}")
    print(f"   - Total books: {stats['total_books']}")
    print(f"   - Total pages: {stats['total_pages']}")
    print(f"   - Total genres: {stats['total_genres']}")

    # 4. List all shelves
    print("\n4. Listing all shelves...")
    shelves = bookstore.maindb.tables.shelf.list()
    for shelf in shelves:
        print(f"   - [{shelf['code']}] {shelf['name']}")

    # 5. List books on a specific shelf
    print("\n5. Listing books on shelf 'A1' (Fiction A-F)...")
    fiction_books = bookstore.maindb.tables.shelf.list_books('A1')
    for book in fiction_books[:3]:  # Show first 3
        print(f"   - {book['title']} by {book['author']}")
    print(f"   ... ({len(fiction_books)} total books)")

    # 6. Search books by author
    print("\n6. Searching books by author 'Asimov'...")
    asimov_books = bookstore.maindb.tables.book.list_by_author('Asimov')
    for book in asimov_books:
        print(f"   - {book['title']} ({book['pages']} pages)")

    # 7. List books by genre
    print("\n7. Listing all genres...")
    genres = bookstore.get_genres()
    print(f"   - Genres: {', '.join(genres)}")

    print("\n8. Books in 'Science Fiction' genre...")
    scifi_books = bookstore.maindb.tables.book.list_by_genre('Science Fiction')
    for book in scifi_books[:3]:  # Show first 3
        print(f"   - {book['title']}")
    print(f"   ... ({len(scifi_books)} total)")

    # 8. Test CRUD operations
    print("\n9. Testing CRUD operations...")

    # Insert new book
    new_book_id = bookstore.maindb.tables.book.insert(record={
        "title": "Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "pages": 100,
        "genre": "Test Genre",
        "shelf_code": "A1"
    })
    print(f"   ✓ Inserted new book (ID: {new_book_id})")

    # Get the book
    book = bookstore.maindb.tables.book.get(new_book_id)
    print(f"   ✓ Retrieved book: {book['title']}")

    # Update the book
    book_to_update = book.copy()
    book_to_update['pages'] = 150
    bookstore.maindb.tables.book.update(record=book_to_update)
    updated_book = bookstore.maindb.tables.book.get(new_book_id)
    print(f"   ✓ Updated pages: {book['pages']} → {updated_book['pages']}")

    # Delete the book
    bookstore.maindb.tables.book.delete(record={"id": new_book_id})
    print(f"   ✓ Deleted book (ID: {new_book_id})")

    # 9. Close database
    print("\n10. Closing database...")
    bookstore.close()
    print("   ✓ Database closed")

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
