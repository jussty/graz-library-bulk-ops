# Graz Library Bulk Operations Tool

⚠️ **Work in Progress (WIP)** - This project is under active development. Features and APIs may change.

A comprehensive Python tool for automating book search, reservations, and mail orders at Stadtbibliothek Graz (Graz City Library).

## Project Overview

This tool provides a command-line interface for bulk operations at Austria's Stadtbibliothek Graz, enabling:

- **Book Search**: Query the library catalog by title, author, ISBN, or keywords
- **Bulk Reservations**: Reserve multiple books at once
- **Mail Order Integration**: Submit bulk mail orders for in-person pickup or delivery
- **Batch Operations**: Process lists of books from CSV/JSON files
- **External Verification**: Verify book existence in world catalogs (Open Library, Google Books, WorldCat)

## Current Status

### Completed ✅
- Book search functionality with WebOPAC scraper
- HTML parser with CSS class detection and fallbacks
- External book search via Open Library, Google Books, and WorldCat
- Test infrastructure for local and external verification
- **Test Results**: 1/11 test books in Graz library, 11/11 verified in world catalogs

### In Progress ⏳
- Browser automation framework setup (Puppeteer)
- Session management for authenticated operations

### Planned 📋
- Reservation workflow
- Mail order integration
- CLI interface
- Batch operations support
- Documentation and examples

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed roadmap and current progress.

## Research Summary

### Library System
- **Catalog System**: WebOPAC-based catalog at https://stadtbibliothek.graz.at/
- **Collections**: ~300,000 items across 7 branches + media center + bookmobile
- **Search Interface**: Simple and Advanced search available through web interface
- **API Access**: No official public API documented; RSS feeds API available through Austria's open data portal

### Technical Approach
Since no official API is available, this tool uses:
1. **Web scraping** of the WebOPAC catalog (with rate limiting and respect for robots.txt)
2. **Browser automation** (Selenium) for interactive operations (reservations, mail orders)
3. **Session management** for authenticated operations
4. **CSV/JSON import** for batch operations

## Installation

```bash
git clone https://github.com/yourusername/graz-library-bulk-ops.git
cd graz-library-bulk-ops
pip install -r requirements.txt
```

## Usage

```bash
# Search for books
python -m graz_library search --title "Harry Potter"

# Bulk search from file
python -m graz_library search --file books.csv

# Reserve books
python -m graz_library reserve --isbn 978-0547928227

# Bulk operations
python -m graz_library bulk --operation reserve --file list.csv --library-branch "Zanklhof"

# Mail order
python -m graz_library mail-order --title "Book Title" --email "user@example.at"
```

## Project Structure

```
graz-library-bulk-ops/
├── src/
│   └── graz_library/
│       ├── __init__.py
│       ├── cli.py                 # Command-line interface
│       ├── catalog/
│       │   ├── __init__.py
│       │   ├── scraper.py         # WebOPAC scraper
│       │   └── parser.py          # HTML parsing utilities
│       ├── operations/
│       │   ├── __init__.py
│       │   ├── search.py          # Search operations
│       │   ├── reservation.py     # Reservation operations
│       │   └── mail_order.py      # Mail order operations
│       ├── session/
│       │   ├── __init__.py
│       │   └── browser.py         # Browser automation session
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── config.py          # Configuration management
│       │   ├── logger.py          # Logging utilities
│       │   └── validators.py      # Input validation
│       └── models/
│           ├── __init__.py
│           └── book.py            # Data models (Book, Reservation, etc.)
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│   ├── test_operations.py
│   └── test_models.py
├── examples/
│   ├── books.csv                  # Example CSV for bulk search
│   ├── reservations.json          # Example JSON for reservations
│   └── batch_operations.csv       # Example batch file
├── docs/
│   ├── API.md                     # API documentation
│   ├── SETUP.md                   # Setup guide
│   ├── USAGE.md                   # Usage guide
│   └── ARCHITECTURE.md            # Architecture overview
├── requirements.txt
├── setup.py
├── .gitignore
└── PROJECT_PLAN.md
```

## Execution Plan

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed step-by-step implementation plan.

## License

MIT License

## Contributing

Contributions welcome. Please ensure respectful use of the library system.

## Contact

For questions about Stadtbibliothek Graz:
- Phone: +43 316 872-800
- Email: stadtbibliothek@stadt.graz.at
- Website: https://www.stadtbibliothek.graz.at/
