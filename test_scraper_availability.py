#!/usr/bin/env python
"""Test script to search for books using scraper and display availability"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graz_library.catalog.scraper import WebOPACScraper
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
    scraper = WebOPACScraper()

    print("\n" + "=" * 100)
    print("BOOK AVAILABILITY REPORT (via Scraper)")
    print("=" * 100 + "\n")

    results = []

    for i, title in enumerate(BOOKS, 1):
        print(f"[{i:2d}/{len(BOOKS)}] Searching: {title}")

        try:
            # Search for the book
            search_result = scraper.search(title)
            if not search_result or not search_result.books:
                print(f"  ✗ No search results")
                results.append({
                    "title": title,
                    "found": False,
                    "availability": "N/A",
                    "branch": "N/A",
                    "author": "N/A",
                    "copies": 0
                })
                continue

            # Get first book from results
            book = search_result.books[0]
            availability = book.availability or "Unknown"
            branch = book.location or "Unknown"
            author = book.author or "Unknown"

            print(f"  ✓ Found: {book.title}")
            print(f"    Author: {author}")
            print(f"    Availability: {availability}")
            print(f"    Branch: {branch}")
            print(f"    Medium: {book.medium_type}")
            print(f"    ISBN: {book.isbn or 'N/A'}")
            print(f"    Total copies found in search: {len(search_result.books)}")

            results.append({
                "title": title,
                "found": True,
                "availability": availability,
                "branch": branch,
                "author": author,
                "copies": len(search_result.books)
            })

        except KeyboardInterrupt:
            print("\n\nSearch interrupted by user")
            break
        except Exception as e:
            print(f"  ✗ Error: {e}")
            logger.exception(f"Error searching for '{title}'")
            results.append({
                "title": title,
                "found": False,
                "availability": "Error",
                "branch": "N/A",
                "author": "N/A",
                "copies": 0
            })

    # Print summary table
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"{'Title':<40} {'Author':<20} {'Availability':<15} {'Branch':<15}")
    print("-" * 100)

    for result in results:
        title = result["title"][:37] + "..." if len(result["title"]) > 40 else result["title"]
        author = result["author"][:17] + "..." if len(result["author"]) > 20 else result["author"]
        avail = result["availability"]
        branch = result["branch"]
        print(f"{title:<40} {author:<20} {avail:<15} {branch:<15}")

    # Statistics
    print("-" * 100)
    found_count = sum(1 for r in results if r["found"])
    available_count = sum(1 for r in results if r["availability"] == "Available")
    print(f"\nTotal: {len(BOOKS)} | Found: {found_count} | Available: {available_count}")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    test_book_availability()
