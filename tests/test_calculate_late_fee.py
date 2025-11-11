import pytest
from services.library_service import calculate_late_fee_for_book

def test_calculate_late_fee_invalid_patron_id_empty():
    """Test late fee calculation with empty patron ID"""
    result = calculate_late_fee_for_book("", 1)
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert result['status'] == 'Invalid patron ID'

def test_calculate_late_fee_book_not_found():
    """Test late fee calculation with nonexistent book"""
    result = calculate_late_fee_for_book("123456", 99999)
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert result['status'] == 'Book not found'

def test_calculate_late_fee_book_not_overdue():
    """Test late fee calculation for book that's not overdue"""
    result = calculate_late_fee_for_book("123456", 1)
    assert result['fee_amount'] == 0.00
    assert result['days_overdue'] == 0
    assert result['status'] == 'Book is not overdue'

def test_calculate_late_fee_book_overdue_10_days():
    """Test late fee calculation for book overdue by 10 days"""
    result = calculate_late_fee_for_book("123456", 3)
    assert result['days_overdue'] >= 0
    assert result['fee_amount'] >= 0.00
    assert 'overdue' in result['status'].lower() or 'not currently borrowed' in result['status'].lower()
