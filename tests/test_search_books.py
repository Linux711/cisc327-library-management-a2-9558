import pytest
from services.library_service import search_books_in_catalog

def test_search_books_empty_search_term():
    """Test search with empty search term"""
    results = search_books_in_catalog("", "title")
    assert results == []

def test_search_books_invalid_search_type():
    """Test search with invalid search type"""
    results = search_books_in_catalog("Python", "publisher")
    assert results == []

def test_search_books_by_title_partial_match():
    """Test search by title with partial match"""
    results = search_books_in_catalog("Python", "title")
    assert isinstance(results, list)
    if len(results) > 0:
        assert all("python" in book['title'].lower() for book in results)

def test_search_books_returns_list():
    """Test that search returns a list"""
    results = search_books_in_catalog("Test", "title")
    assert isinstance(results, list)
