# Greta's Books Search Tool

This is a personal utility to search for books in Greta's reading list at Stadtbibliothek Graz.

## Files

- `greta-books.md` - Contains the list of books to search for
- `search_greta_books.py` - Standalone script to search for availability

**Note**: These files should not be committed to the repository. They are already in `.gitignore`.

## Running the Search

```bash
cd /path/to/graz-library-bulk-ops
source venv/bin/activate
python search_greta_books.py
```

## What It Does

1. **Parses** the book list from `greta-books.md`
2. **Cleans up** book titles (removes numbering, markdown formatting)
3. **Looks up ISBNs** using Open Library API (optional, helps with accuracy)
4. **Searches** the Stadtbibliothek Graz catalog for each book
5. **Reports** availability and location for each book found

## Current Status

The script is fully functional for:
- ✅ Parsing book lists from markdown
- ✅ ISBN lookup from Open Library
- ✅ Query construction and rate limiting
- ❌ Library catalog search (404 - endpoint may have changed)

The library's search API endpoint appears to have changed. Once the correct endpoint is identified, simply update the `LIBRARY_SEARCH_URL` in `WebOPACScraper.search()` method.

## Books in Greta's List

1. Die Flügelpferde von Sternenhall
2. Die Ponys von Lillasund: Winterzauber im Stall
3. Dragon Girls: Rosie, der Zünddrache
4. Das Geheimnis der Luchse
5. Eulenzauber Junior: Goldwing und Mondscheinpony
6. Die Schule der magischen Tiere
7. PS: Du bist ein Geschenk!
8. Endlich 13: jetzt ist starke ich richtig durch
9. Wirbel um das Weihnachtspony
10. Wilder Lauf der Wald
11. Jahresmarkt der Zeitreisenden - Der gestohlene Kristall

## Fixing the Library API

If you need to update the search endpoint:

1. Visit https://stadtbibliothek.graz.at/ manually to understand the current search interface
2. Update `search_greta_books.py` with the correct endpoint URL
3. Adjust the request parameters if needed
4. Run the script again

The script will then show availability and locations for each book.

## Customization

To add or modify the book list, edit `greta-books.md`:

```markdown
# List Title

1. Book Title One
2. Book Title Two
3. Book Title Three
```

The script will automatically parse and clean the list.
