"""Configuration management for Graz Library tool"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application"""

    # Paths
    BASE_DIR = Path(__file__).parent.parent.parent.parent
    DATA_DIR = Path.home() / ".graz-library" / "data"
    CACHE_DIR = DATA_DIR / "cache"
    CONFIG_DIR = Path.home() / ".graz-library" / "config"

    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Library configuration
    LIBRARY_BASE_URL = "https://stadtbibliothek.graz.at"
    LIBRARY_SEARCH_URL = "https://stadtbibliothek.graz.at/Mediensuche/"
    LIBRARY_CATALOG_URL = "https://stadtbibliothek.graz.at/Mediensuche/"

    # Browser configuration
    BROWSER_HEADLESS = True
    BROWSER_TIMEOUT = 30000  # 30 seconds
    BROWSER_VIEWPORT = {"width": 1280, "height": 720}
    BROWSER_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    # Scraper configuration
    REQUEST_TIMEOUT = 10
    REQUEST_RETRY_ATTEMPTS = 3
    REQUEST_RETRY_DELAY = 2  # seconds
    RATE_LIMIT_DELAY = 2  # seconds between requests
    CACHE_TTL = 3600  # 1 hour in seconds

    # Search configuration
    DEFAULT_SEARCH_TYPE = "keyword"  # keyword, author, title, isbn
    MAX_SEARCH_RESULTS = 100
    DEFAULT_LANGUAGE = "de"  # German

    # Email configuration
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None

    # Logging configuration
    LOG_LEVEL = "INFO"

    @classmethod
    def load_env(cls) -> None:
        """Load environment variables from .env file"""
        env_path = Path.home() / ".graz-library" / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # Override class attributes with environment variables
        cls.LIBRARY_BASE_URL = os.getenv("LIBRARY_BASE_URL", cls.LIBRARY_BASE_URL)
        cls.BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        cls.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", cls.REQUEST_TIMEOUT))
        cls.RATE_LIMIT_DELAY = int(os.getenv("RATE_LIMIT_DELAY", cls.RATE_LIMIT_DELAY))
        cls.LOG_LEVEL = os.getenv("LOG_LEVEL", cls.LOG_LEVEL)
        cls.SMTP_SERVER = os.getenv("SMTP_SERVER")
        cls.SMTP_PORT = int(os.getenv("SMTP_PORT", cls.SMTP_PORT))
        cls.SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        cls.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        cls.MAIL_FROM = os.getenv("MAIL_FROM")

    @classmethod
    def get_cache_path(cls, key: str) -> Path:
        """Get cache file path for a given key"""
        return cls.CACHE_DIR / f"{key}.cache"

    @classmethod
    def get_config_path(cls, filename: str) -> Path:
        """Get config file path"""
        return cls.CONFIG_DIR / filename


# Load environment configuration on module import
Config.load_env()
