"""Catalog management - WebOPAC scraping and parsing"""

from .scraper import WebOPACScraper
from .parser import CatalogParser

__all__ = ["WebOPACScraper", "CatalogParser"]
