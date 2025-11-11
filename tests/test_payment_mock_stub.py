# tests/test_payment_mock_stub.py

import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

@pytest.fixture
def stub_db_functions(mocker):
    # calculate_late_fee_for_book with $5 late fee
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={'fee_amount': 5.00, 'days_overdue': 5, 'status': 'Book is overdue by 5 days'}
    )
    
    # get_book_by_id to return test book
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={'book_id': 1, 'title': 'Test Book', 'available_copies': 1}
    )

def test_pay_late_fees_success(mocker, stub_db_functions):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = True
    
    success, message = pay_late_fees("123456", 1, mock_gateway)
    
    assert success is True
    assert "Payment successful" in message
    mock_gateway.process_payment.assert_called_once_with("123456", 5.00)

def test_pay_late_fees_declined(mocker, stub_db_functions):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = False
    
    success, message = pay_late_fees("123456", 1, mock_gateway)
    
    assert success is False
    assert "Payment declined" in message
    mock_gateway.process_payment.assert_called_once_with("123456", 5.00)

def test_pay_late_fees_invalid_patron_id(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = pay_late_fees("abc123", 1, mock_gateway)
    
    assert success is False
    assert "Invalid patron ID" in message
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_zero_fee(mocker):
    # Stub late fee = 0
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Book is not overdue'}
    )
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = pay_late_fees("123456", 1, mock_gateway)
    
    assert success is False
    assert "No late fees" in message
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_network_error(mocker, stub_db_functions):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network Error")
    
    success, message = pay_late_fees("123456", 1, mock_gateway)
    
    assert success is False
    assert "network error" in message.lower()
    mock_gateway.process_payment.assert_called_once_with("123456", 5.00)


def test_refund_success(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = True
    
    success, message = refund_late_fee_payment("txn123", 5.00, mock_gateway)
    
    assert success is True
    assert "Refund successful" in message
    mock_gateway.refund_payment.assert_called_once_with("txn123", 5.00)

def test_refund_invalid_transaction_id(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("", 5.00, mock_gateway)
    
    assert success is False
    assert "Invalid transaction ID" in message
    mock_gateway.refund_payment.assert_not_called()

@pytest.mark.parametrize("amount", [-5.0, 0.0, 16.0])
def test_refund_invalid_amounts(mocker, amount):
    mock_gateway = Mock(spec=PaymentGateway)
    
    success, message = refund_late_fee_payment("txn123", amount, mock_gateway)
    
    assert success is False
    assert "Invalid refund amount" in message
    mock_gateway.refund_payment.assert_not_called()
