import pytest
from library_service import add_book_to_catalog

def test_add_book_success():
    """Test adding a book with valid details"""
    import random
    unique_isbn = f"{random.randint(1000000000000, 9999999999999)}"
    success, message = add_book_to_catalog("Test Book", "Author Name", unique_isbn, 5)
    assert success is True

def test_add_book_empty_title():
    """Test adding a book with an empty title"""
    success, message = add_book_to_catalog("", "Author", "1234567890124", 1)
    assert success is False

def test_add_book_long_title():
    """Test adding a book with a title that is too long"""
    long_title = "A" * 201
    success, message = add_book_to_catalog(long_title, "Author", "1234567890125", 1)
    assert success is False

def test_add_book_empty_author():
    """Test adding a book with an empty author"""
    success, message = add_book_to_catalog("Book", "", "1234567890126", 1)
    assert success is False

def test_add_book_invalid_isbn():
    """Test adding a book with an invalid ISBN"""
    success, message = add_book_to_catalog("Book", "Author", "123", 1)
    assert success is False
