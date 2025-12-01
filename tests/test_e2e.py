import pytest
from playwright.sync_api import Page, expect
import sqlite3
import os

DATABASE = os.path.abspath("library.db")

def reset_test_patron_borrows(patron_id="000001"):
    """clear borrow records for test patron"""
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM borrow_records WHERE patron_id = ? AND return_date IS NULL",
                (patron_id,)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Failed to reset borrows: {e}")

def delete_test_books():
    """clean any previous 'Test Book' entries."""
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='books'"
            )
            if cursor.fetchone():
                cursor.execute("DELETE FROM books WHERE title = ?", ("Test Book",))
                conn.commit()
    except sqlite3.Error as e:
        print(f"Database deletion failed: {e}")


def test_add_book_and_verify_catalog(page: Page):
    """Add a book and verify it appears in the catalog."""
    # Clean up old Test Book entries
    delete_test_books()

    # Go to add book page
    page.goto("http://127.0.0.1:5000/add_book")

    # Fill out the form
    page.fill("input[name='title']", "Test Book")
    page.fill("input[name='author']", "John Doe")
    page.fill("input[name='isbn']", "1234567890123")
    page.fill("input[name='total_copies']", "5")

    # Submit form
    page.click("button[type='submit']")

    # Go to catalog page
    page.goto("http://127.0.0.1:5000/catalog")

    # Wait for the catalog table
    expect(page.locator("table tbody")).to_be_visible(timeout=5000)

    # Find the row that has the text "Test Book"
    book_row = page.locator("table tbody tr", has_text="Test Book").first

    # Verify title, author, and ISBN in that row
    expect(book_row.locator("td:nth-child(2)")).to_have_text("Test Book")
    expect(book_row.locator("td:nth-child(3)")).to_have_text("John Doe")
    expect(book_row.locator("td:nth-child(4)")).to_have_text("1234567890123")


def test_borrow_book(page: Page):

    reset_test_patron_borrows("000001")  # clear patron borrow records

    """borrow a book and verifying confirmation."""
    page.goto("http://127.0.0.1:5000/catalog")

    # Fill the first available book's borrow form
    book_row = page.locator("table tbody tr").first

    # Fill patron ID inside that row
    book_row.locator("input[name='patron_id']").fill("000001")

    # Submit the form
    book_row.locator("button[type='submit']").click()

    # Check for success flash (substring match)
    flash = page.locator("div.flash-success")
    expect(flash).to_be_visible()
    expect(flash).to_contain_text("Successfully borrowed")
