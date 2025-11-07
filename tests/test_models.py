"""Tests for data models"""

import pytest
from datetime import datetime
from src.graz_library.models.book import Book, SearchResult, Reservation, MailOrder


class TestBook:
    """Test Book model"""

    def test_book_creation(self):
        """Test basic book creation"""
        book = Book(title="Harry Potter", author="J.K. Rowling")
        assert book.title == "Harry Potter"
        assert book.author == "J.K. Rowling"
        assert book.medium_type == "Book"
        assert book.availability == "Unknown"

    def test_book_missing_title(self):
        """Test that title is required"""
        with pytest.raises(ValueError):
            Book(title="")

    def test_book_with_all_fields(self):
        """Test book with all fields"""
        book = Book(
            title="1984",
            author="George Orwell",
            isbn="0451524934",
            publisher="Penguin Books",
            publication_year=1949,
            medium_type="Book",
            catalog_id="12345",
            availability="Available",
            location="Zanklhof",
        )
        assert book.isbn == "0451524934"
        assert book.publication_year == 1949
        assert book.location == "Zanklhof"

    def test_book_to_dict(self):
        """Test converting book to dictionary"""
        book = Book(title="Test Book", author="Test Author")
        book_dict = book.to_dict()
        assert isinstance(book_dict, dict)
        assert book_dict["title"] == "Test Book"
        assert book_dict["author"] == "Test Author"

    def test_book_str_representation(self):
        """Test string representation"""
        book = Book(
            title="Test",
            author="Author",
            publication_year=2020,
            availability="Available",
        )
        str_repr = str(book)
        assert "Test" in str_repr
        assert "Author" in str_repr
        assert "2020" in str_repr
        assert "Available" in str_repr


class TestSearchResult:
    """Test SearchResult model"""

    def test_search_result_creation(self):
        """Test search result creation"""
        result = SearchResult(query="Harry Potter")
        assert result.query == "Harry Potter"
        assert len(result) == 0
        assert result.total_results == 0

    def test_search_result_add_book(self):
        """Test adding books to search result"""
        result = SearchResult(query="test")
        book1 = Book(title="Book 1")
        book2 = Book(title="Book 2")

        result.add_book(book1)
        result.add_book(book2)

        assert len(result) == 2
        assert result.total_results == 2
        assert result.books[0].title == "Book 1"

    def test_search_result_iteration(self):
        """Test iterating over search results"""
        result = SearchResult(query="test")
        result.add_book(Book(title="Book 1"))
        result.add_book(Book(title="Book 2"))

        titles = [book.title for book in result]
        assert titles == ["Book 1", "Book 2"]

    def test_search_result_to_dict(self):
        """Test converting search result to dictionary"""
        result = SearchResult(query="test", search_type="keyword")
        result.add_book(Book(title="Test Book"))

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["query"] == "test"
        assert result_dict["search_type"] == "keyword"
        assert result_dict["total_results"] == 1
        assert len(result_dict["books"]) == 1


class TestReservation:
    """Test Reservation model"""

    def test_reservation_creation(self):
        """Test reservation creation"""
        book = Book(title="Test Book")
        reservation = Reservation(
            book=book,
            user_email="user@example.com",
            pickup_location="Zanklhof",
        )
        assert reservation.book.title == "Test Book"
        assert reservation.user_email == "user@example.com"
        assert reservation.status == "pending"

    def test_reservation_to_dict(self):
        """Test converting reservation to dictionary"""
        book = Book(title="Test Book")
        reservation = Reservation(book=book, user_email="user@example.com")
        res_dict = reservation.to_dict()

        assert isinstance(res_dict, dict)
        assert res_dict["status"] == "pending"
        assert res_dict["user_email"] == "user@example.com"


class TestMailOrder:
    """Test MailOrder model"""

    def test_mail_order_creation_with_delivery(self):
        """Test mail order creation with delivery address"""
        book = Book(title="Test Book")
        order = MailOrder(
            book=book,
            recipient_name="John Doe",
            recipient_email="john@example.com",
            delivery_address="123 Main St",
        )
        assert order.book.title == "Test Book"
        assert order.recipient_name == "John Doe"
        assert order.status == "pending"

    def test_mail_order_creation_with_pickup(self):
        """Test mail order creation with pickup location"""
        book = Book(title="Test Book")
        order = MailOrder(
            book=book,
            recipient_name="Jane Doe",
            recipient_email="jane@example.com",
            pickup_location="Zanklhof",
        )
        assert order.pickup_location == "Zanklhof"

    def test_mail_order_missing_recipient(self):
        """Test that recipient name and email are required"""
        book = Book(title="Test Book")
        with pytest.raises(ValueError):
            MailOrder(
                book=book,
                recipient_name="",
                recipient_email="test@example.com",
                delivery_address="123 Main St",
            )

    def test_mail_order_missing_address_and_location(self):
        """Test that either address or pickup location is required"""
        book = Book(title="Test Book")
        with pytest.raises(ValueError):
            MailOrder(
                book=book,
                recipient_name="John Doe",
                recipient_email="john@example.com",
            )

    def test_mail_order_to_dict(self):
        """Test converting mail order to dictionary"""
        book = Book(title="Test Book")
        order = MailOrder(
            book=book,
            recipient_name="John Doe",
            recipient_email="john@example.com",
            delivery_address="123 Main St",
        )
        order_dict = order.to_dict()

        assert isinstance(order_dict, dict)
        assert order_dict["recipient_name"] == "John Doe"
        assert order_dict["status"] == "pending"
