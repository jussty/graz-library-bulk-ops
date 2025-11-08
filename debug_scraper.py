#!/usr/bin/env python
"""Debug script to see what HTML we're actually getting from search"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graz_library.catalog.scraper import WebOPACScraper
from graz_library.utils.logger import get_logger

logger = get_logger(__name__)

def debug_search():
    """Debug search to see raw HTML"""
    scraper = WebOPACScraper()

    # Try searching for a famous book
    query = "Harry Potter"
    print(f"\nSearching for: {query}\n")

    try:
        # Get the viewstate and form data
        form_data = scraper._get_viewstate()
        if not form_data:
            print("ERROR: Could not get form data")
            return

        # Build search URL directly instead of using form POST
        search_endpoint = f"{scraper.base_url}/Mediensuche/Einfache-Suche"
        search_url = f"{search_endpoint}?search={query}"

        print(f"Search URL: {search_url}")

        # Make GET request
        response = scraper.session.get(
            search_url,
            timeout=10
        )
        response.raise_for_status()

        html = response.text
        print(f"Response HTML size: {len(html)} bytes")

        # Look for common result container patterns
        print("\n--- Checking for result patterns ---")

        patterns = [
            ('div.result-item', 'div', 'result-item'),
            ('div.hit', 'div', 'hit'),
            ('div.result', 'div', 'result'),
            ('div.result-entry', 'div', 'result-entry'),
            ('tr.record', 'tr', 'record'),
            ('li.record', 'li', 'record'),
            ('div.record', 'div', 'record'),
        ]

        for pattern_name, tag, cls in patterns:
            if f'<{tag} class="{cls}"' in html or f'<{tag} class="{cls} ' in html:
                print(f"✓ Found pattern: {pattern_name}")
            else:
                print(f"✗ Not found: {pattern_name}")

        # Show a sample of the HTML around search results
        print("\n--- HTML snippet (first 3000 chars after body) ---")
        body_start = html.find("<body")
        if body_start > 0:
            snippet = html[body_start:body_start+3000]
            print(snippet[:2000])
            print("\n... [truncated] ...\n")

        # Save full HTML for inspection
        debug_file = "/tmp/debug_search_results.html"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Full HTML saved to: {debug_file}")

    except Exception as e:
        print(f"Error: {e}")
        logger.exception("Debug error")

if __name__ == "__main__":
    debug_search()
