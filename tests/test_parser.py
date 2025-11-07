"""Tests for the HTML parser functionality"""

import pytest
from src.graz_library.catalog.parser import CatalogParser
from src.graz_library.models.book import Book


class TestCatalogParserBasic:
    """Test basic parser functionality"""

    def test_parser_initialization(self):
        """Test parser can be initialized"""
        parser = CatalogParser()
        assert parser is not None
        assert parser.logger is not None

    def test_parse_empty_html(self):
        """Test parsing empty HTML returns empty list"""
        parser = CatalogParser()
        result = parser.parse_search_results("")
        assert result == []
        assert isinstance(result, list)

    def test_parse_invalid_html(self):
        """Test parsing invalid HTML returns empty list"""
        parser = CatalogParser()
        result = parser.parse_search_results("<invalid>not a real page")
        assert result == []

    def test_parse_book_detail_empty(self):
        """Test parsing empty detail page returns dict with None values"""
        parser = CatalogParser()
        result = parser.parse_book_detail("")
        assert isinstance(result, dict)
        # Empty HTML still returns dict with None/default values
        assert result.get("title") is None
        assert result.get("availability") == "Unknown"
        assert result.get("keywords") == []


class TestCatalogParserDetailPage:
    """Test detail page parsing with realistic HTML samples"""

    @pytest.fixture
    def sample_detail_html(self):
        """Sample detail page HTML from investigation"""
        return """
        <html>
            <head><title>Harry Potter: Das Buch der Zauberstäbe</title></head>
            <body>
                <h1>Harry Potter: Das Buch der Zauberstäbe</h1>
                <p>Mediengruppe: Kinderbuch</p>
                <p>Verfasser: Peterson, Monique</p>
                <p>Jahr: 2017</p>
                <p>Verlag: Stuttgart, Panini-Verl.</p>
                <p>Sprache: Deutsch</p>
                <p>ISBN: 978-3-8332-3580-1</p>
                <p>Beschreibung: 148 S. : überw. Ill.</p>
                <p>Reihe: Harry Potter, Panini Comics</p>
                <p>Originaltitel: Harry Potter: the wand collection <dt.></p>
                <p>Schlagwörter: Magie, Magier, Kindersachbuch, Zauber</p>
                <div class="summary">
                    <p>DIE ZAUBERSTÄBE IN DEN HARRY-POTTER-FILMEN sind genauso einzigartig
                    wie die Hexe oder der Zauberer, die sie schwingen. Ob Hermine Grangers eleganter...</p>
                </div>
                <table>
                    <tr>
                        <th>ZWEIGSTELLE</th>
                        <th>SIGNATUR</th>
                        <th>STANDORT 2</th>
                        <th>STATUS</th>
                        <th>VORBESTELLUNGEN</th>
                        <th>MEDIENGRUPPE</th>
                        <th>FRIST</th>
                        <th>BARCODE</th>
                    </tr>
                    <tr>
                        <td>Zanklhof</td>
                        <td>JK.T PET</td>
                        <td>Ausleihe</td>
                        <td>Verfügbar</td>
                        <td>0</td>
                        <td>Kinderbuch</td>
                        <td></td>
                        <td>1801SB02708</td>
                    </tr>
                </table>
                <img src="/covers/9783833235801.jpg" alt="Cover" class="cover"/>
            </body>
        </html>
        """

    def test_parse_detail_extracts_title(self, sample_detail_html):
        """Test title extraction from detail page"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        assert result.get("title") == "Harry Potter: Das Buch der Zauberstäbe"

    def test_parse_detail_extracts_author(self, sample_detail_html):
        """Test author extraction"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        assert "Peterson" in (result.get("author") or "")

    def test_parse_detail_extracts_isbn(self, sample_detail_html):
        """Test ISBN extraction and cleanup"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        isbn = result.get("isbn")
        assert isbn is not None
        assert len(isbn) == 13
        assert isbn == "9783833235801"

    def test_parse_detail_extracts_year(self, sample_detail_html):
        """Test publication year extraction"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        assert result.get("publication_year") == 2017

    def test_parse_detail_extracts_language(self, sample_detail_html):
        """Test language extraction"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        assert result.get("language") == "Deutsch"

    def test_parse_detail_extracts_series(self, sample_detail_html):
        """Test series extraction"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        series = result.get("series")
        assert series is not None
        assert "Harry Potter" in series
        assert "Panini Comics" in series

    def test_parse_detail_extracts_page_count(self, sample_detail_html):
        """Test page count extraction from description"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        assert result.get("page_count") == 148

    def test_parse_detail_extracts_keywords(self, sample_detail_html):
        """Test keywords extraction and splitting"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        keywords = result.get("keywords", [])
        assert isinstance(keywords, list)
        assert "Magie" in keywords
        assert "Zauber" in keywords
        assert len(keywords) >= 4

    def test_parse_detail_extracts_exemplare(self, sample_detail_html):
        """Test exemplare/copies table extraction"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        exemplare = result.get("exemplare", [])
        assert isinstance(exemplare, list)
        assert len(exemplare) > 0
        first_copy = exemplare[0]
        assert first_copy.get("branch") == "Zanklhof"
        assert first_copy.get("call_number") == "JK.T PET"
        assert "Available" in first_copy.get("status", "")
        assert first_copy.get("barcode") == "1801SB02708"

    def test_parse_detail_extracts_availability_from_exemplare(self, sample_detail_html):
        """Test availability is set from exemplare table"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        assert "Available" in result.get("availability", "")

    def test_parse_detail_extracts_branch_from_exemplare(self, sample_detail_html):
        """Test branch is set from exemplare table"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        assert result.get("branch") == "Zanklhof"

    def test_parse_detail_extracts_description(self, sample_detail_html):
        """Test description extraction"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        description = result.get("description")
        assert description is not None
        assert "ZAUBERSTÄBE" in description or "Zauberstab" in description

    def test_parse_detail_extract_publisher(self, sample_detail_html):
        """Test publisher extraction"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        assert "Stuttgart" in (result.get("publisher") or "")
        assert "Panini" in (result.get("publisher") or "")

    def test_parse_detail_medium_type(self, sample_detail_html):
        """Test medium type extraction"""
        parser = CatalogParser()
        result = parser.parse_book_detail(sample_detail_html)
        assert result.get("medium_type") == "Kinderbuch"


class TestCatalogParserFieldExtraction:
    """Test the field extraction helper methods"""

    def test_extract_field_by_label(self):
        """Test _extract_field_by_label method"""
        parser = CatalogParser()
        html = """
        <html>
            <body>
                <p>ISBN: 978-3-8332-3580-1</p>
                <p>Jahr: 2017</p>
                <p>Verlag: Stuttgart, Panini-Verl.</p>
            </body>
        </html>
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        assert parser._extract_field_by_label(soup, "ISBN") == "978-3-8332-3580-1"
        assert parser._extract_field_by_label(soup, "Jahr") == "2017"
        assert "Stuttgart" in (parser._extract_field_by_label(soup, "Verlag") or "")

    def test_extract_field_not_found(self):
        """Test _extract_field_by_label with missing field"""
        parser = CatalogParser()
        html = "<html><body><p>Some content</p></body></html>"
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        assert parser._extract_field_by_label(soup, "NonExistent") is None

    def test_extract_exemplare_info(self):
        """Test _extract_exemplare_info method"""
        parser = CatalogParser()
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <th>ZWEIGSTELLE</th>
                        <th>SIGNATUR</th>
                        <th>STANDORT 2</th>
                        <th>STATUS</th>
                    </tr>
                    <tr>
                        <td>Zanklhof</td>
                        <td>JK.T PET</td>
                        <td>Ausleihe</td>
                        <td>Verfügbar</td>
                    </tr>
                    <tr>
                        <td>Gösting</td>
                        <td>JK.T ROW</td>
                        <td>Ausleihe</td>
                        <td>Ausgeliehen</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        exemplare = parser._extract_exemplare_info(soup)
        assert len(exemplare) == 2
        assert exemplare[0]["branch"] == "Zanklhof"
        assert exemplare[0]["status"] == "Available"
        assert exemplare[1]["branch"] == "Gösting"
        assert exemplare[1]["status"] == "Checked Out"


class TestCatalogParserIntegration:
    """Integration tests with complete detail page parsing"""

    def test_detail_parsing_creates_valid_book_data(self):
        """Test that detail parsing creates data compatible with Book model"""
        parser = CatalogParser()
        html = """
        <html>
            <h1>Test Book Title</h1>
            <p>Verfasser: Test Author</p>
            <p>ISBN: 978-1234567890</p>
            <p>Verlag: Test Publisher</p>
            <p>Jahr: 2023</p>
            <p>Mediengruppe: Book</p>
            <p>Sprache: English</p>
        </html>
        """
        result = parser.parse_book_detail(html)

        # Verify we can create a Book from the parsed data
        book = Book(
            title=result.get("title", "Unknown"),
            author=result.get("author"),
            isbn=result.get("isbn"),
            publisher=result.get("publisher"),
            publication_year=result.get("publication_year"),
            medium_type=result.get("medium_type", "Book"),
            language=result.get("language"),
            series=result.get("series"),
            original_title=result.get("original_title"),
            page_count=result.get("page_count"),
            keywords=result.get("keywords", []),
            barcode=result.get("barcode"),
            branch=result.get("branch"),
            availability=result.get("availability", "Unknown"),
            location=result.get("location"),
            call_number=result.get("call_number"),
            description=result.get("description"),
        )

        assert book.title == "Test Book Title"
        assert book.author == "Test Author"

    def test_multiple_exemplare_copies(self):
        """Test parsing multiple copies from different branches"""
        parser = CatalogParser()
        html = """
        <html>
            <h1>Popular Book</h1>
            <table>
                <tr>
                    <th>ZWEIGSTELLE</th>
                    <th>SIGNATUR</th>
                    <th>STANDORT 2</th>
                    <th>STATUS</th>
                    <th>VORBESTELLUNGEN</th>
                    <th>MEDIENGRUPPE</th>
                    <th>FRIST</th>
                    <th>BARCODE</th>
                </tr>
                <tr>
                    <td>Zanklhof</td>
                    <td>JK.T</td>
                    <td>Ausleihe</td>
                    <td>Verfügbar</td>
                    <td>0</td>
                    <td>Book</td>
                    <td></td>
                    <td>1001</td>
                </tr>
                <tr>
                    <td>Gösting</td>
                    <td>JK.T</td>
                    <td>Ausleihe</td>
                    <td>Ausgeliehen</td>
                    <td>2</td>
                    <td>Book</td>
                    <td>2024-01-15</td>
                    <td>1002</td>
                </tr>
                <tr>
                    <td>West</td>
                    <td>JK.T</td>
                    <td>Ausleihe</td>
                    <td>Verfügbar</td>
                    <td>1</td>
                    <td>Book</td>
                    <td></td>
                    <td>1003</td>
                </tr>
            </table>
        </html>
        """
        result = parser.parse_book_detail(html)
        exemplare = result.get("exemplare", [])

        assert len(exemplare) == 3
        assert exemplare[0]["branch"] == "Zanklhof"
        assert exemplare[0]["status"] == "Available"
        assert exemplare[1]["branch"] == "Gösting"
        assert exemplare[1]["status"] == "Checked Out"
        assert exemplare[1]["reservations"] == "2"
        assert exemplare[2]["branch"] == "West"


class TestCatalogParserEdgeCases:
    """Test edge cases and error handling"""

    def test_parse_isbn_with_hyphens(self):
        """Test ISBN extraction with hyphens"""
        parser = CatalogParser()
        html = "<html><body><p>ISBN: 978-3-8332-3580-1</p></body></html>"
        result = parser.parse_book_detail(html)
        isbn = result.get("isbn")
        assert isbn is not None
        assert "-" not in isbn
        assert len(isbn) == 13

    def test_parse_invalid_isbn(self):
        """Test invalid ISBN is not returned"""
        parser = CatalogParser()
        html = "<html><body><p>ISBN: 123</p></body></html>"
        result = parser.parse_book_detail(html)
        assert result.get("isbn") is None

    def test_parse_missing_optional_fields(self):
        """Test parsing works with missing optional fields"""
        parser = CatalogParser()
        html = "<html><h1>Book Title Only</h1></html>"
        result = parser.parse_book_detail(html)
        assert result.get("title") == "Book Title Only"
        assert result.get("author") is None
        assert result.get("isbn") is None
        assert result.get("keywords") == []

    def test_parse_description_with_special_characters(self):
        """Test description parsing with German umlauts"""
        parser = CatalogParser()
        html = """
        <html>
            <h1>Test Book</h1>
            <div class="summary">
                <p>Ein Buch über Zauberei, Magie und wunderbare Geschichten.</p>
            </div>
        </html>
        """
        result = parser.parse_book_detail(html)
        description = result.get("description")
        assert description is not None
        assert "Zauberei" in description or "Magie" in description
