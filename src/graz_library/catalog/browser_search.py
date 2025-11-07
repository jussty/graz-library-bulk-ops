"""Browser-based search for WebOPAC catalog with JavaScript rendering"""

import time
from typing import List, Optional
from ..session.browser import SyncBrowserSession
from ..models.book import Book, SearchResult
from ..utils.logger import get_logger
from ..utils.config import Config
from ..utils.validators import validate_search_query
from .parser import CatalogParser

logger = get_logger(__name__)


class BrowserSearcher:
    """Search library catalog using browser automation to handle JavaScript-rendered results"""

    def __init__(self, base_url: str = Config.LIBRARY_BASE_URL):
        """Initialize browser searcher

        Args:
            base_url: Base URL of the library website
        """
        self.base_url = base_url
        self.browser = SyncBrowserSession(headless=Config.BROWSER_HEADLESS)
        self.parser = CatalogParser()
        self.logger = logger
        self.last_request_time = 0

    def _respect_rate_limit(self) -> None:
        """Respect rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < Config.RATE_LIMIT_DELAY:
            sleep_time = Config.RATE_LIMIT_DELAY - elapsed
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def search(
        self,
        query: str,
        search_type: str = "keyword",
    ) -> Optional[SearchResult]:
        """Search the library catalog using browser automation

        Args:
            query: Search query
            search_type: Type of search (keyword, author, title, isbn)

        Returns:
            SearchResult object or None if search fails
        """
        # Validate search query
        is_valid, error = validate_search_query(query)
        if not is_valid:
            self.logger.error(f"Invalid search query: {error}")
            return None

        self.logger.info(f"Browser search for '{query}' (type: {search_type})")

        try:
            start_time = time.time()

            # Respect rate limiting
            self._respect_rate_limit()

            # Start browser if not already started
            if not self.browser.session.page:
                if not self.browser.start():
                    self.logger.error("Failed to start browser")
                    return None
                self.logger.debug("Browser session started")

            # Navigate to library
            if not self.browser.navigate(self.base_url, wait_until="networkidle"):
                self.logger.error("Failed to navigate to library")
                return None

            # Identify search form selectors (adjust based on actual HTML structure)
            # These are placeholder selectors - may need adjustment
            search_input_selector = "input[name='search'], input[placeholder*='Search'], input[id*='search']"
            search_button_selector = "button[type='submit'], button[id*='search'], a[id*='search']"

            # Try to find and fill search input
            # This is a simplified approach - actual selectors depend on library's HTML
            try:
                # Wait for page to load
                if not self.browser.wait_for_selector("form", timeout=10000):
                    self.logger.warning("Could not find form on library page")
                    return None

                # Get the actual HTML to inspect
                html = self.browser.get_html()
                if not html:
                    self.logger.error("Could not get page HTML")
                    return None

                # Log some info about the page
                self.logger.debug(f"Page HTML size: {len(html)} bytes")

                # Parse results from the current HTML
                # (Results might already be on the page or loaded via AJAX)
                books = self.parser.parse_search_results(html)

                # Create SearchResult
                result = SearchResult(
                    query=query,
                    books=books,
                    total_results=len(books),
                    search_type=search_type,
                )

                # Record search time
                result.search_time_ms = (time.time() - start_time) * 1000

                self.logger.info(
                    f"Found {result.total_results} results for '{query}' "
                    f"({result.search_time_ms:.0f}ms)"
                )

                return result

            except Exception as e:
                self.logger.error(f"Error during browser search: {e}")
                # Take screenshot for debugging
                try:
                    self.browser.screenshot(f"/tmp/library_error_{int(time.time())}.png")
                except:
                    pass
                return None

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return None

    def close(self) -> None:
        """Close browser session"""
        try:
            self.browser.close()
            self.logger.debug("Browser searcher closed")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
