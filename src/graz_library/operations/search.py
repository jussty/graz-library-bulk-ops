"""Search operation handler"""

from typing import List, Optional
import csv
import json
from pathlib import Path

from ..catalog.scraper import WebOPACScraper
from ..models.book import SearchResult, Book
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SearchOperation:
    """Handles search operations"""

    def __init__(self):
        """Initialize search operation"""
        self.scraper = WebOPACScraper()
        self.logger = logger

    def search(
        self,
        query: str,
        search_type: str = "keyword",
        use_cache: bool = True,
    ) -> Optional[SearchResult]:
        """Perform a search

        Args:
            query: Search query
            search_type: Type of search (keyword, author, title, isbn)
            use_cache: Whether to use cached results

        Returns:
            SearchResult or None
        """
        return self.scraper.search(query, search_type=search_type, use_cache=use_cache)

    def search_from_file(
        self,
        file_path: str,
        search_type: str = "keyword",
        use_cache: bool = True,
    ) -> List[SearchResult]:
        """Search for multiple queries from a file

        Args:
            file_path: Path to file (CSV or JSON)
            search_type: Type of search
            use_cache: Whether to use cached results

        Returns:
            List of SearchResult objects
        """
        path = Path(file_path)

        if not path.exists():
            self.logger.error(f"File not found: {file_path}")
            return []

        results = []

        try:
            if path.suffix.lower() == ".csv":
                results = self._search_from_csv(path, search_type, use_cache)
            elif path.suffix.lower() == ".json":
                results = self._search_from_json(path, search_type, use_cache)
            else:
                self.logger.error(f"Unsupported file format: {path.suffix}")
                return []

            self.logger.info(f"Completed {len(results)} searches from file")
            return results

        except Exception as e:
            self.logger.error(f"Error reading file: {e}")
            return []

    def _search_from_csv(
        self,
        path: Path,
        search_type: str,
        use_cache: bool,
    ) -> List[SearchResult]:
        """Search from CSV file

        Args:
            path: Path to CSV file
            search_type: Type of search
            use_cache: Whether to use cached results

        Returns:
            List of SearchResult objects
        """
        results = []

        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    # Expect 'query' or 'search' column
                    query = row.get("query") or row.get("search") or row.get("title")

                    if not query:
                        self.logger.warning(f"Skipping row with no query: {row}")
                        continue

                    result = self.search(query, search_type=search_type, use_cache=use_cache)
                    if result:
                        results.append(result)

            self.logger.info(f"Loaded {len(results)} search queries from CSV")
            return results

        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            return []

    def _search_from_json(
        self,
        path: Path,
        search_type: str,
        use_cache: bool,
    ) -> List[SearchResult]:
        """Search from JSON file

        Args:
            path: Path to JSON file
            search_type: Type of search
            use_cache: Whether to use cached results

        Returns:
            List of SearchResult objects
        """
        results = []

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both list and dict formats
            queries = []
            if isinstance(data, list):
                queries = data
            elif isinstance(data, dict) and "queries" in data:
                queries = data["queries"]
            elif isinstance(data, dict):
                queries = [data]

            for item in queries:
                if isinstance(item, str):
                    query = item
                elif isinstance(item, dict):
                    query = item.get("query") or item.get("search") or item.get("title")
                else:
                    self.logger.warning(f"Skipping invalid query item: {item}")
                    continue

                if not query:
                    continue

                result = self.search(query, search_type=search_type, use_cache=use_cache)
                if result:
                    results.append(result)

            self.logger.info(f"Loaded {len(results)} search queries from JSON")
            return results

        except Exception as e:
            self.logger.error(f"Error reading JSON file: {e}")
            return []

    def export_results(
        self,
        results: List[SearchResult],
        output_file: str,
        format: str = "csv",
    ) -> bool:
        """Export search results to file

        Args:
            results: List of SearchResult objects
            output_file: Path to output file
            format: Export format (csv, json)

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(output_file)
            path.parent.mkdir(parents=True, exist_ok=True)

            if format.lower() == "csv":
                return self._export_to_csv(results, path)
            elif format.lower() == "json":
                return self._export_to_json(results, path)
            else:
                self.logger.error(f"Unsupported export format: {format}")
                return False

        except Exception as e:
            self.logger.error(f"Error exporting results: {e}")
            return False

    def _export_to_csv(self, results: List[SearchResult], path: Path) -> bool:
        """Export results to CSV

        Args:
            results: List of SearchResult objects
            path: Output path

        Returns:
            True if successful
        """
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                # Collect all books from all results
                all_books = []
                for result in results:
                    all_books.extend(result.books)

                if not all_books:
                    self.logger.warning("No books to export")
                    return False

                # Write headers
                fieldnames = [
                    "title",
                    "author",
                    "isbn",
                    "publisher",
                    "publication_year",
                    "medium_type",
                    "availability",
                    "location",
                    "catalog_id",
                ]

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                # Write book data
                for book in all_books:
                    writer.writerow({
                        "title": book.title,
                        "author": book.author,
                        "isbn": book.isbn,
                        "publisher": book.publisher,
                        "publication_year": book.publication_year,
                        "medium_type": book.medium_type,
                        "availability": book.availability,
                        "location": book.location,
                        "catalog_id": book.catalog_id,
                    })

            self.logger.info(f"Exported {len(all_books)} books to {path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return False

    def _export_to_json(self, results: List[SearchResult], path: Path) -> bool:
        """Export results to JSON

        Args:
            results: List of SearchResult objects
            path: Output path

        Returns:
            True if successful
        """
        try:
            data = {
                "export_timestamp": __import__("datetime").datetime.now().isoformat(),
                "total_searches": len(results),
                "results": [result.to_dict() for result in results],
            }

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Exported {len(results)} search results to {path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            return False

    def close(self) -> None:
        """Close resources"""
        self.scraper.close()
