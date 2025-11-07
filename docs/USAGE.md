# Usage Guide

This guide explains how to use the Graz Library Bulk Operations Tool.

## Command Overview

The tool provides several commands for interacting with the library catalog:

```bash
graz-library --help
```

## Search Operations

### Simple Search

Search for a book by keywords:

```bash
graz-library search "Harry Potter"
```

### Search by Type

#### By Title

```bash
graz-library search --type title "Harry Potter and the Philosopher's Stone"
```

#### By Author

```bash
graz-library search --type author "J.K. Rowling"
```

#### By ISBN

```bash
graz-library search --type isbn "9780439708180"
```

### Save Search Results

Export search results to CSV or JSON:

```bash
graz-library search "Harry Potter" --output results.csv
graz-library search "Harry Potter" --output results.json
```

### Bulk Search from File

Search for multiple books from a CSV file:

```bash
graz-library bulk-search books.csv --output results.csv
```

#### CSV Format

```csv
query,type
Harry Potter,title
J.K. Rowling,author
9780439708180,isbn
```

#### JSON Format

```json
{
  "queries": [
    {"query": "Harry Potter", "type": "title"},
    {"query": "J.K. Rowling", "type": "author"}
  ]
}
```

## Search Results Output

Results are displayed in a table format:

```
Title                     | Author          | ISBN           | Availability | Location
------------------------- | --------------- | -------------- | ------------ | ----------
Harry Potter and the      | J.K. Rowling   | 9780439708180 | Available    | Zanklhof
Philosopher's Stone       |                 |               |              |
```

### Export Formats

#### CSV Export

Columns: title, author, isbn, publisher, publication_year, medium_type, availability, location, catalog_id

#### JSON Export

Complete search metadata including timestamps and search performance metrics:

```json
{
  "export_timestamp": "2024-01-15T10:30:00",
  "total_searches": 3,
  "results": [
    {
      "query": "Harry Potter",
      "search_type": "title",
      "total_results": 25,
      "books": [...]
    }
  ]
}
```

## Reservation Operations (Coming Soon)

Reserve a book by ISBN:

```bash
graz-library reserve 9780439708180 --email user@example.com
```

With specific pickup location:

```bash
graz-library reserve 9780439708180 --email user@example.com --location "Zanklhof"
```

Bulk reservations from file:

```bash
graz-library bulk-reserve reservations.csv
```

## Mail Order Operations (Coming Soon)

Submit a mail order:

```bash
graz-library mail-order "Harry Potter" \
  --recipient "John Doe" \
  --email "john@example.com" \
  --address "123 Main St, Graz 8010"
```

Or with library pickup:

```bash
graz-library mail-order "Harry Potter" \
  --recipient "John Doe" \
  --email "john@example.com" \
  --pickup "Zanklhof"
```

## Caching

Search results are cached locally for 1 hour to reduce library server load.

### View Cache

Cached results are stored in `~/.graz-library/data/cache/`

### Clear Cache

Clear all cache:

```bash
graz-library cache --clear
```

Clear specific search:

```bash
graz-library cache --clear "Harry Potter"
```

## Examples

### Example 1: Find all books by an author

```bash
graz-library search --type author "Stephen King" --output stephen_king_books.csv
```

### Example 2: Bulk search from file with results

```bash
# Create a file with search queries
cat > wishlist.csv << EOF
query,type
The Hobbit,title
J.R.R. Tolkien,author
EOF

# Search all queries
graz-library bulk-search wishlist.csv --output wishlist_results.json

# View results
cat wishlist_results.json
```

### Example 3: Search by ISBN and get JSON output

```bash
graz-library search --type isbn "978-3-442-76261-5" --output result.json
```

## Logging and Debugging

### View Logs

Logs are stored in `~/.graz-library/logs/graz-library.log`

```bash
# View recent logs
tail -f ~/.graz-library/logs/graz-library.log

# View all logs
cat ~/.graz-library/logs/graz-library.log
```

### Enable Debug Logging

Set log level in `.env`:

```bash
LOG_LEVEL=DEBUG
```

Then run commands - you'll see detailed debug information:

```bash
graz-library search "Harry Potter"
```

## Batch Processing

For large-scale operations, create a CSV file and process in batches:

```bash
# books.csv
query,type
Book 1,title
Book 2,title
Book 3,title
...
```

```bash
graz-library bulk-search books.csv --output all_results.json
```

## Performance Tips

1. **Reuse Results**: Cache is enabled by default for 1 hour
2. **Batch Queries**: Use bulk-search instead of multiple individual searches
3. **Rate Limiting**: The tool automatically respects rate limits (2 second delay)
4. **Headless Mode**: Browser automation runs in headless mode for better performance

## Troubleshooting

### No Results Found

- Check spelling of search terms
- Try a broader search (fewer keywords)
- Try a different search type (e.g., author instead of title)

### Connection Timeout

- Check internet connection
- Verify library website is accessible
- Increase REQUEST_TIMEOUT in `.env`

### Permission Errors

- Ensure `~/.graz-library/` is writable
- Check file permissions

## Limits and Rate Limiting

- Requests are rate-limited to 1 every 2 seconds
- Search results cache for 1 hour
- Maximum search results per query: 100

These limits help ensure respectful use of the library's resources.
