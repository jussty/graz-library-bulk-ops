# Graz Library Bulk Operations Tool - Execution Plan

## Project Goals
1. Create a Python tool for bulk operations at Stadtbibliothek Graz
2. Support book search, reservations, and mail orders
3. Handle batch operations from CSV/JSON files
4. Provide a clean CLI interface

## Phase 1: Project Foundation (Milestone: Initial Setup) ✅ COMPLETE
- [x] Research library system and APIs
- [x] Create project repository
- [x] Set up git configuration
- [x] Create project structure
- [x] Initialize Python package structure
- [x] Create requirements.txt
- [x] Create setup.py
- [x] Create .gitignore

**Status**: COMPLETE - All foundational infrastructure in place
**Commits**:
- "chore: initialize project structure and configuration"
- "docs: add book list and project documentation"

## Phase 2: Core Infrastructure (Milestone: Scraper Ready) ✅ COMPLETE
- [x] Create data models (Book, Reservation, SearchResult)
- [x] Implement WebOPAC scraper base class
- [x] Create HTML parser utilities
- [x] Implement search functionality
- [x] Add logging and error handling
- [x] Write unit tests for scraper
- [x] Add external book search (Open Library, Google Books, WorldCat)

**Status**: COMPLETE - Full search infrastructure with HTML parsing and external verification
**Key Implementations**:
- WebOPACScraper: Direct GET requests to `/Mediensuche/Einfache-Suche?search=<query>`
- Parser: CSS class discovery - uses `tosic-oclc-search-resultitem` with fallbacks
- ExternalBookSearcher: Multi-source verification (Open Library, Google Books, WorldCat)
- Test Results:
  - 1/11 books from test list found in Graz library ("Die Schule der magischen Tiere" - 10 copies)
  - 11/11 books verified to exist in world catalogs
  - WorldCat links provided for interlibrary loan requests

**Commits**:
- "feat: implement WebOPAC scraper and search functionality"
- "feat: enhance HTML parser with browser automation and detail pages"
- "fix: search scraper and parser for library's actual HTML structure"
- "feat: add external book search to verify book existence across public catalogs"
- "docs: enhance book search documentation with WorldCat links and external verification results"

## Phase 3: Browser Automation (Milestone: Interactive Ops Ready) ⏳ IN PROGRESS
- [x] Set up Playwright browser automation with Puppeteer MCP
- [ ] Implement session management
- [ ] Create login/authentication handler
- [ ] Implement reservation workflow
- [ ] Add rate limiting and respectful crawling
- [ ] Write integration tests

**Status**: IN PROGRESS - Browser automation framework tested and validated
**Key Work Done**:
- Evaluated and implemented Puppeteer MCP for browser automation
- Tested navigation and screenshot capabilities
- Discovered direct GET API pattern (more efficient than browser automation for search)
- Browser automation reserved for JavaScript-heavy pages and interactive operations

**Next Steps**:
- Implement session management for authenticated operations
- Build reservation workflow using browser automation
- Add error handling and retry logic

**Commit Message**: "feat: implement browser automation for reservations"

## Phase 4: Mail Order Integration (Milestone: All Operations Complete) ⏳ PENDING
- [ ] Implement mail order form submission
- [ ] Add email notification handling
- [ ] Create mail order request builder
- [ ] Implement library branch selection
- [ ] Add validation for mail orders
- [ ] Write tests for mail order flow

**Status**: PENDING - Ready to start after Phase 3 completes
**Estimated Timeline**: 2-3 hours

**Commit Message**: "feat: add mail order functionality and email integration"

## Phase 5: CLI and Batch Operations (Milestone: CLI Complete) ⏳ PENDING
- [ ] Create Click/Typer CLI framework
- [ ] Implement search command
- [ ] Implement reserve command
- [ ] Implement mail-order command
- [ ] Create bulk/batch command
- [ ] Add CSV/JSON import support
- [ ] Create example files

**Status**: PENDING - Ready to start after Phases 3-4 complete
**Estimated Timeline**: 3-4 hours

**Commit Message**: "feat: add CLI interface and batch operation support"

## Phase 6: Documentation and Polish (Milestone: Release Ready) ⏳ PENDING
- [ ] Write API documentation
- [ ] Create usage guide
- [ ] Create setup guide
- [ ] Add architecture documentation
- [ ] Create example scripts
- [ ] Add README sections for each command
- [ ] Full test coverage (target: 80%+)
- [ ] Add error handling and user-friendly messages

**Status**: PENDING - Final phase after Phases 3-5 complete
**Estimated Timeline**: 2-3 hours

**Commit Message**: "docs: add comprehensive documentation and examples"

## Implementation Details

### Phase 2: Core Infrastructure
**Tasks:**
1. Create `src/graz_library/models/book.py` with Book, SearchResult classes
2. Create `src/graz_library/catalog/scraper.py` with WebOPACScraper class
3. Create `src/graz_library/catalog/parser.py` with HTML parsing utilities
4. Create `src/graz_library/operations/search.py` with search logic
5. Create `src/graz_library/utils/logger.py` for logging
6. Create comprehensive unit tests

**Key Decisions:**
- Use BeautifulSoup for HTML parsing (lightweight)
- Use requests for HTTP calls
- Implement rate limiting (2s delay between requests)
- Cache search results locally to respect library resources

### Phase 3: Browser Automation
**Tasks:**
1. Setup Playwright (faster than Selenium, no Java dependency)
2. Create `src/graz_library/session/browser.py` with session management
3. Implement login logic (if library requires authentication)
4. Create reservation workflow in `src/graz_library/operations/reservation.py`
5. Add retry logic and error handling

**Key Decisions:**
- Use Playwright for browser automation (Chromium engine)
- Implement headless mode for performance
- Add screenshots on error for debugging
- Implement exponential backoff for retries

### Phase 4: Mail Order Integration
**Tasks:**
1. Create `src/graz_library/operations/mail_order.py`
2. Implement form submission workflow
3. Create email notification handler
4. Add validation for mail order requirements

**Key Decisions:**
- Support mail orders to library branches and postal offices
- Email confirmation if available
- Validate email addresses and book information

### Phase 5: CLI
**Tasks:**
1. Use Click framework for CLI (simpler than Typer)
2. Create main CLI group in `src/graz_library/cli.py`
3. Implement commands: search, reserve, mail-order, bulk
4. Add batch file processing (CSV/JSON)
5. Create output formatting (table, JSON, CSV)

**Key Decisions:**
- Support CSV and JSON input formats
- Output results as table (default) or JSON
- Progress bars for batch operations
- Colored output for readability

### Phase 6: Documentation
**Key Documents:**
1. **API.md** - Function and class documentation
2. **SETUP.md** - Installation and configuration guide
3. **USAGE.md** - Command examples and workflows
4. **ARCHITECTURE.md** - System design and components

## Testing Strategy

### Unit Tests
- Models (data validation)
- Parsers (HTML extraction)
- Validators (input validation)

### Integration Tests
- WebOPAC scraper with sample HTML
- Browser automation workflows
- Batch operations

### Manual Testing
- End-to-end book search
- Reservation workflow (test library account)
- Mail order submission

## Success Criteria
- [ ] All core operations working (search, reserve, mail-order)
- [ ] CLI interface complete with all major commands
- [ ] 80%+ test coverage
- [ ] Documentation complete
- [ ] Respectful crawling (rate limiting, error handling)
- [ ] User-friendly error messages
- [ ] Batch operations support (CSV/JSON)

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Library blocks scraper | High | Rate limiting, respectful crawling, user-agent rotation |
| HTML structure changes | High | Regular testing, notification system, graceful degradation |
| Authentication required | Medium | Implement login flow, session management |
| Rate limits exceeded | Medium | Implement delays, caching, batch request queuing |
| Browser automation flakiness | Medium | Retry logic, explicit waits, screenshots on failure |

## Progress Summary

### Completed Work
- **Phase 1**: COMPLETE (Project foundation, git, package structure)
- **Phase 2**: COMPLETE (Full search infrastructure, HTML parsing, external verification)
  - WebOPACScraper with direct GET API discovery
  - HTML parser with CSS class detection and fallbacks
  - ExternalBookSearcher with multi-source verification
  - Test results: 1/11 books in Graz, 11/11 verified globally

### In Progress
- **Phase 3**: IN PROGRESS (Browser automation setup)
  - Puppeteer MCP framework tested and working
  - Direct GET pattern discovered (more efficient for search)
  - Ready for authenticated operations and reservations

### Pending
- **Phase 4**: Mail order integration (2-3 hours)
- **Phase 5**: CLI interface (3-4 hours)
- **Phase 6**: Final documentation (2-3 hours)

## Timeline Estimate
- Phase 1: 1 hour (completed)
- Phase 2: 6-8 hours (completed)
- Phase 3: 3-4 hours (in progress)
- Phase 4: 2-3 hours (pending)
- Phase 5: 3-4 hours (pending)
- Phase 6: 2-3 hours (pending)

**Total: 17-25 hours of development** (7-8 hours completed, 8-14 hours remaining)
