# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Graz Library Bulk Operations Tool is a Python application for automating book search, reservations, and mail orders at Stadtbibliothek Graz (https://stadtbibliothek.graz.at/). Since the library has no official public API, the tool uses web scraping and browser automation to interact with the library's WebOPAC-based catalog system.

## Quick Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browser drivers (required for browser automation)
python -m playwright install chromium

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_browser_search.py -v

# Run with coverage
pytest --cov=src tests/
```

## Architecture

### Core Components

**1. Catalog Module** (`src/graz_library/catalog/`)
- `scraper.py`: WebOPACScraper - HTTP-based scraping of library catalog
  - Uses POST requests with ASP.NET ViewState parameters
  - Implements search caching (1-hour TTL)
  - Rate limiting (2s between requests)
  - Retry logic with exponential backoff

- `parser.py`: CatalogParser - HTML parsing and data extraction
  - Extracts book metadata from search results
  - Parses ISBN, availability, location information
  - Handles multiple result formats

- `browser_search.py`: BrowserSearcher - Browser automation for JavaScript-rendered results
  - Uses Playwright for browser automation
  - Fills search form and navigates to results
  - Extracts HTML from rendered pages
  - Form selectors validated via Puppeteer MCP:
    - Input: `input[placeholder="Ihre Suche"]`
    - Button: `button.app-minitools-search-btn`

**2. Models Module** (`src/graz_library/models/`)
- `book.py`: Data classes for domain models
  - `Book`: Full book information including metadata from detail pages
    - Basic fields: title, author, isbn, publisher, publication_year, medium_type
    - Detail page fields: series, language, original_title, page_count, keywords, barcode, branch
    - Availability fields: availability, location, call_number, catalog_id
    - Web fields: description, cover_url, url

  - `SearchResult`: Container for search results with timing
  - `Reservation`: Book reservation with branch and notification info
  - `MailOrder`: Mail order request with delivery/pickup options

**3. Session Module** (`src/graz_library/session/`)
- `browser.py`: Browser automation wrappers
  - `BrowserSession`: Async Playwright implementation
    - Methods: start(), navigate(), fill_form(), click(), wait_for_selector(), get_html(), screenshot(), close()

  - `SyncBrowserSession`: Synchronous wrapper using asyncio.run()
    - Provides synchronous interface for the async BrowserSession
    - Used by BrowserSearcher for compatibility with synchronous code

**4. Operations Module** (`src/graz_library/operations/`)
- `search.py`: SearchOperation for batch searches
  - CSV/JSON import support
  - Caching of results
  - Export to multiple formats
  - File-based filtering

- `reservation.py`: Reservation operations (stub)
  - Requires authentication (modal appears on button click)
  - Uses ASP.NET postback mechanism (`__doPostBack()`)

- `mail_order.py`: Mail order operations (stub)
  - Requires form discovery (direct /Mediensuche/Postservice returns 404)
  - Needs authenticated session context

**5. Utils Module** (`src/graz_library/utils/`)
- `config.py`: Configuration management
  - Class-based config with default values
  - Environment variable overrides via .env
  - Paths: `~/.graz-library/` for data, cache, config
  - Browser settings: headless mode, viewport, user agent
  - Scraper settings: timeouts, rate limiting, cache TTL

- `logger.py`: Centralized logging with file and console output
  - Uses Python's standard logging module
  - Logs to console and `~/.graz-library/logs/`

- `validators.py`: Input validation for email, ISBN, phone, search queries

## Key Findings from Investigation

### Search Workflow (✅ Validated)
1. Navigate to https://stadtbibliothek.graz.at/
2. Handle cookie consent modal (Cookiebot)
3. Fill search input with query
4. Click search button
5. Page navigates to `/Mediensuche/Einfache-Suche?search=<QUERY>`
6. Extract HTML and parse results

### Detail Page Information (✅ Validated)
- URL: `/Mediensuche/Einfache-Suche?search=<QUERY>&detail=1`
- Expandable "Mehr Informationen" section contains full metadata
- Exemplare (copies) table shows branch-specific availability
- All fields in Book model are extractable from detail pages

### Reservation Flow (⚠️ Requires Authentication)
- Button: "Vorbestellen" (Reserve) - `tosic-oclc-btn-reserve` class
- Action: Clicking triggers login modal
- Modal message: "Sie müssen angemeldet sein, um fortzufahren"
- Mechanism: ASP.NET postback with `__doPostBack('...BtnReserve','')`
- Status: Requires user authentication flow before proceeding

### Mail Order Service (⚠️ Not Directly Accessible)
- Button: "Medium auf die Postliste setzen" (Add to Waitlist)
- Direct URL: `/Mediensuche/Postservice` returns 404
- Possible solutions:
  - May require book context/parameters in URL
  - May require authenticated session
  - Could need to be accessed from detail page with proper context

## Testing Strategy

**Unit Tests** (`tests/test_browser_search.py`)
- 10 passing unit tests for initialization, validation, timing, error handling
- 2 skipped integration tests (require actual browser/library access)

**Test Execution**
```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_browser_search.py::TestBrowserSearcher -v

# Run with detailed output
pytest tests/test_browser_search.py -vv -s
```

**Manual Testing via Puppeteer MCP**
- All critical form selectors validated against live website
- Search, detail page navigation, and metadata extraction confirmed
- Action buttons identified and behavior documented

## Configuration

Configuration is managed through two methods:

1. **Code Defaults** (in `config.py`)
   - Library URLs, browser settings, timeouts, rate limiting

2. **Environment Variables** (via `~/.graz-library/.env`)
   ```
   LIBRARY_BASE_URL=https://stadtbibliothek.graz.at
   BROWSER_HEADLESS=true
   REQUEST_TIMEOUT=10
   RATE_LIMIT_DELAY=2
   LOG_LEVEL=INFO
   SMTP_SERVER=<your_smtp_server>
   SMTP_PORT=587
   SMTP_USERNAME=<your_email>
   SMTP_PASSWORD=<your_password>
   MAIL_FROM=<your_email>
   ```

## Development Workflow

### When Starting a New Task

1. **Check the investigation documents** for relevant findings:
   - `INVESTIGATION_COMPLETE.md`: Full investigation summary
   - `BROWSER_AUTOMATION_FINDINGS.md`: Form selector validation
   - `BOOK_DETAIL_PAGE_ANALYSIS.md`: Metadata structure
   - `DETAIL_PAGE_ACTIONS_AND_AVAILABILITY.md`: Button details
   - `PUPPETEER_INVESTIGATION_SUMMARY.md`: Test results

2. **Run tests first** to ensure nothing broke
   ```bash
   pytest tests/ -v
   ```

3. **Check git status** and recent commits
   ```bash
   git log --oneline -10
   git status
   ```

### When Implementing Features

1. **Update models first** if adding new fields to books/reservations
   - Verify field mappings against library page structure
   - Update `to_dict()` methods for serialization

2. **Update parser** if extracting new information
   - Test with actual HTML from library pages
   - Reference investigation documents for field locations

3. **Use browser automation** for JavaScript-rendered content
   - BrowserSearcher for search results
   - Detail page expansion for metadata

4. **Implement with auth-awareness**
   - Reservation requires login modal handling
   - Mail order service requires form discovery

### When Fixing Issues

1. **Check investigation findings** - errors may be documented
2. **Use Puppeteer MCP** for live website testing if needed
   - Quick validation without full Playwright testing
   - Works with live selectors and forms
3. **Update documentation** if findings change
4. **Commit with detailed messages** - reference investigation phases

## Important Implementation Notes

### Form Selectors (Validated via Puppeteer)
```python
# Search form
search_input = "input[placeholder='Ihre Suche']"  # NOT wildcard
search_button = "button.app-minitools-search-btn"  # NOT :has-text()

# Reservation
reserve_link = "a.tosic-oclc-btn-reserve"  # Triggers login modal

# Mail order
mail_button = "a"  # Text: "Medium auf die Postliste setzen"
mail_url = "/Mediensuche/Postservice"  # Returns 404, needs context
```

### Browser Timing
- Fill to click: 0.3 seconds minimum
- Click to navigation: 1 second minimum for page load
- Navigation wait: Use `wait_until="networkidle"` for reliability

### ASP.NET Form Handling
- Hidden ViewState fields required for POST requests
- Postback mechanism uses `__doPostBack()` JavaScript function
- Library uses DNN (DotNetNuke) framework

### Rate Limiting
- Respect 2-second delay between requests (configured in `Config.RATE_LIMIT_DELAY`)
- Implement exponential backoff for retries
- Cache search results (1-hour TTL default)

## Git Workflow

**Commit messages should reference investigation phases:**
```
Validate and fix browser automation with Puppeteer MCP testing
Expand Book model with library detail page metadata
Complete Puppeteer MCP investigation of library website
```

**Recent commits:** Run `git log --oneline` to see implementation history

## Remaining Implementation Tasks

1. **Update parser** - Extract all detail page metadata
2. **Implement authenticated reservation** - Handle login modal and postback
3. **Implement mail order** - Discover form structure and submission
4. **Add CLI interface** - Click-based command structure
5. **Add bulk operations** - CSV/JSON import for batch processing

## Resources

- **Library Website**: https://stadtbibliothek.graz.at/
- **Investigation Documents**: See root directory for `*.md` files
- **Test Files**: `tests/test_browser_search.py`
- **Example Data**: `examples/` directory
- **Project Plan**: `PROJECT_PLAN.md`
