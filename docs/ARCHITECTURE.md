# Architecture Overview

This document describes the architecture and design of the Graz Library Bulk Operations Tool.

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│          Command Line Interface (CLI)               │
│            (Click Framework)                        │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│   Operations     │  │   Session        │
│ - Search        │  │ - BrowserSession │
│ - Reservation   │  │ - Authentication │
│ - Mail Order    │  │ - Page Interaction
└────────┬─────────┘  └──────────────────┘
        │                     │
        │     ┌───────────────┴──────┐
        │     │                      │
        ▼     ▼                      ▼
┌──────────────────────────────────────────┐
│         Catalog Module                   │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   Scraper    │  │   Parser     │    │
│  │  (Requests)  │  │(BeautifulSoup)   │
│  └──────────────┘  └──────────────┘    │
└────────────┬─────────────────────────────┘
             │
    ┌────────┴──────────┐
    │                   │
    ▼                   ▼
┌──────────────┐  ┌──────────────┐
│   Cache      │  │   Models     │
│  (JSON)      │  │  - Book      │
│              │  │  - Result    │
│              │  │  - Reservation
│              │  │  - MailOrder │
└──────────────┘  └──────────────┘
    │
    ▼
┌──────────────────────────┐
│  Library Catalog         │
│  (Stadtbibliothek Graz)  │
└──────────────────────────┘
```

## Components

### 1. CLI Layer (`cli.py`)

**Purpose**: Command-line interface for user interaction

**Responsibilities**:
- Parse command-line arguments
- Route commands to appropriate operations
- Format and display results
- Handle user input validation

**Technologies**: Click framework

### 2. Operations Layer

#### SearchOperation (`operations/search.py`)
- Execute search queries
- Load/save from files (CSV, JSON)
- Export results
- Batch processing

#### ReservationOperation (`operations/reservation.py`)
- Reserve books
- Manage reservations
- Cancel reservations

#### MailOrderOperation (`operations/mail_order.py`)
- Create mail orders
- Submit to library
- Track orders

### 3. Catalog Layer

#### WebOPACScraper (`catalog/scraper.py`)
**Responsibilities**:
- HTTP communication with library website
- Request/response handling
- Rate limiting and retry logic
- Session management
- Cache management

**Features**:
- Automatic retry with exponential backoff
- Rate limiting (2 second delay between requests)
- Result caching (1 hour TTL)
- User-agent spoofing

#### CatalogParser (`catalog/parser.py`)
**Responsibilities**:
- Parse HTML responses
- Extract book information
- Data normalization

**Parsing**:
- Search result pages
- Book detail pages
- Availability status
- Location/branch information

### 4. Session Layer (`session/browser.py`)

**Purpose**: Browser automation for interactive operations

**Responsibilities**:
- Launch browser instance
- Navigate to pages
- Fill forms
- Click buttons
- Wait for elements
- Take screenshots

**Technologies**: Playwright (async-based)

### 5. Models Layer (`models/book.py`)

**Data Classes**:
- `Book`: Represents a catalog item
- `SearchResult`: Container for search results
- `Reservation`: Reservation tracking
- `MailOrder`: Mail order request

**Properties**:
- Validation on initialization
- Serialization to dict/JSON
- String representations

### 6. Utils Layer

#### Logger (`utils/logger.py`)
- Centralized logging
- File and console output
- Configurable log levels

#### Config (`utils/config.py`)
- Centralized configuration
- Environment variable loading
- Path management

#### Validators (`utils/validators.py`)
- Email validation
- ISBN-10/ISBN-13 validation
- Phone validation
- Search query validation

## Data Flow

### Search Operation Flow

```
User Input (CLI)
    ↓
SearchOperation.search()
    ↓
WebOPACScraper.search()
    ├─ Check Cache
    │   ├─ Found → Return cached result
    │   └─ Not found → Continue
    ├─ Rate Limit Check (wait if needed)
    ├─ HTTP GET request to library
    ├─ Parse HTML response
    ├─ Extract Book objects
    └─ Save to cache
    ↓
SearchResult object
    ↓
CLI Formatter
    ↓
User Output (table, JSON, CSV)
```

### Reservation Flow (Phase 3)

```
User Input (CLI)
    ↓
ReservationOperation.reserve_book()
    ↓
BrowserSession.start()
    ├─ Launch browser
    └─ Navigate to library
    ↓
Library Login (if required)
    ├─ Fill credentials
    └─ Submit form
    ↓
Search for book
    ├─ Find book in catalog
    └─ Navigate to book page
    ↓
Submit Reservation
    ├─ Fill reservation form
    ├─ Select pickup location
    └─ Submit form
    ↓
Reservation object
    ↓
User Confirmation
```

## Design Patterns

### 1. Factory Pattern
- `SearchOperation()` creates `WebOPACScraper()`
- Operations manage their own resource creation

### 2. Strategy Pattern
- Different search types (keyword, author, title, isbn)
- Pluggable parser strategies

### 3. Singleton-like Pattern
- Logger instances shared across modules
- Configuration loaded once, accessed everywhere

### 4. Repository Pattern
- Cache layer abstracts data storage
- Potential for swapping storage backends

## Error Handling

### Request Errors
- Automatic retry with backoff
- Timeout handling
- Connection error logging

### Parsing Errors
- Graceful degradation (skip problematic items)
- Detailed logging of parse failures
- HTML structure change detection

### User Input Errors
- Validation before processing
- Clear error messages
- Suggestions for correction

## Caching Strategy

### Cache Key Generation
```
"{search_type}_{query_lowercase_with_underscores}"
```

### Cache TTL
- Default: 3600 seconds (1 hour)
- Configurable via environment variable

### Cache Storage
- Location: `~/.graz-library/data/cache/`
- Format: JSON files
- Automatic cleanup (manual clear command available)

## Configuration Management

### Loading Order
1. Default values in Config class
2. Environment variables (override defaults)
3. .env file in `~/.graz-library/` (loaded via dotenv)

### Key Configuration Variables
- `LIBRARY_BASE_URL`: Library website base URL
- `RATE_LIMIT_DELAY`: Delay between requests
- `REQUEST_TIMEOUT`: HTTP request timeout
- `CACHE_TTL`: Cache time-to-live
- `LOG_LEVEL`: Logging verbosity
- `BROWSER_HEADLESS`: Browser headless mode

## Security Considerations

### 1. Rate Limiting
- Prevents overwhelming library servers
- Respectful crawling practices

### 2. User-Agent Spoofing
- Identifies as a standard web browser
- Respects robots.txt (future implementation)

### 3. Credential Security
- Credentials not logged
- Session data not exposed
- No credential storage (user provides on-demand)

### 4. Input Validation
- All user inputs validated
- Prevention of injection attacks
- Sanitization of search terms

## Scalability Considerations

### 1. Async/Await (Future)
- BrowserSession uses async (Playwright)
- Can handle concurrent operations
- Potential for asyncio-based CLI

### 2. Batch Processing
- Bulk operations in single run
- Progress tracking for large operations
- Memory-efficient streaming (when needed)

### 3. Database (Future)
- Could replace JSON cache with SQLite
- Track reservation/mail order history
- User preferences storage

## Testing Strategy

### Unit Tests
- Models validation
- Validators functionality
- Parser accuracy

### Integration Tests
- Scraper with sample HTML
- File I/O operations
- Caching mechanism

### End-to-End Tests
- Full search workflow
- File import/export
- Result verification

## Dependencies

### Core
- `requests`: HTTP library
- `beautifulsoup4`: HTML parsing
- `lxml`: XML/HTML processing
- `click`: CLI framework

### Browser Automation
- `playwright`: Cross-platform browser automation

### Development
- `pytest`: Testing framework
- `black`: Code formatting
- `mypy`: Type checking

## Future Enhancements

1. **Async CLI**: Use asyncio for concurrent operations
2. **Database**: SQLite for history and user data
3. **Authentication**: Login support for reservations
4. **Email Notifications**: Send confirmations to users
5. **Web API**: REST API alongside CLI
6. **Web UI**: Web interface for GUI users
7. **Webhook Support**: Real-time availability notifications
8. **Internationalization**: Multi-language support (German, English)
