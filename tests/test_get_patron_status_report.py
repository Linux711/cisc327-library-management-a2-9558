import pytest
from services.library_service import get_patron_status_report

def test_patron_status_invalid_id_empty():
    """Test patron status with empty patron ID"""
    result = get_patron_status_report("")
    assert result['status'] == 'Invalid patron ID'
    assert result['books_borrowed'] == 0
    assert result['books_available_to_borrow'] == 0
    assert result['borrowed_books'] == []
    assert result['total_late_fees'] == 0.00

def test_patron_status_valid_patron_no_books():
    """Test patron status for patron with no borrowed books"""
    result = get_patron_status_report("123456")
    assert result['patron_id'] == "123456"
    assert result['status'] == 'Active'
    assert result['books_borrowed'] >= 0
    assert result['books_available_to_borrow'] >= 0
    assert result['borrowing_limit'] == 5
    assert result['books_borrowed'] + result['books_available_to_borrow'] == 5
    assert isinstance(result['borrowed_books'], list)
    assert result['total_late_fees'] >= 0.00

def test_patron_status_patron_with_multiple_books():
    """Test patron status for patron with multiple borrowed books"""
    result = get_patron_status_report("345678")
    assert result['patron_id'] == "345678"
    assert result['status'] == 'Active'
    assert 'books_borrowed' in result
    assert 'books_available_to_borrow' in result
    assert result['borrowing_limit'] == 5
    assert result['books_borrowed'] + result['books_available_to_borrow'] == 5
    assert len(result['borrowed_books']) == result['books_borrowed']

def test_patron_status_with_overdue_books():
    """Test patron status with overdue books"""
    result = get_patron_status_report("678901")
    assert result['patron_id'] == "678901"
    assert result['status'] == 'Active'
    assert 'total_late_fees' in result
    assert isinstance(result['total_late_fees'], float)
    assert result['total_late_fees'] >= 0.00
    if result['total_late_fees'] > 0:
        assert any(book['is_overdue'] for book in result['borrowed_books'])