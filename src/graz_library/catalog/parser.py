"""HTML parsing utilities for the WebOPAC catalog"""

from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup, Tag
from datetime import datetime
import re

from ..models.book import Book
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CatalogParser:
    """Parses HTML from the WebOPAC catalog"""

    def __init__(self):
        """Initialize the parser"""
        self.logger = logger

    def parse_search_results(self, html: str) -> List[Book]:
        """Parse book search results from HTML

        Args:
            html: HTML content from search results page

        Returns:
            List of Book objects extracted from HTML
        """
        books = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Find all result items (this will depend on actual WebOPAC structure)
            # Placeholder selector - needs to be adjusted based on actual HTML
            result_items = soup.find_all("div", class_=["result-item", "hit"])

            if not result_items:
                self.logger.debug(
                    "No result items found - checking alternative selectors"
                )
                result_items = soup.find_all("div", class_="result")

            for item in result_items:
                try:
                    book = self._parse_book_item(item)
                    if book:
                        books.append(book)
                except Exception as e:
                    self.logger.warning(f"Failed to parse book item: {e}")
                    continue

            self.logger.info(f"Parsed {len(books)} books from search results")
            return books

        except Exception as e:
            self.logger.error(f"Error parsing search results: {e}")
            return []

    def _parse_book_item(self, item: Tag) -> Optional[Book]:
        """Parse a single book item from HTML

        Args:
            item: BeautifulSoup Tag containing book information

        Returns:
            Book object or None if parsing fails
        """
        try:
            # Extract title (usually in a link or heading)
            title_elem = item.find(["h2", "h3", "a"], class_=["title", "hit-title"])
            title = title_elem.get_text(strip=True) if title_elem else None

            if not title:
                self.logger.debug("Could not find title in item")
                return None

            # Extract author
            author_elem = item.find(["span", "p"], class_=["author", "creator"])
            author = author_elem.get_text(strip=True) if author_elem else None

            # Extract ISBN
            isbn = self._extract_isbn(item)

            # Extract catalog/item ID from link
            catalog_id = None
            link_elem = item.find("a", href=re.compile(r".*\d+.*"))
            if link_elem and link_elem.get("href"):
                # Extract ID from URL (format-dependent)
                match = re.search(r"(\d+)", link_elem["href"])
                if match:
                    catalog_id = match.group(1)

            # Extract availability
            availability = self._extract_availability(item)

            # Extract location/branch
            location = self._extract_location(item)

            # Extract medium type (if available)
            medium_elem = item.find(["span", "p"], class_=["medium-type", "type"])
            medium_type = (
                medium_elem.get_text(strip=True) if medium_elem else "Book"
            )

            # Extract publication year
            pub_year = self._extract_publication_year(item)

            # Get URL if available
            url = None
            url_elem = item.find("a", href=re.compile(r".*"))
            if url_elem and url_elem.get("href"):
                url = url_elem["href"]
                if not url.startswith("http"):
                    url = "https://stadtbibliothek.graz.at" + url

            return Book(
                title=title,
                author=author,
                isbn=isbn,
                catalog_id=catalog_id,
                availability=availability,
                location=location,
                medium_type=medium_type,
                publication_year=pub_year,
                url=url,
            )

        except Exception as e:
            self.logger.debug(f"Error parsing book item: {e}")
            return None

    def _extract_isbn(self, item: Tag) -> Optional[str]:
        """Extract ISBN from book item

        Args:
            item: BeautifulSoup Tag

        Returns:
            ISBN string or None
        """
        try:
            # Look for ISBN in text
            text = item.get_text()
            isbn_match = re.search(r"ISBN[:\s]*([0-9\-X]+)", text, re.IGNORECASE)
            if isbn_match:
                isbn = isbn_match.group(1).replace("-", "").replace(" ", "")
                # Validate basic ISBN format
                if len(isbn) in [10, 13]:
                    return isbn
        except Exception:
            pass
        return None

    def _extract_availability(self, item: Tag) -> str:
        """Extract availability status from book item

        Args:
            item: BeautifulSoup Tag

        Returns:
            Availability string (Available, Checked Out, On Order, etc.)
        """
        try:
            # Look for availability indicators
            avail_elem = item.find(["span", "p"], class_=["availability", "status"])
            if avail_elem:
                status_text = avail_elem.get_text(strip=True).lower()

                if "available" in status_text or "verfügbar" in status_text:
                    return "Available"
                elif "checked out" in status_text or "ausgeliehen" in status_text:
                    return "Checked Out"
                elif "order" in status_text or "bestellt" in status_text:
                    return "On Order"
                elif "reserved" in status_text or "reserviert" in status_text:
                    return "Reserved"
                else:
                    return status_text

            # Alternative: look for visual indicators (color, icons)
            if item.find("span", class_=["available", "green"]):
                return "Available"
            elif item.find("span", class_=["unavailable", "red"]):
                return "Checked Out"

        except Exception:
            pass

        return "Unknown"

    def _extract_location(self, item: Tag) -> Optional[str]:
        """Extract library location/branch from book item

        Args:
            item: BeautifulSoup Tag

        Returns:
            Location string or None
        """
        try:
            location_elem = item.find(
                ["span", "p"], class_=["location", "branch", "library"]
            )
            if location_elem:
                return location_elem.get_text(strip=True)
        except Exception:
            pass
        return None

    def _extract_publication_year(self, item: Tag) -> Optional[int]:
        """Extract publication year from book item

        Args:
            item: BeautifulSoup Tag

        Returns:
            Publication year as int or None
        """
        try:
            text = item.get_text()
            year_match = re.search(r"\b(19|20)\d{2}\b", text)
            if year_match:
                return int(year_match.group(0))
        except Exception:
            pass
        return None

    def parse_book_detail(self, html: str) -> Dict[str, Any]:
        """Parse detailed book information from a book detail page

        Args:
            html: HTML content from book detail page

        Returns:
            Dictionary with book details
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            details = {}

            # Extract various fields based on common WebOPAC structure
            # This is a template - adjust based on actual HTML structure

            # Title
            title_elem = soup.find(["h1", "h2"], class_=["title", "hit-title"])
            details["title"] = title_elem.get_text(strip=True) if title_elem else None

            # Author
            author_elem = soup.find(["span", "p"], class_=["author", "creator"])
            details["author"] = (
                author_elem.get_text(strip=True) if author_elem else None
            )

            # Description
            desc_elem = soup.find(["div", "p"], class_=["description", "summary"])
            details["description"] = (
                desc_elem.get_text(strip=True) if desc_elem else None
            )

            # Cover image
            cover_elem = soup.find("img", class_=["cover", "thumbnail"])
            details["cover_url"] = cover_elem.get("src") if cover_elem else None

            return details

        except Exception as e:
            self.logger.error(f"Error parsing book details: {e}")
            return {}
