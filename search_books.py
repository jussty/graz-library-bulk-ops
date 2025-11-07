#!/usr/bin/env python3
"""
Search for books from books-to-search.md in Stadtbibliothek Graz catalog.
Uses external ISBN lookup to improve search accuracy.

This is a utility script for bulk book searching - not part of the main package.
"""

import sys
from pathlib import Path
import re
import time
import requests
from typing import List, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graz_library.operations.search import SearchOperation
from graz_library.models.book import Book, SearchResult
from graz_library.utils.logger import get_logger

logger = get_logger(__name__)


class ISBNLookup:
    """Look up ISBN from book title using external APIs"""

    # OpenLibrary API - free, no authentication needed
    OPENLIBRARY_SEARCH_API = "https://openlibrary.org/search.json"

    def __init__(self):
        """Initialize ISBN lookup"""
        self.session = requests.Session()
        self.session.timeout = 5

    def lookup_isbn(self, title: str, author: Optional[str] = None) -> Optional[str]:
        """Look up ISBN for a book title

        Args:
            title: Book title
            author: Author name (optional, improves accuracy)

        Returns:
            ISBN or None if not found
        """
        try:
            params = {"title": title}
            if author:
                params["author"] = author

            response = self.session.get(
                self.OPENLIBRARY_SEARCH_API,
                params=params,
                timeout=5
            )
            response.raise_for_status()

            data = response.json()
            docs = data.get("docs", [])

            if docs:
                # Get first result
                doc = docs[0]
                # Try to get ISBN-13 first, then ISBN-10
                isbn_list = doc.get("isbn", [])
                if isbn_list:
                    return isbn_list[0]

            return None

        except Exception as e:
            logger.warning(f"ISBN lookup failed for '{title}': {e}")
            return None

    def close(self):
        """Close session"""
        self.session.close()


def parse_book_list(file_path: Path) -> List[str]:
    """Parse book titles from markdown file

    Args:
        file_path: Path to markdown file

    Returns:
        List of book titles
    """
    titles = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and headers
                if not line or line.startswith("#"):
                    continue
                # Remove markdown list markers and number prefixes
                # Matches: "1. ", "- ", "* ", "1→ "
                cleaned = re.sub(r"^[\d]+[\.\)]\s*", "", line)  # "1. " or "1) "
                cleaned = re.sub(r"^[\d]+→\s*", "", cleaned)    # "1→ "
                cleaned = re.sub(r"^[\-\*]\s*", "", cleaned)    # "- " or "* "
                cleaned = cleaned.strip()
                if cleaned:
                    titles.append(cleaned)

        logger.info(f"Loaded {len(titles)} book titles from {file_path}")
        return titles

    except Exception as e:
        logger.error(f"Error reading book list: {e}")
        return []


def search_book_in_library(
    search_op: SearchOperation,
    title: str,
    isbn: Optional[str] = None,
) -> Optional[SearchResult]:
    """Search for a book in the library catalog

    Args:
        search_op: SearchOperation instance
        title: Book title
        isbn: ISBN (optional)

    Returns:
        SearchResult or None
    """
    # Try ISBN search first if available
    if isbn:
        logger.debug(f"Searching by ISBN: {isbn}")
        result = search_op.search(isbn, search_type="isbn", use_cache=False)
        if result and result.total_results > 0:
            return result

    # Fall back to title search
    logger.debug(f"Searching by title: {title}")
    result = search_op.search(title, search_type="title", use_cache=False)
    return result


def print_results(
    title: str,
    isbn: Optional[str],
    result: Optional[SearchResult]
) -> None:
    """Print search results in a readable format

    Args:
        title: Original book title
        isbn: ISBN if found
        result: SearchResult or None
    """
    isbn_str = f" (ISBN: {isbn})" if isbn else ""
    print(f"\n📚 {title}{isbn_str}")
    print("-" * 80)

    if not result or result.total_results == 0:
        print("  ❌ Not found in library catalog")
        return

    print(f"  ✓ Found {result.total_results} result(s)")

    for i, book in enumerate(result.books, 1):
        availability_icon = "✓" if "Available" in book.availability else "⏳"
        location = book.location or "Unknown location"
        print(f"\n  [{i}] {availability_icon} {book.availability}")
        print(f"      Location: {location}")
        if book.publication_year:
            print(f"      Published: {book.publication_year}")
        if book.medium_type and book.medium_type != "Book":
            print(f"      Type: {book.medium_type}")


def display_book_list_summary(titles: List[str]) -> None:
    """Display a summary of the books to search for

    Args:
        titles: List of book titles
    """
    print(f"\n📚 Books to search ({len(titles)} total):\n")
    for i, title in enumerate(titles, 1):
        print(f"   {i:2d}. {title}")
    print()


def main():
    """Main search function"""
    print("\n" + "=" * 80)
    print("GRAZ LIBRARY BOOK SEARCH - Greta's Reading List")
    print("=" * 80)

    # Find book list file (try multiple locations)
    potential_paths = [
        Path(__file__).parent / "books-to-search.md",
        Path(__file__).parent / "examples" / "books-to-search.md",
    ]

    book_list_file = None
    for path in potential_paths:
        if path.exists():
            book_list_file = path
            break

    if not book_list_file:
        print(f"\n❌ Error: books-to-search.md not found in project root or examples/")
        sys.exit(1)

    # Parse books
    titles = parse_book_list(book_list_file)
    if not titles:
        print("❌ No books found in file")
        sys.exit(1)

    # Display summary
    display_book_list_summary(titles)
    print("Searching for books...\n")

    # Initialize search and ISBN lookup
    search_op = SearchOperation()
    isbn_lookup = ISBNLookup()

    results_summary = {
        "total": len(titles),
        "found": 0,
        "available": 0,
        "not_found": 0,
    }

    try:
        for i, title in enumerate(titles, 1):
            print(f"[{i}/{len(titles)}] Searching for '{title}'...")

            # Look up ISBN
            isbn = isbn_lookup.lookup_isbn(title)
            if isbn:
                print(f"       → Found ISBN: {isbn}")
                time.sleep(0.5)  # Rate limit

            # Search in library
            result = search_book_in_library(search_op, title, isbn)

            # Print results
            print_results(title, isbn, result)

            # Update summary
            if result and result.total_results > 0:
                results_summary["found"] += 1
                for book in result.books:
                    if "Available" in book.availability:
                        results_summary["available"] += 1
            else:
                results_summary["not_found"] += 1

            # Rate limiting between requests
            time.sleep(1)

    finally:
        # Cleanup
        search_op.close()
        isbn_lookup.close()

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total books: {results_summary['total']}")
    print(f"Found in catalog: {results_summary['found']}")
    print(f"Available now: {results_summary['available']}")
    print(f"Not found: {results_summary['not_found']}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
