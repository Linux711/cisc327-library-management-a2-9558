import pytest
from services.library_service import borrow_book_by_patron, add_book_to_catalog

def test_borrow_success():
    """Test successful borrowing of a book"""
    add_book_to_catalog("Borrowable", "Author", "2222222222222", 3)
    success, msg = borrow_book_by_patron("123456", 1)
    assert success is True

def test_borrow_invalid_patron():
    """Test borrowing with an invalid patron ID"""
    success, msg = borrow_book_by_patron("abc123", 1)
    assert success is False

def test_borrow_nonexistent_book():
    """Test borrowing a book that does not exist"""
    success, msg = borrow_book_by_patron("123456", 999)
    assert success is False

def test_borrow_exceed_limit():
    """Test borrowing when patron has reached borrowing limit"""
    add_book_to_catalog("Book1", "Author", "4444444444444", 1)
    add_book_to_catalog("Book2", "Author", "5555555555555", 1)