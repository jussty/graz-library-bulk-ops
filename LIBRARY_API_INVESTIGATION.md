# Stadtbibliothek Graz Library API Investigation

## Summary
The library's catalog system has been identified and tested. The search functionality is working but returns HTML that needs different parsing.

## Key Findings

### 1. Library System Architecture
- **Framework**: ASP.NET DNN (DotNetNuke)
- **Search Method**: POST to root URL (`https://stadtbibliothek.graz.at/`)
- **Form Type**: Server-side form with ViewState

### 2. Authentication Requirements
- No user authentication needed for public search
- Form requires ASP.NET ViewState parameters:
  - `__VIEWSTATE`
  - `__VIEWSTATEGENERATOR`
  - `__EVENTVALIDATION`

### 3. Search Parameters Tested
- `search`: Keyword search
- `title`: Title-based search
- `author`: Author-based search
- `isbn`: ISBN search

All parameters are accepted (HTTP 200), but results page contains dynamic content.

### 4. Response Analysis
- **Status**: HTTP 200 OK ✓
- **Size**: ~271KB (significant content)
- **Content Type**: HTML/text
- **Issue**: Search results appear to be JavaScript-rendered

###5. Current Challenge
The response HTML doesn't contain pre-rendered search results. This suggests:
1. Results are loaded via AJAX/JavaScript after page load
2. Results may be in a modal or separate DOM element
3. Dynamic rendering requires browser automation (Playwright/Selenium)

## Solution Path

### Option A: Browser Automation (Recommended for now)
Use Playwright to:
1. Navigate to library website
2. Fill search form
3. Click search button
4. Wait for results to load
5. Parse rendered HTML

This is more reliable but slightly slower.

### Option B: API Reverse Engineering
1. Monitor network requests in browser DevTools
2. Identify AJAX endpoint for search results
3. Call API directly with appropriate parameters

This would be faster once identified.

## Next Steps

1. **Implement Playwright-based search** in `session/browser.py`
2. **Update SearchOperation** to use browser session
3. **Test with known books** (e.g., "Die Schule der magischen Tiere")
4. **Improve parser** for any new HTML structure

## Testing Notes

Command to test:
```bash
source venv/bin/activate
python search_books.py
```

Books to test (from books-to-search.md):
- Die Schule der magischen Tiere (popular children's book)
- Die Flügelpferde von Sternenhall
- Dragon Girls: Rosie, der Zünddrache

These should all be available in a typical library system.

## Code Changes Made

- Updated `WebOPACScraper` to POST to root URL
- Added `_get_viewstate()` method to extract form data
- Changed search method from GET to POST
- Added support for ViewState parameters

## Files Affected

- `src/graz_library/catalog/scraper.py` - Updated for POST + ViewState
- `search_books.py` - Utility script (renamed from search_greta_books.py)
- `books-to-search.md` - Book list (renamed from greta-books.md)

