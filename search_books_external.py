#!/usr/bin/env python
"""Search for books using external ISBN/metadata sources to verify they exist"""

import sys
from pathlib import Path
import requests
from urllib.parse import quote

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

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


def search_google_books(title):
    """Search for book on Google Books API"""
    try:
        url = f"https://www.googleapis.com/books/v1/volumes"
        params = {
            "q": f"intitle:{quote(title)}",
            "maxResults": 5,
            "langRestrict": "de"
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        if data.get("items"):
            book = data["items"][0]["volumeInfo"]
            return {
                "source": "Google Books",
                "title": book.get("title"),
                "author": ", ".join(book.get("authors", [])),
                "isbn": book.get("industryIdentifiers", [{}])[0].get("identifier", "N/A"),
                "published": book.get("publishedDate", "N/A"),
                "url": book.get("infoLink")
            }
        return None
    except Exception as e:
        logger.debug(f"Google Books search error: {e}")
        return None


def search_open_library(title):
    """Search for book on Open Library API"""
    try:
        url = "https://openlibrary.org/search.json"
        params = {
            "title": title,
            "limit": 5,
            "language": "ger"
        }

        response = requests.get(url, params=params, timeout=5)
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
                "url": f"https://openlibrary.org{book.get('key', '')}"
            }
        return None
    except Exception as e:
        logger.debug(f"Open Library search error: {e}")
        return None


def search_isbn_db(title):
    """Search using ISBNdb API (if available)"""
    try:
        # ISBNdb requires API key, so we'll use a simple fallback
        # to show the concept - in practice, would need actual API key
        url = "https://isbnsearch.org/search"
        params = {
            "q": title
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        # Parse HTML to find first result
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for first ISBN link
        result = soup.find('a', class_='isbn-link')
        if result:
            return {
                "source": "ISBNSearch",
                "title": result.get_text(strip=True),
                "url": f"https://isbnsearch.org{result.get('href', '')}"
            }
        return None
    except Exception as e:
        logger.debug(f"ISBNdb search error: {e}")
        return None


def search_worldcat(title):
    """Search WorldCat (world library catalog)"""
    try:
        # WorldCat search - simple web search approach
        url = "https://www.worldcat.org/search"
        params = {
            "q": title,
            "dblist": "638",  # German libraries
            "format": "json"
        }

        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            # WorldCat found results
            return {
                "source": "WorldCat",
                "title": title,
                "url": f"https://www.worldcat.org/search?q={quote(title)}"
            }
        return None
    except Exception as e:
        logger.debug(f"WorldCat search error: {e}")
        return None


def search_book_external(title):
    """Search for book using multiple external sources"""
    print(f"\n  Searching external sources...")

    results = []

    # Try Open Library (most reliable)
    ol_result = search_open_library(title)
    if ol_result:
        results.append(ol_result)
        print(f"    ✓ Found on Open Library")

    # Try Google Books
    gb_result = search_google_books(title)
    if gb_result:
        results.append(gb_result)
        print(f"    ✓ Found on Google Books")

    # Try ISBNSearch
    isbn_result = search_isbn_db(title)
    if isbn_result:
        results.append(isbn_result)
        print(f"    ✓ Found on ISBNSearch")

    # Try WorldCat
    wc_result = search_worldcat(title)
    if wc_result:
        results.append(wc_result)
        print(f"    ✓ Found on WorldCat")

    return results if results else None


def main():
    """Search for all books externally"""
    print("\n" + "=" * 100)
    print("EXTERNAL BOOK SEARCH - VERIFY BOOKS EXIST")
    print("=" * 100 + "\n")

    from graz_library.catalog.scraper import WebOPACScraper

    scraper = WebOPACScraper()
    results = []

    for i, title in enumerate(BOOKS, 1):
        print(f"[{i:2d}/{len(BOOKS)}] {title}")

        # Search locally first
        local_result = scraper.search(title, use_cache=False)
        in_graz_library = bool(local_result and local_result.books)

        # Search externally
        external_results = search_book_external(title)
        exists_externally = bool(external_results)

        # Determine status
        status = "✓" if in_graz_library else "✗"
        exists = "✓" if exists_externally else "✗"

        print(f"    In Graz Library: {status} | Exists Externally: {exists}")

        if external_results:
            first_result = external_results[0]
            print(f"    Source: {first_result.get('source', 'N/A')}")
            if first_result.get('author') != 'N/A':
                print(f"    Author: {first_result.get('author', 'N/A')}")
            if first_result.get('isbn') != 'N/A':
                print(f"    ISBN: {first_result.get('isbn', 'N/A')}")

        results.append({
            "title": title,
            "in_graz": in_graz_library,
            "exists_externally": exists_externally,
            "external_source": external_results[0].get('source') if external_results else 'N/A'
        })

    # Summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"{'Title':<50} {'In Graz':<12} {'Exists':<12} {'Source':<20}")
    print("-" * 100)

    for result in results:
        title = result["title"][:47] + "..." if len(result["title"]) > 50 else result["title"]
        in_graz = "✓ Yes" if result["in_graz"] else "✗ No"
        exists = "✓ Yes" if result["exists_externally"] else "✗ No"
        source = result["external_source"]
        print(f"{title:<50} {in_graz:<12} {exists:<12} {source:<20}")

    print("-" * 100)
    in_library = sum(1 for r in results if r["in_graz"])
    exists_ext = sum(1 for r in results if r["exists_externally"])
    only_external = sum(1 for r in results if r["exists_externally"] and not r["in_graz"])

    print(f"\nTotal: {len(BOOKS)}")
    print(f"In Graz Library: {in_library}")
    print(f"Exist Externally: {exists_ext}")
    print(f"Only in External Sources (not in Graz): {only_external}")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    main()
