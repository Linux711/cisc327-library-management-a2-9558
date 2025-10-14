import pytest
from library_service import return_book_by_patron

def test_return_book_success():
    """Test successful book return"""
    success, message = return_book_by_patron("123456", 1)
    assert success is True
    assert "Successfully returned" in message

def test_return_book_invalid_patron_id_empty():
    """Test return with empty patron ID"""
    success, message = return_book_by_patron("", 1)
    assert success is False
    assert message == "Invalid patron ID. Must be exactly 6 digits."

def test_return_book_nonexistent_book():
    """Test return with book that doesn't exist"""
    success, message = return_book_by_patron("123456", 99999)
    assert success is False
    assert message == "Book not found."

def test_return_book_overdue():
    """Test returning a book that is overdue"""
    patron_id = "234567"  
    book_id = 3           
    success, message = return_book_by_patron(patron_id, book_id)
    assert success is True
    assert "Successfully returned" in message
    assert isinstance(message, str)
