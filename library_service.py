"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count, get_patron_borrowed_books,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    # Update the borrow record with return date
    return_date = datetime.now()
    return_success = update_borrow_record_return_date(patron_id, book_id, return_date)
    if not return_success:
        return False, "No active borrow record found for this book and patron."
    
    # Update book availability
    availability_success = update_book_availability(book_id, 1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully returned "{book["title"]}".'




def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    Implements R5 as per requirements 
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book
        
    Returns:
        dict: Contains fee_amount, days_overdue, and status
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Invalid patron ID'
        }
    
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book not found'
        }
    
    # Get patron's borrowed books
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    # Find the specific book
    target_book = None
    for borrowed_book in borrowed_books:
        if borrowed_book['book_id'] == book_id:
            target_book = borrowed_book
            break
    
    if not target_book:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'This book is not currently borrowed by this patron'
        }
    
    # Calculate days overdue
    current_date = datetime.now()
    due_date = target_book['due_date']
    
    if current_date <= due_date:
        return {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'Book is not overdue'
        }
    
    # Calculate overdue days and fee
    days_overdue = (current_date - due_date).days
    fee_per_day = 0.50  # $0.50 per day late fee
    fee_amount = round(days_overdue * fee_per_day, 2)
    
    return {
        'fee_amount': fee_amount,
        'days_overdue': days_overdue,
        'status': f'Book is overdue by {days_overdue} days'
    }


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    Implements R6 as per requirements
    
    Args:
        search_term: Term to search for
        search_type: Type of search ('title', 'author', or 'isbn')
        
    Returns:
        list: List of matching books
    """
    # Validate inputs
    if not search_term or not search_term.strip():
        return []
    
    if search_type not in ['title', 'author', 'isbn']:
        return []
    
    search_term = search_term.strip().lower()
    
    # Get all books from database
    all_books = get_all_books()
    
    # Filter based on search type
    results = []
    for book in all_books:
        if search_type == 'title':
            if search_term in book.get('title', '').lower():
                results.append(book)
        elif search_type == 'author':
            if search_term in book.get('author', '').lower():
                results.append(book)
        elif search_type == 'isbn':
            if search_term == book.get('isbn', '').lower():
                results.append(book)
    
    return results


def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    Implements R7 as per requirements
    
    Args:
        patron_id: 6-digit library card ID
        
    Returns:
        dict: Patron status information including borrowed books and late fees
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            'patron_id': patron_id,
            'status': 'Invalid patron ID',
            'books_borrowed': 0,
            'books_available_to_borrow': 0,
            'borrowed_books': [],
            'total_late_fees': 0.00
        }
    
    # Get patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    books_available = max(0, 5 - current_borrowed)
    
    # Get detailed information about borrowed books
    borrowed_books = get_patron_borrowed_books(patron_id)
    
    # Calculate total late fees
    total_late_fees = 0.00
    for book in borrowed_books:
        if book['is_overdue']:
            fee_info = calculate_late_fee_for_book(patron_id, book['book_id'])
            total_late_fees += fee_info['fee_amount']
    
    return {
        'patron_id': patron_id,
        'status': 'Active',
        'books_borrowed': current_borrowed,
        'books_available_to_borrow': books_available,
        'borrowing_limit': 5,
        'borrowed_books': borrowed_books,
        'total_late_fees': round(total_late_fees, 2)
    }