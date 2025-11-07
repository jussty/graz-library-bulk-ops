"""Catalog management - WebOPAC scraping and parsing"""

from .scraper import WebOPACScraper
from .parser import CatalogParser
from .browser_search import BrowserSearcher

__all__ = ["WebOPACScraper", "CatalogParser", "BrowserSearcher"]
