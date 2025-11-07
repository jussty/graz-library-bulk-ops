"""Data models for books, search results, and reservations"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Book:
    """Represents a book in the library catalog"""

    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    medium_type: str = "Book"  # Book, eBook, Audio, DVD, etc.
    catalog_id: Optional[str] = None
    availability: str = "Unknown"  # Available, Checked Out, On Order
    location: Optional[str] = None
    call_number: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    url: Optional[str] = None

    def __post_init__(self):
        """Validate book data"""
        if not self.title:
            raise ValueError("Book title is required")

    def __str__(self) -> str:
        author_str = f" by {self.author}" if self.author else ""
        year_str = f" ({self.publication_year})" if self.publication_year else ""
        availability_str = f" [{self.availability}]"
        return f"{self.title}{author_str}{year_str}{availability_str}"

    def __repr__(self) -> str:
        return f"Book(title={self.title!r}, author={self.author!r}, isbn={self.isbn!r})"

    def to_dict(self) -> dict:
        """Convert book to dictionary"""
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "publisher": self.publisher,
            "publication_year": self.publication_year,
            "medium_type": self.medium_type,
            "catalog_id": self.catalog_id,
            "availability": self.availability,
            "location": self.location,
            "call_number": self.call_number,
            "description": self.description,
            "cover_url": self.cover_url,
            "url": self.url,
        }


@dataclass
class SearchResult:
    """Represents a search result containing multiple books"""

    query: str
    books: List[Book] = field(default_factory=list)
    total_results: int = 0
    search_type: str = "keyword"  # keyword, author, title, isbn
    timestamp: datetime = field(default_factory=datetime.now)
    search_time_ms: Optional[float] = None

    def __len__(self) -> int:
        return len(self.books)

    def __iter__(self):
        return iter(self.books)

    def __str__(self) -> str:
        return f"SearchResult: {self.total_results} results for '{self.query}'"

    def add_book(self, book: Book) -> None:
        """Add a book to search results"""
        self.books.append(book)
        self.total_results = len(self.books)

    def to_dict(self) -> dict:
        """Convert search result to dictionary"""
        return {
            "query": self.query,
            "search_type": self.search_type,
            "total_results": self.total_results,
            "search_time_ms": self.search_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "books": [book.to_dict() for book in self.books],
        }


@dataclass
class Reservation:
    """Represents a book reservation"""

    book: Book
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    reservation_date: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, confirmed, ready, cancelled
    ready_date: Optional[datetime] = None
    pickup_location: Optional[str] = None
    notification_email: Optional[str] = None

    def __str__(self) -> str:
        status_str = f" - {self.status.upper()}"
        date_str = self.ready_date.strftime("%Y-%m-%d") if self.ready_date else "TBD"
        return f"Reservation: {self.book.title}{status_str} (Ready: {date_str})"

    def to_dict(self) -> dict:
        """Convert reservation to dictionary"""
        return {
            "book": self.book.to_dict(),
            "user_id": self.user_id,
            "user_email": self.user_email,
            "reservation_date": self.reservation_date.isoformat(),
            "status": self.status,
            "ready_date": self.ready_date.isoformat() if self.ready_date else None,
            "pickup_location": self.pickup_location,
            "notification_email": self.notification_email,
        }


@dataclass
class MailOrder:
    """Represents a mail order request"""

    book: Book
    recipient_name: str
    recipient_email: str
    recipient_phone: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None  # Alternative: pickup at branch
    order_date: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, confirmed, sent, delivered
    tracking_id: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        """Validate mail order data"""
        if not self.recipient_name or not self.recipient_email:
            raise ValueError("Recipient name and email are required")
        if not self.delivery_address and not self.pickup_location:
            raise ValueError("Either delivery address or pickup location must be provided")

    def __str__(self) -> str:
        return f"MailOrder: {self.book.title} to {self.recipient_name} [{self.status}]"

    def to_dict(self) -> dict:
        """Convert mail order to dictionary"""
        return {
            "book": self.book.to_dict(),
            "recipient_name": self.recipient_name,
            "recipient_email": self.recipient_email,
            "recipient_phone": self.recipient_phone,
            "delivery_address": self.delivery_address,
            "pickup_location": self.pickup_location,
            "order_date": self.order_date.isoformat(),
            "status": self.status,
            "tracking_id": self.tracking_id,
            "notes": self.notes,
        }
