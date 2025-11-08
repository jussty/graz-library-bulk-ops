"""WebOPAC scraper for Stadtbibliothek Graz catalog"""

import time
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .parser import CatalogParser
from ..models.book import Book, SearchResult
from ..utils.logger import get_logger
from ..utils.config import Config
from ..utils.validators import validate_search_query

logger = get_logger(__name__)


class WebOPACScraper:
    """Scraper for WebOPAC-based catalog (Stadtbibliothek Graz)"""

    def __init__(self, base_url: str = Config.LIBRARY_BASE_URL):
        """Initialize the scraper

        Args:
            base_url: Base URL of the library website
        """
        self.base_url = base_url
        self.search_url = f"{base_url}/"  # DNN-based site uses POST to root
        self.parser = CatalogParser()
        self.logger = logger
        self.last_request_time = 0
        self.session = self._create_session()
        self.viewstate = None  # ASP.NET ViewState for form submissions

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Setup retry strategy
        retry_strategy = Retry(
            total=Config.REQUEST_RETRY_ATTEMPTS,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set user agent
        session.headers.update(
            {
                "User-Agent": Config.BROWSER_USER_AGENT,
                "Accept-Language": "de-AT,de;q=0.9",
            }
        )

        return session

    def _respect_rate_limit(self) -> None:
        """Respect rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < Config.RATE_LIMIT_DELAY:
            sleep_time = Config.RATE_LIMIT_DELAY - elapsed
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _get_cache_key(self, query: str, search_type: str) -> str:
        """Generate cache key for search query

        Args:
            query: Search query
            search_type: Type of search

        Returns:
            Cache key string
        """
        return f"{search_type}_{query.lower().replace(' ', '_')}"

    def _load_from_cache(self, cache_key: str) -> Optional[SearchResult]:
        """Load search results from cache

        Args:
            cache_key: Cache key

        Returns:
            SearchResult or None if not in cache or expired
        """
        try:
            cache_path = Config.get_cache_path(cache_key)

            if not cache_path.exists():
                return None

            # Check if cache is expired
            file_mtime = cache_path.stat().st_mtime
            cache_age = time.time() - file_mtime

            if cache_age > Config.CACHE_TTL:
                self.logger.debug(f"Cache expired for {cache_key}")
                return None

            # Load from cache
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Reconstruct SearchResult from cached data
            books = [Book(**book_data) for book_data in data.get("books", [])]
            result = SearchResult(
                query=data["query"],
                books=books,
                total_results=data["total_results"],
                search_type=data["search_type"],
            )

            self.logger.info(f"Loaded {len(books)} results from cache for '{data['query']}'")
            return result

        except Exception as e:
            self.logger.warning(f"Error loading from cache: {e}")
            return None

    def _save_to_cache(self, cache_key: str, result: SearchResult) -> None:
        """Save search results to cache

        Args:
            cache_key: Cache key
            result: SearchResult to cache
        """
        try:
            cache_path = Config.get_cache_path(cache_key)

            data = {
                "query": result.query,
                "search_type": result.search_type,
                "total_results": result.total_results,
                "books": [book.to_dict() for book in result.books],
            }

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Cached search results for '{result.query}'")

        except Exception as e:
            self.logger.warning(f"Error saving to cache: {e}")

    def _get_viewstate(self) -> Optional[dict]:
        """Extract ASP.NET ViewState and other form values from the library page

        Returns:
            Dictionary with form values needed for POST, or None if failed
        """
        try:
            from bs4 import BeautifulSoup

            response = self.session.get(self.base_url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.find('form')

            if not form:
                self.logger.warning("Could not find form on library page")
                return None

            # Extract all hidden inputs and form fields
            form_data = {}
            for inp in form.find_all('input'):
                name = inp.get('name')
                value = inp.get('value', '')
                if name:
                    form_data[name] = value

            self.logger.debug(f"Extracted {len(form_data)} form fields")
            return form_data

        except Exception as e:
            self.logger.warning(f"Error extracting ViewState: {e}")
            return None

    def search(
        self,
        query: str,
        search_type: str = "keyword",
        use_cache: bool = True,
        page: int = 1,
    ) -> Optional[SearchResult]:
        """Search the library catalog

        Args:
            query: Search query
            search_type: Type of search (keyword, author, title, isbn)
            use_cache: Whether to use cached results
            page: Page number for results (default: 1)

        Returns:
            SearchResult object or None if search fails
        """
        # Validate search query
        is_valid, error = validate_search_query(query)
        if not is_valid:
            self.logger.error(f"Invalid search query: {error}")
            return None

        # Check cache
        cache_key = self._get_cache_key(query, search_type)
        if use_cache:
            cached_result = self._load_from_cache(cache_key)
            if cached_result:
                return cached_result

        # Perform search
        self.logger.info(f"Searching for '{query}' (type: {search_type})")

        try:
            start_time = time.time()

            # Respect rate limiting
            self._respect_rate_limit()

            # Build search URL based on search type
            # The library uses direct URLs for searches: /Mediensuche/Einfache-Suche?search=...
            search_endpoint = f"{self.base_url}/Mediensuche/Einfache-Suche"

            if search_type == "title":
                search_url = f"{search_endpoint}?title={query}"
            elif search_type == "author":
                search_url = f"{search_endpoint}?author={query}"
            elif search_type == "isbn":
                search_url = f"{search_endpoint}?isbn={query}"
            else:  # keyword (default)
                search_url = f"{search_endpoint}?search={query}"

            self.logger.debug(f"Search URL: {search_url}")

            # Make GET request to search page
            response = self.session.get(
                search_url,
                timeout=Config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            # Parse results
            books = self.parser.parse_search_results(response.text)

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

            # Save to cache
            self._save_to_cache(cache_key, result)

            return result

        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return None

    def search_by_author(self, author: str, **kwargs) -> Optional[SearchResult]:
        """Search by author

        Args:
            author: Author name
            **kwargs: Additional arguments for search()

        Returns:
            SearchResult or None
        """
        return self.search(author, search_type="author", **kwargs)

    def search_by_title(self, title: str, **kwargs) -> Optional[SearchResult]:
        """Search by title

        Args:
            title: Book title
            **kwargs: Additional arguments for search()

        Returns:
            SearchResult or None
        """
        return self.search(title, search_type="title", **kwargs)

    def search_by_isbn(self, isbn: str, **kwargs) -> Optional[SearchResult]:
        """Search by ISBN

        Args:
            isbn: ISBN (10 or 13 digit)
            **kwargs: Additional arguments for search()

        Returns:
            SearchResult or None
        """
        return self.search(isbn, search_type="isbn", **kwargs)

    def clear_cache(self, query: Optional[str] = None) -> None:
        """Clear cache for a query or all cache

        Args:
            query: Specific query to clear, or None to clear all
        """
        try:
            if query:
                cache_key = self._get_cache_key(query, "keyword")
                cache_path = Config.get_cache_path(cache_key)
                if cache_path.exists():
                    cache_path.unlink()
                    self.logger.info(f"Cleared cache for '{query}'")
            else:
                # Clear all cache
                for cache_file in Config.CACHE_DIR.glob("*.cache"):
                    cache_file.unlink()
                self.logger.info("Cleared all cache")

        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")

    def close(self) -> None:
        """Close the session"""
        self.session.close()
        self.logger.debug("Scraper session closed")
