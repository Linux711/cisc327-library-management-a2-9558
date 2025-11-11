import pytest
from unittest.mock import patch
from services.library_service import (
    add_book_to_catalog
)

@patch("services.library_service.get_book_by_isbn", return_value=None)
@patch("services.library_service.insert_book", return_value=True)

def test_add_book_valid_input(mock_insert, mock_get):
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message


# Add more test methods for each function and edge case. You can keep all your test in a separate folder named `tests`.