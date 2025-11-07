"""Browser automation session management with Playwright"""

import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page
from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


class BrowserSession:
    """Manages browser automation sessions with Playwright"""

    def __init__(self, headless: bool = Config.BROWSER_HEADLESS):
        """Initialize browser session

        Args:
            headless: Whether to run in headless mode
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.logger = logger

    async def start(self) -> bool:
        """Start browser session

        Returns:
            True if successful, False otherwise
        """
        try:
            self.playwright = await async_playwright().start()

            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless
            )

            # Create page with viewport
            self.page = await self.browser.new_page(
                viewport=Config.BROWSER_VIEWPORT
            )

            # Set user agent
            await self.page.set_extra_http_headers({
                "User-Agent": Config.BROWSER_USER_AGENT
            })

            self.logger.info("Browser session started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error starting browser session: {e}")
            return False

    async def navigate(self, url: str, wait_until: str = "networkidle") -> bool:
        """Navigate to a URL

        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete
                       (load, domcontentloaded, networkidle)

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.logger.error("Browser page not initialized")
                return False

            await self.page.goto(url, wait_until=wait_until, timeout=Config.BROWSER_TIMEOUT)
            self.logger.debug(f"Navigated to {url}")
            return True

        except Exception as e:
            self.logger.error(f"Error navigating to {url}: {e}")
            return False

    async def fill_form(self, selector: str, value: str) -> bool:
        """Fill a form field

        Args:
            selector: CSS selector for the field
            value: Value to fill

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.logger.error("Browser page not initialized")
                return False

            await self.page.fill(selector, value)
            self.logger.debug(f"Filled {selector} with '{value}'")
            return True

        except Exception as e:
            self.logger.error(f"Error filling form field {selector}: {e}")
            return False

    async def click(self, selector: str) -> bool:
        """Click an element

        Args:
            selector: CSS selector for the element

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.logger.error("Browser page not initialized")
                return False

            await self.page.click(selector)
            self.logger.debug(f"Clicked {selector}")
            return True

        except Exception as e:
            self.logger.error(f"Error clicking {selector}: {e}")
            return False

    async def wait_for_selector(self, selector: str, timeout: int = 5000) -> bool:
        """Wait for an element to appear

        Args:
            selector: CSS selector to wait for
            timeout: Timeout in milliseconds

        Returns:
            True if element appeared, False otherwise
        """
        try:
            if not self.page:
                self.logger.error("Browser page not initialized")
                return False

            await self.page.wait_for_selector(selector, timeout=timeout)
            self.logger.debug(f"Element found: {selector}")
            return True

        except Exception as e:
            self.logger.warning(f"Timeout waiting for selector {selector}: {e}")
            return False

    async def get_text(self, selector: str) -> Optional[str]:
        """Get text content of an element

        Args:
            selector: CSS selector

        Returns:
            Text content or None if not found
        """
        try:
            if not self.page:
                self.logger.error("Browser page not initialized")
                return None

            text = await self.page.text_content(selector)
            if text:
                self.logger.debug(f"Got text from {selector}: {text[:50]}...")
            return text

        except Exception as e:
            self.logger.warning(f"Error getting text from {selector}: {e}")
            return None

    async def get_html(self) -> Optional[str]:
        """Get current page HTML

        Returns:
            HTML content or None if error
        """
        try:
            if not self.page:
                self.logger.error("Browser page not initialized")
                return None

            html = await self.page.content()
            self.logger.debug(f"Retrieved page HTML ({len(html)} bytes)")
            return html

        except Exception as e:
            self.logger.error(f"Error getting page HTML: {e}")
            return None

    async def screenshot(self, path: str) -> bool:
        """Take a screenshot

        Args:
            path: Path to save screenshot

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.logger.error("Browser page not initialized")
                return False

            await self.page.screenshot(path=path)
            self.logger.info(f"Screenshot saved to {path}")
            return True

        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return False

    async def close(self) -> None:
        """Close browser session"""
        try:
            if self.page:
                await self.page.close()
                self.page = None

            if self.browser:
                await self.browser.close()
                self.browser = None

            if self.playwright:
                await self.playwright.stop()
                self.playwright = None

            self.logger.info("Browser session closed")

        except Exception as e:
            self.logger.error(f"Error closing browser session: {e}")

    def __del__(self):
        """Cleanup on deletion"""
        if self.browser or self.page:
            self.logger.warning(
                "BrowserSession not properly closed. Call close() explicitly."
            )


class SyncBrowserSession:
    """Synchronous wrapper for BrowserSession using asyncio"""

    def __init__(self, headless: bool = Config.BROWSER_HEADLESS):
        """Initialize synchronous browser session

        Args:
            headless: Whether to run in headless mode
        """
        self.session = BrowserSession(headless=headless)
        self.logger = logger

    def start(self) -> bool:
        """Start browser session (synchronous)

        Returns:
            True if successful, False otherwise
        """
        try:
            return asyncio.run(self.session.start())
        except Exception as e:
            self.logger.error(f"Error starting browser: {e}")
            return False

    def navigate(self, url: str, wait_until: str = "networkidle") -> bool:
        """Navigate to a URL (synchronous)

        Args:
            url: URL to navigate to
            wait_until: When to consider navigation complete

        Returns:
            True if successful, False otherwise
        """
        try:
            return asyncio.run(self.session.navigate(url, wait_until=wait_until))
        except Exception as e:
            self.logger.error(f"Error navigating: {e}")
            return False

    def fill_form(self, selector: str, value: str) -> bool:
        """Fill a form field (synchronous)

        Args:
            selector: CSS selector for the field
            value: Value to fill

        Returns:
            True if successful, False otherwise
        """
        try:
            return asyncio.run(self.session.fill_form(selector, value))
        except Exception as e:
            self.logger.error(f"Error filling form: {e}")
            return False

    def click(self, selector: str) -> bool:
        """Click an element (synchronous)

        Args:
            selector: CSS selector for the element

        Returns:
            True if successful, False otherwise
        """
        try:
            return asyncio.run(self.session.click(selector))
        except Exception as e:
            self.logger.error(f"Error clicking: {e}")
            return False

    def wait_for_selector(self, selector: str, timeout: int = 5000) -> bool:
        """Wait for an element to appear (synchronous)

        Args:
            selector: CSS selector to wait for
            timeout: Timeout in milliseconds

        Returns:
            True if element appeared, False otherwise
        """
        try:
            return asyncio.run(self.session.wait_for_selector(selector, timeout))
        except Exception as e:
            self.logger.error(f"Error waiting for selector: {e}")
            return False

    def get_text(self, selector: str) -> Optional[str]:
        """Get text content of an element (synchronous)

        Args:
            selector: CSS selector

        Returns:
            Text content or None if not found
        """
        try:
            return asyncio.run(self.session.get_text(selector))
        except Exception as e:
            self.logger.error(f"Error getting text: {e}")
            return None

    def get_html(self) -> Optional[str]:
        """Get current page HTML (synchronous)

        Returns:
            HTML content or None if error
        """
        try:
            return asyncio.run(self.session.get_html())
        except Exception as e:
            self.logger.error(f"Error getting HTML: {e}")
            return None

    def screenshot(self, path: str) -> bool:
        """Take a screenshot (synchronous)

        Args:
            path: Path to save screenshot

        Returns:
            True if successful, False otherwise
        """
        try:
            return asyncio.run(self.session.screenshot(path))
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return False

    def close(self) -> None:
        """Close browser session (synchronous)"""
        try:
            asyncio.run(self.session.close())
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")
