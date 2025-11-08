#!/usr/bin/env python
"""Test parser with known books that exist in the library"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graz_library.catalog.scraper import WebOPACScraper
from graz_library.utils.logger import get_logger

logger = get_logger(__name__)

# Books we know exist in the library from our Puppeteer investigation
KNOWN_BOOKS = [
    "Harry Potter",
    "Herr der Ringe",
    "Die Bibel",
    "Das Hobbit",
]


def test_known_books():
    """Search for known books and display results"""
    scraper = WebOPACScraper()

    print("\n" + "=" * 100)
    print("KNOWN BOOKS AVAILABILITY TEST")
    print("=" * 100 + "\n")

    results = []

    for i, title in enumerate(KNOWN_BOOKS, 1):
        print(f"[{i:2d}/{len(KNOWN_BOOKS)}] Searching: {title}")

        try:
            search_result = scraper.search(title)
            if not search_result or not search_result.books:
                print(f"  ✗ No search results")
                results.append({
                    "title": title,
                    "found": False,
                    "count": 0,
                    "first_result": "N/A",
                    "availability": "N/A"
                })
                continue

            # Show results
            print(f"  ✓ Found {len(search_result.books)} results")
            for j, book in enumerate(search_result.books[:3], 1):
                avail = book.availability or "Unknown"
                print(f"     {j}. {book.title[:60]} [{avail}]")

            # First result
            first_book = search_result.books[0]
            results.append({
                "title": title,
                "found": True,
                "count": len(search_result.books),
                "first_result": first_book.title,
                "availability": first_book.availability or "Unknown"
            })

        except Exception as e:
            print(f"  ✗ Error: {e}")
            logger.exception(f"Error searching for '{title}'")
            results.append({
                "title": title,
                "found": False,
                "count": 0,
                "first_result": "Error",
                "availability": "Error"
            })

    # Print summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    for result in results:
        status = "✓" if result["found"] else "✗"
        print(f"{status} {result['title']:<30} Count: {result['count']:<5} [{result['availability']}]")

    print("=" * 100 + "\n")


if __name__ == "__main__":
    test_known_books()
