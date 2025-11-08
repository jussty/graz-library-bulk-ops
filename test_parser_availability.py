#!/usr/bin/env python
"""Test script to search for books and display availability"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graz_library.catalog.browser_search import BrowserSearcher
from graz_library.catalog.parser import CatalogParser
from graz_library.utils.logger import get_logger

logger = get_logger(__name__)

# Books to search for
BOOKS = [
    "Die Flügelpferde von Sternenhall",
    "Die Ponys von Lillasund: Winterzauber im Stall",
    "Dragon Girls: Rosie, der Zünddrache",
    "Das Geheimnis der Luchse",
    "Eulenzauber Junior: Goldwing und Mondscheinpony",
    "Die Schule der magischen Tiere",
    "PS: Du bist ein Geschenk!",
    "Endlich 13: jetzt ist starke ich richtig durch",
    "Wirbel um das Weihnachtspony",
    "Wilder Lauf der Wald",
    "Jahresmarkt der Zeitreisenden - Der gestohlene Kristall",
]


def test_book_availability():
    """Search for books and display availability"""
    searcher = BrowserSearcher()

    print("\n" + "=" * 80)
    print("BOOK AVAILABILITY REPORT")
    print("=" * 80 + "\n")

    results = []

    for i, title in enumerate(BOOKS, 1):
        print(f"[{i:2d}/{len(BOOKS)}] Searching: {title}")

        try:
            # Search for the book - returns SearchResult with books list
            search_result = searcher.search(title)
            if not search_result or not search_result.books:
                print(f"  ✗ No search results")
                results.append({
                    "title": title,
                    "found": False,
                    "availability": "N/A",
                    "branch": "N/A",
                    "copies": 0
                })
                continue

            # Get first book from results
            book = search_result.books[0]
            availability = book.availability or "Unknown"
            branch = book.location or "Unknown"

            print(f"  ✓ Found: {book.title}")
            print(f"    Availability: {availability}")
            print(f"    Branch: {branch}")
            print(f"    ISBN: {book.isbn or 'N/A'}")

            results.append({
                "title": title,
                "found": True,
                "availability": availability,
                "branch": branch,
                "copies": len(search_result.books)
            })

        except KeyboardInterrupt:
            print("\n\nSearch interrupted by user")
            searcher.close()
            break
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                "title": title,
                "found": False,
                "availability": "Error",
                "branch": "N/A",
                "copies": 0
            })

    # Print summary table
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Title':<50} {'Availability':<15} {'Branch':<15}")
    print("-" * 80)

    for result in results:
        title = result["title"][:47] + "..." if len(result["title"]) > 50 else result["title"]
        avail = result["availability"]
        branch = result["branch"]
        print(f"{title:<50} {avail:<15} {branch:<15}")

    # Statistics
    print("-" * 80)
    found_count = sum(1 for r in results if r["found"])
    available_count = sum(1 for r in results if r["availability"] == "Available")
    print(f"\nTotal: {len(BOOKS)} | Found: {found_count} | Available: {available_count}")
    print("=" * 80 + "\n")

    # Close browser
    try:
        searcher.close()
    except:
        pass


if __name__ == "__main__":
    test_book_availability()
