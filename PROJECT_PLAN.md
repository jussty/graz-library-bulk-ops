# Graz Library Bulk Operations Tool - Execution Plan

## Project Goals
1. Create a Python tool for bulk operations at Stadtbibliothek Graz
2. Support book search, reservations, and mail orders
3. Handle batch operations from CSV/JSON files
4. Provide a clean CLI interface

## Phase 1: Project Foundation (Milestone: Initial Setup)
- [x] Research library system and APIs
- [x] Create project repository
- [x] Set up git configuration
- [ ] Create project structure
- [ ] Initialize Python package structure
- [ ] Create requirements.txt
- [ ] Create setup.py
- [ ] Create .gitignore

**Commit Message**: "chore: initialize project structure and configuration"

## Phase 2: Core Infrastructure (Milestone: Scraper Ready)
- [ ] Create data models (Book, Reservation, SearchResult)
- [ ] Implement WebOPAC scraper base class
- [ ] Create HTML parser utilities
- [ ] Implement search functionality
- [ ] Add logging and error handling
- [ ] Write unit tests for scraper

**Commit Message**: "feat: implement WebOPAC scraper and search functionality"

## Phase 3: Browser Automation (Milestone: Interactive Ops Ready)
- [ ] Set up Selenium/Playwright browser automation
- [ ] Implement session management
- [ ] Create login/authentication handler
- [ ] Implement reservation workflow
- [ ] Add rate limiting and respectful crawling
- [ ] Write integration tests

**Commit Message**: "feat: implement browser automation for reservations"

## Phase 4: Mail Order Integration (Milestone: All Operations Complete)
- [ ] Implement mail order form submission
- [ ] Add email notification handling
- [ ] Create mail order request builder
- [ ] Implement library branch selection
- [ ] Add validation for mail orders
- [ ] Write tests for mail order flow

**Commit Message**: "feat: add mail order functionality and email integration"

## Phase 5: CLI and Batch Operations (Milestone: CLI Complete)
- [ ] Create Click/Typer CLI framework
- [ ] Implement search command
- [ ] Implement reserve command
- [ ] Implement mail-order command
- [ ] Create bulk/batch command
- [ ] Add CSV/JSON import support
- [ ] Create example files

**Commit Message**: "feat: add CLI interface and batch operation support"

## Phase 6: Documentation and Polish (Milestone: Release Ready)
- [ ] Write API documentation
- [ ] Create usage guide
- [ ] Create setup guide
- [ ] Add architecture documentation
- [ ] Create example scripts
- [ ] Add README sections for each command
- [ ] Full test coverage (target: 80%+)
- [ ] Add error handling and user-friendly messages

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

## Timeline Estimate
- Phase 1: 1 hour (completed)
- Phase 2: 4-6 hours
- Phase 3: 4-6 hours
- Phase 4: 2-3 hours
- Phase 5: 3-4 hours
- Phase 6: 2-3 hours

**Total: 16-23 hours of development**
