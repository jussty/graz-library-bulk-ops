"""External book search using public APIs to verify book existence"""

from typing import Optional, List, Dict, Any
import requests
from urllib.parse import quote
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ExternalBookSearcher:
    """Search for books using external sources (Google Books, Open Library, etc.)"""

    @staticmethod
    def search_open_library(title: str, author: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search Open Library API

        Args:
            title: Book title
            author: Author name (optional)

        Returns:
            Dict with book info or None
        """
        try:
            url = "https://openlibrary.org/search.json"
            query = title
            if author:
                query = f"{title} {author}"

            params = {
                "title": query,
                "limit": 5
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("docs"):
                book = data["docs"][0]
                isbn = book.get("isbn", ["N/A"])[0] if book.get("isbn") else "N/A"

                return {
                    "source": "Open Library",
                    "title": book.get("title"),
                    "author": book.get("author_name", ["N/A"])[0] if book.get("author_name") else "N/A",
                    "isbn": isbn,
                    "published": book.get("first_publish_year", "N/A"),
                    "pages": book.get("number_of_pages_median", "N/A"),
                    "url": f"https://openlibrary.org{book.get('key', '')}"
                }
            return None
        except Exception as e:
            logger.debug(f"Open Library search error for '{title}': {e}")
            return None

    @staticmethod
    def search_google_books(title: str, author: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search Google Books API

        Note: Requires no API key for basic searches

        Args:
            title: Book title
            author: Author name (optional)

        Returns:
            Dict with book info or None
        """
        try:
            url = "https://www.googleapis.com/books/v1/volumes"
            query = f"intitle:{quote(title)}"
            if author:
                query += f"+inauthor:{quote(author)}"

            params = {
                "q": query,
                "maxResults": 5,
                "langRestrict": "de"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("items"):
                book = data["items"][0]["volumeInfo"]
                identifiers = book.get("industryIdentifiers", [])
                isbn = "N/A"
                for identifier in identifiers:
                    if identifier.get("type") == "ISBN_13":
                        isbn = identifier.get("identifier")
                        break
                    elif identifier.get("type") == "ISBN_10":
                        isbn = identifier.get("identifier")

                return {
                    "source": "Google Books",
                    "title": book.get("title"),
                    "author": ", ".join(book.get("authors", [])),
                    "isbn": isbn,
                    "published": book.get("publishedDate", "N/A"),
                    "pages": book.get("pageCount", "N/A"),
                    "url": book.get("infoLink")
                }
            return None
        except Exception as e:
            logger.debug(f"Google Books search error for '{title}': {e}")
            return None

    @staticmethod
    def search_worldcat(title: str, author: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search WorldCat (world library catalog)

        Args:
            title: Book title
            author: Author name (optional)

        Returns:
            Dict with book info or None
        """
        try:
            query = title
            if author:
                query = f"{title} {author}"

            return {
                "source": "WorldCat",
                "title": title,
                "url": f"https://www.worldcat.org/search?q={quote(query)}"
            }
        except Exception as e:
            logger.debug(f"WorldCat search error for '{title}': {e}")
            return None

    @staticmethod
    def search_book_external(title: str, author: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for book using multiple external sources

        Args:
            title: Book title
            author: Author name (optional)

        Returns:
            List of results from different sources
        """
        results = []

        # Try Open Library (most reliable for metadata)
        ol_result = ExternalBookSearcher.search_open_library(title, author)
        if ol_result:
            results.append(ol_result)

        # Try Google Books
        gb_result = ExternalBookSearcher.search_google_books(title, author)
        if gb_result:
            results.append(gb_result)

        # WorldCat is always available as a reference
        wc_result = ExternalBookSearcher.search_worldcat(title, author)
        if wc_result:
            results.append(wc_result)

        return results

    @staticmethod
    def verify_book_exists(title: str, author: Optional[str] = None) -> bool:
        """Verify if a book exists in any external source

        Args:
            title: Book title
            author: Author name (optional)

        Returns:
            True if book found in at least one source
        """
        results = ExternalBookSearcher.search_book_external(title, author)
        return len(results) > 0
