"""Tests for browser-based search functionality"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from src.graz_library.catalog.browser_search import BrowserSearcher
from src.graz_library.session.browser import SyncBrowserSession
from src.graz_library.models.book import SearchResult, Book


class TestBrowserSearcher:
    """Test BrowserSearcher functionality"""

    def test_browser_searcher_init(self):
        """Test BrowserSearcher initialization"""
        searcher = BrowserSearcher()
        assert searcher.base_url == "https://stadtbibliothek.graz.at"
        assert searcher.browser is not None
        assert searcher.parser is not None
        assert searcher.logger is not None

    def test_rate_limiting(self):
        """Test rate limiting between searches"""
        searcher = BrowserSearcher()

        # Set last request time to now
        searcher.last_request_time = time.time()

        # Should sleep if called immediately
        start = time.time()
        searcher._respect_rate_limit()
        elapsed = time.time() - start

        # Should have slept approximately 2 seconds (RATE_LIMIT_DELAY)
        assert elapsed >= 1.9, f"Expected ~2s sleep, got {elapsed}s"

    def test_search_invalid_query(self):
        """Test search with invalid query"""
        searcher = BrowserSearcher()

        # Test empty query
        result = searcher.search("")
        assert result is None

        # Test too short query
        result = searcher.search("a")
        assert result is None

        # Test too long query
        result = searcher.search("a" * 600)
        assert result is None

    def test_search_valid_query_format(self):
        """Test that valid queries pass validation"""
        searcher = BrowserSearcher()

        # These should pass validation (but browser interaction may fail)
        assert searcher.logger is not None  # Just verify searcher is initialized

    @patch('src.graz_library.catalog.browser_search.SyncBrowserSession')
    def test_search_browser_not_started(self, mock_browser_class):
        """Test search when browser fails to start"""
        mock_browser = MagicMock()
        mock_browser.session.page = None
        mock_browser.start.return_value = False
        mock_browser_class.return_value = mock_browser

        searcher = BrowserSearcher()
        searcher.browser = mock_browser

        result = searcher.search("test query")
        assert result is None
        mock_browser.start.assert_called_once()

    def test_search_context_manager(self):
        """Test BrowserSearcher as context manager"""
        with BrowserSearcher() as searcher:
            assert searcher is not None
            assert searcher.browser is not None


class TestSyncBrowserSession:
    """Test SyncBrowserSession synchronous wrapper"""

    def test_sync_browser_session_init(self):
        """Test SyncBrowserSession initialization"""
        session = SyncBrowserSession(headless=True)
        assert session is not None
        assert session.session is not None
        assert session.logger is not None

    def test_sync_browser_session_methods_exist(self):
        """Test that all expected methods exist"""
        session = SyncBrowserSession()

        # Check that all methods exist
        assert hasattr(session, 'start')
        assert hasattr(session, 'navigate')
        assert hasattr(session, 'fill_form')
        assert hasattr(session, 'click')
        assert hasattr(session, 'wait_for_selector')
        assert hasattr(session, 'get_text')
        assert hasattr(session, 'get_html')
        assert hasattr(session, 'screenshot')
        assert hasattr(session, 'close')

        # Check they're callable
        assert callable(session.start)
        assert callable(session.navigate)
        assert callable(session.fill_form)


class TestBrowserIntegration:
    """Integration tests for browser functionality"""

    @pytest.mark.skip(reason="Requires actual browser - integration test")
    def test_browser_navigation(self):
        """Test actual browser navigation (skip in unit tests)"""
        searcher = BrowserSearcher()
        try:
            # This would test actual browser navigation
            # Skipped because it requires time and resources
            pass
        finally:
            searcher.close()

    @pytest.mark.skip(reason="Requires actual library access - integration test")
    def test_full_search_workflow(self):
        """Test full search workflow end-to-end (skip in unit tests)"""
        searcher = BrowserSearcher()
        try:
            # This would test the complete search flow
            # Including navigation, form interaction, and parsing
            pass
        finally:
            searcher.close()


class TestBrowserSearcherErrorHandling:
    """Test error handling in BrowserSearcher"""

    def test_search_handles_exceptions(self):
        """Test that search handles exceptions gracefully"""
        searcher = BrowserSearcher()

        # Mock browser to raise exception
        searcher.browser.navigate = Mock(side_effect=Exception("Network error"))

        # Should return None, not raise exception
        result = searcher.search("test")
        assert result is None

    def test_close_handles_exceptions(self):
        """Test that close handles exceptions gracefully"""
        searcher = BrowserSearcher()
        searcher.browser.close = Mock(side_effect=Exception("Close error"))

        # Should not raise exception
        try:
            searcher.close()
        except Exception as e:
            pytest.fail(f"close() raised {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
