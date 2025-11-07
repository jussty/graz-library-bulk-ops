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

    def _extract_field_by_label(self, soup: BeautifulSoup, label: str) -> Optional[str]:
        """Extract a field value by finding its label in the HTML

        This method looks for text patterns like "Label: Value" in the page.
        Works for detail pages that list metadata with labels.

        Args:
            soup: BeautifulSoup parsed HTML
            label: Field label to search for (e.g., "ISBN", "Verfasser")

        Returns:
            Field value as string or None if not found
        """
        try:
            # Get all text content
            page_text = soup.get_text()

            # Build regex pattern to find the label and extract the value
            # Patterns like "ISBN: 978-3-8332-3580-1"
            pattern = rf"{label}[:\s]+([^\n]*?)(?:\n|$)"
            match = re.search(pattern, page_text, re.IGNORECASE)

            if match:
                value = match.group(1).strip()
                # Remove trailing punctuation and whitespace
                value = re.sub(r"\s+$", "", value)
                if value:
                    return value
        except Exception as e:
            self.logger.debug(f"Error extracting field {label}: {e}")

        return None

    def _extract_exemplare_info(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract copy/exemplare information from the detail page

        Extracts table with library branch, location, call number, status, etc.

        Args:
            soup: BeautifulSoup parsed HTML

        Returns:
            List of dicts with copy information
        """
        exemplare_list = []
        try:
            # Look for table with "ZWEIGSTELLE", "SIGNATUR", "STATUS" headers
            tables = soup.find_all("table")

            for table in tables:
                rows = table.find_all("tr")
                if not rows:
                    continue

                # Check if this is the exemplare table by looking at headers
                header_text = " ".join([cell.get_text().strip() for cell in rows[0].find_all(["th", "td"])])
                if "zweigstelle" in header_text.lower() and "status" in header_text.lower():
                    # This is the exemplare table
                    for row in rows[1:]:  # Skip header row
                        cells = row.find_all("td")
                        if len(cells) >= 4:
                            exemplar = {
                                "branch": cells[0].get_text(strip=True) if len(cells) > 0 else None,
                                "call_number": cells[1].get_text(strip=True) if len(cells) > 1 else None,
                                "section": cells[2].get_text(strip=True) if len(cells) > 2 else None,
                                "status": cells[3].get_text(strip=True) if len(cells) > 3 else "Unknown",
                                "reservations": cells[4].get_text(strip=True) if len(cells) > 4 else "0",
                                "medium_type": cells[5].get_text(strip=True) if len(cells) > 5 else None,
                                "barcode": cells[7].get_text(strip=True) if len(cells) > 7 else None,
                            }
                            # Clean up status values
                            if "verfügbar" in exemplar["status"].lower():
                                exemplar["status"] = "Available"
                            elif "ausgeliehen" in exemplar["status"].lower():
                                exemplar["status"] = "Checked Out"

                            if exemplar.get("branch"):
                                exemplare_list.append(exemplar)

        except Exception as e:
            self.logger.debug(f"Error extracting exemplare info: {e}")

        return exemplare_list

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the book description/summary text

        Args:
            soup: BeautifulSoup parsed HTML

        Returns:
            Description text or None
        """
        try:
            # Look for description in common locations
            # Often appears as a paragraph or div after the title

            # Try to find by class
            desc_elem = soup.find(["div", "p"], class_=re.compile(r".*description|summary|content|abstract"))
            if desc_elem:
                text = desc_elem.get_text(strip=True)
                if text and len(text) > 50:
                    return text

            # Try finding the main content area
            main_content = soup.find("main") or soup.find(["div"], class_=re.compile(r".*main|content"))
            if main_content:
                # Find the first long paragraph after the title
                paragraphs = main_content.find_all("p")
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 100:
                        return text

        except Exception as e:
            self.logger.debug(f"Error extracting description: {e}")

        return None

    def parse_book_detail(self, html: str) -> Dict[str, Any]:
        """Parse detailed book information from a book detail page

        Args:
            html: HTML content from book detail page

        Returns:
            Dictionary with book details (compatible with Book model)
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            details = {}

            # Extract title (usually h1)
            title_elem = soup.find(["h1", "h2"])
            details["title"] = title_elem.get_text(strip=True) if title_elem else None

            # Extract media type (e.g., "Mediengruppe: Kinderbuch")
            details["medium_type"] = self._extract_field_by_label(soup, "Mediengruppe")

            # Extract author/creator
            author = self._extract_field_by_label(soup, "Verfasser")
            if author:
                # Remove "Suche nach diesem Verfasser" link text if present
                author = author.split("Suche nach")[0].strip()
            details["author"] = author

            # Extract ISBN
            isbn = self._extract_field_by_label(soup, "ISBN")
            if isbn:
                # Clean up ISBN (remove hyphens/spaces, validate)
                isbn = isbn.replace("-", "").replace(" ", "")
                if len(isbn) in [10, 13]:
                    details["isbn"] = isbn
                else:
                    details["isbn"] = None
            else:
                details["isbn"] = None

            # Extract publisher (Verlag)
            details["publisher"] = self._extract_field_by_label(soup, "Verlag")

            # Extract publication year (Jahr)
            year_str = self._extract_field_by_label(soup, "Jahr")
            if year_str:
                try:
                    details["publication_year"] = int(year_str.strip())
                except (ValueError, AttributeError):
                    details["publication_year"] = None
            else:
                details["publication_year"] = None

            # Extract language (Sprache)
            details["language"] = self._extract_field_by_label(soup, "Sprache")

            # Extract series (Reihe)
            series_text = self._extract_field_by_label(soup, "Reihe")
            if series_text:
                # Remove link formatting, join with commas
                series_parts = [s.strip() for s in series_text.split(",")]
                details["series"] = ", ".join(series_parts)
            else:
                details["series"] = None

            # Extract original title (Originaltitel)
            details["original_title"] = self._extract_field_by_label(soup, "Originaltitel")

            # Extract page count/description (Beschreibung)
            beschreibung = self._extract_field_by_label(soup, "Beschreibung")
            if beschreibung:
                # Try to extract page count from format like "148 S. : überw. Ill."
                page_match = re.search(r"^(\d+)\s*S\.", beschreibung)
                if page_match:
                    try:
                        details["page_count"] = int(page_match.group(1))
                    except (ValueError, AttributeError):
                        details["page_count"] = None
                else:
                    details["page_count"] = None
            else:
                details["page_count"] = None

            # Extract keywords (Schlagwörter)
            keywords_text = self._extract_field_by_label(soup, "Schlagwörter")
            if keywords_text:
                # Split by commas and clean up
                keywords = [k.strip() for k in keywords_text.split(",")]
                details["keywords"] = keywords
            else:
                details["keywords"] = []

            # Extract availability and branch info from Exemplare table
            exemplare_info = self._extract_exemplare_info(soup)
            if exemplare_info:
                # Use the first copy's information for top-level fields
                first_copy = exemplare_info[0]
                details["availability"] = first_copy.get("status", "Unknown")
                details["location"] = first_copy.get("section", None)
                details["call_number"] = first_copy.get("call_number", None)
                details["barcode"] = first_copy.get("barcode", None)
                details["branch"] = first_copy.get("branch", None)
                # Store full exemplare list for reference
                details["exemplare"] = exemplare_info
            else:
                details["availability"] = "Unknown"
                details["location"] = None
                details["call_number"] = None
                details["barcode"] = None
                details["branch"] = None
                details["exemplare"] = []

            # Extract description (full summary text)
            description = self._extract_description(soup)
            details["description"] = description

            # Extract cover image
            cover_elem = soup.find("img", class_=["cover", "thumbnail"])
            if not cover_elem:
                # Try alternative selector for book cover
                cover_elem = soup.find("img", src=re.compile(r".*cover.*|.*cover.*"))
            details["cover_url"] = cover_elem.get("src") if cover_elem else None

            # Build full URL for detail page if not present
            details["url"] = None  # Will be set by caller if needed

            return details

        except Exception as e:
            self.logger.error(f"Error parsing book details: {e}", exc_info=True)
            return {}
