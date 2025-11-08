#!/usr/bin/env python
"""Test script to verify books exist using external sources"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graz_library.operations.external_search import ExternalBookSearcher
from graz_library.utils.logger import get_logger

logger = get_logger(__name__)

# Books to verify
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


def verify_books_external():
    """Verify books exist using external sources"""
    searcher = ExternalBookSearcher()

    print("\n" + "=" * 120)
    print("EXTERNAL BOOK VERIFICATION")
    print("Verifying if books exist in Google Books, Open Library, or WorldCat")
    print("=" * 120 + "\n")

    results = []

    for i, title in enumerate(BOOKS, 1):
        print(f"[{i:2d}/{len(BOOKS)}] Verifying: {title}")

        try:
            # Search externally
            external_results = searcher.search_book_external(title)

            if external_results:
                first_result = external_results[0]
                print(f"  ✓ FOUND on {first_result.get('source', 'N/A')}")

                if first_result.get('author') not in [None, 'N/A', '']:
                    print(f"    Author: {first_result.get('author', 'N/A')}")
                if first_result.get('isbn') not in [None, 'N/A', '']:
                    print(f"    ISBN: {first_result.get('isbn', 'N/A')}")
                else:
                    print(f"    ISBN: N/A")
                if first_result.get('published') not in [None, 'N/A', '']:
                    print(f"    Published: {first_result.get('published', 'N/A')}")
                if first_result.get('pages') not in [None, 'N/A', '']:
                    print(f"    Pages: {first_result.get('pages', 'N/A')}")
                if first_result.get('url'):
                    print(f"    More Info: {first_result.get('url', 'N/A')[:70]}...")

                results.append({
                    "title": title,
                    "exists": True,
                    "source": first_result.get('source', 'N/A'),
                    "author": first_result.get('author', 'N/A'),
                    "isbn": first_result.get('isbn', 'N/A'),
                    "published": first_result.get('published', 'N/A')
                })
            else:
                print(f"  ✗ NOT FOUND in external sources")

                results.append({
                    "title": title,
                    "exists": False,
                    "source": "Not Found",
                    "author": "N/A",
                    "isbn": "N/A",
                    "published": "N/A"
                })

        except KeyboardInterrupt:
            print("\n\nVerification interrupted by user")
            break
        except Exception as e:
            print(f"  ✗ Error: {e}")
            logger.exception(f"Error verifying '{title}'")
            results.append({
                "title": title,
                "exists": False,
                "source": "Error",
                "author": "N/A",
                "isbn": "N/A",
                "published": "N/A"
            })

    # Print summary table
    print("\n" + "=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print(f"{'Title':<45} {'Exists':<12} {'Source':<25} {'Author':<25} {'ISBN':<15}")
    print("-" * 120)

    for result in results:
        title = result["title"][:42] + "..." if len(result["title"]) > 45 else result["title"]
        exists = "✓ Yes" if result["exists"] else "✗ No"
        source = result["source"][:22] if result["source"] else "N/A"
        author = result["author"][:22] + "..." if len(result["author"]) > 25 else result["author"]
        isbn = result["isbn"][:12] if result["isbn"] else "N/A"
        print(f"{title:<45} {exists:<12} {source:<25} {author:<25} {isbn:<15}")

    # Statistics
    print("-" * 120)
    found_count = sum(1 for r in results if r["exists"])
    not_found = sum(1 for r in results if not r["exists"])

    print(f"\nTotal: {len(BOOKS)}")
    print(f"Found in External Sources: {found_count}")
    print(f"Not Found Anywhere: {not_found}")
    print("=" * 120 + "\n")


if __name__ == "__main__":
    verify_books_external()
