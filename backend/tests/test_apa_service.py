import pytest
from app.services.apa_service import apa7_service, APA7Service


class TestGenerateCitation:
    """Tests for in-text citation generation"""

    def test_citation_single_author(self):
        """Test citation with single author"""
        ref = {
            "authors": ["Smith, J."],
            "year": 2020,
        }
        result = apa7_service.generate_citation(ref)
        assert "Smith" in result
        assert "2020" in result
        assert result.startswith("(") and result.endswith(")")

    def test_citation_two_authors(self):
        """Test citation with two authors"""
        ref = {
            "authors": ["Smith, J.", "Jones, M."],
            "year": 2020,
        }
        result = apa7_service.generate_citation(ref)
        assert "Smith" in result
        assert "Jones" in result
        assert "&" in result
        assert "2020" in result

    def test_citation_multiple_authors(self):
        """Test citation with multiple authors (3-5)"""
        ref = {
            "authors": ["Smith, J.", "Jones, M.", "Brown, K."],
            "year": 2020,
        }
        result = apa7_service.generate_citation(ref)
        assert "Smith" in result
        assert "Brown" in result
        assert "&" in result
        assert "2020" in result

    def test_citation_many_authors(self):
        """Test citation with more than 5 authors (should use et al.)"""
        ref = {
            "authors": ["Smith, J.", "Jones, M.", "Brown, K.", "White, L.", "Green, P.", "Blue, Q."],
            "year": 2020,
        }
        result = apa7_service.generate_citation(ref)
        assert "Smith" in result
        assert "et al." in result
        assert "2020" in result

    def test_citation_no_year(self):
        """Test citation without year"""
        ref = {
            "authors": ["Smith, J."],
        }
        result = apa7_service.generate_citation(ref)
        assert "n.d." in result

    def test_citation_no_authors(self):
        """Test citation without authors"""
        ref = {
            "year": 2020,
            "citation_key": "Test2020",
        }
        result = apa7_service.generate_citation(ref)
        assert "2020" in result or "Test2020" in result


class TestGenerateReference:
    """Tests for reference list generation"""

    def test_book_reference(self):
        """Test book reference formatting"""
        ref = {
            "authors": ["Smith, J.", "Jones, M."],
            "year": 2020,
            "title": "Introduction to Psychology",
            "publisher": "Academic Press",
            "location": "New York",
            "type": "book",
        }
        result = apa7_service.generate_reference(ref)
        assert "Smith" in result
        assert "Jones" in result
        assert "Introduction to Psychology" in result
        assert "Academic Press" in result
        assert "2020" in result

    def test_article_reference(self):
        """Test journal article reference formatting"""
        ref = {
            "authors": ["Smith, J."],
            "year": 2020,
            "title": "Cognitive Development in Children",
            "source": "Journal of Psychology",
            "volume": "45",
            "issue": "3",
            "pages": "123-145",
            "type": "article",
        }
        result = apa7_service.generate_reference(ref)
        assert "Smith" in result
        assert "Cognitive Development" in result
        assert "Journal of Psychology" in result
        assert "45(3)" in result or "45" in result
        assert "123-145" in result

    def test_web_reference(self):
        """Test web/website reference formatting"""
        ref = {
            "authors": ["Smith, J."],
            "year": 2020,
            "title": "Understanding Psychology",
            "site_name": "Psychology Today",
            "url": "https://example.com/article",
            "type": "web",
        }
        result = apa7_service.generate_reference(ref)
        assert "Smith" in result
        assert "Understanding Psychology" in result
        assert "https://example.com" in result

    def test_chapter_reference(self):
        """Test book chapter reference formatting"""
        ref = {
            "authors": ["Smith, J."],
            "year": 2020,
            "chapter_title": "Introduction to Cognitive Psychology",
            "editors": ["Jones, M."],
            "book_title": "Handbook of Psychology",
            "publisher": "Academic Press",
            "pages": "45-67",
            "type": "chapter",
        }
        result = apa7_service.generate_reference(ref)
        assert "Smith" in result
        assert "Introduction to Cognitive" in result
        assert "Handbook of Psychology" in result
        assert "45-67" in result or "pp." in result


class TestParseReference:
    """Tests for parsing raw reference text"""

    def test_parse_article_reference(self):
        """Test parsing article reference"""
        raw_text = "Smith, J., & Jones, M. (2020). Introduction to Psychology. American Journal of Psychology, 45(3), 123-145. https://doi.org/10.1234/example"
        result = apa7_service.parse_reference_text(raw_text)
        
        assert len(result.get("authors", [])) > 0
        assert result.get("year") == 2020
        assert "Introduction" in result.get("title", "")
        assert result.get("type") == "article"
        assert "10.1234" in result.get("doi", "")

    def test_parse_book_reference(self):
        """Test parsing book reference"""
        raw_text = "Smith, J. (2020). Introduction to Psychology. New York: Academic Press."
        result = apa7_service.parse_reference_text(raw_text)
        
        assert len(result.get("authors", [])) > 0
        assert result.get("year") == 2020
        assert "Introduction" in result.get("title", "")

    def test_parse_web_reference(self):
        """Test parsing web reference"""
        raw_text = "Smith, J. (2020, January 15). Understanding Psychology. Psychology Today. https://example.com/article"
        result = apa7_service.parse_reference_text(raw_text)
        
        assert len(result.get("authors", [])) > 0
        assert result.get("year") == 2020
        assert "https://example.com" in result.get("url", "")
        assert result.get("type") == "web"

    def test_parse_with_doi(self):
        """Test parsing reference with DOI"""
        raw_text = "Smith, J. (2020). Example article. Journal Name, 10(2), 50-60. https://doi.org/10.1234/example"
        result = apa7_service.parse_reference_text(raw_text)
        
        assert "10.1234" in result.get("doi", "")

    def test_parse_extracts_volume_issue_pages(self):
        """Test that volume, issue, and pages are extracted"""
        raw_text = "Smith, J. (2020). Title. Journal, 45(3), 123-145."
        result = apa7_service.parse_reference_text(raw_text)
        
        assert result.get("volume") == "45"
        assert result.get("issue") == "3"
        assert "123" in result.get("pages", "")


class TestValidateCoherence:
    """Tests for citation-reference coherence validation"""

    def test_perfect_match(self):
        """Test validation with perfect matches"""
        citations = [
            {
                "citation_key": "[Smith, 2020]",
                "citation_text": "Smith (2020) states...",
                "parsed": {
                    "authors": ["Smith, J."],
                    "year": 2020,
                },
            }
        ]
        references = [
            {
                "ref_key": "[Smith, 2020]",
                "ref_text": "Smith, J. (2020). Example book.",
                "parsed": {
                    "authors": ["Smith, J."],
                    "year": 2020,
                },
            }
        ]
        
        result = apa7_service.validate_coherence(citations, references)
        
        assert len(result["citations_without_reference"]) == 0
        assert len(result["references_without_citations"]) == 0
        assert len(result["imperfect_matches"]) == 0

    def test_citation_without_reference(self):
        """Test detection of citation without matching reference"""
        citations = [
            {
                "citation_key": "[Smith, 2020]",
                "citation_text": "Smith (2020) states...",
                "parsed": {"authors": ["Smith, J."], "year": 2020},
            }
        ]
        references = []
        
        result = apa7_service.validate_coherence(citations, references)
        
        assert len(result["citations_without_reference"]) == 1
        assert result["citations_without_reference"][0]["citation_key"] == "[Smith, 2020]"

    def test_reference_without_citation(self):
        """Test detection of reference without matching citation"""
        citations = []
        references = [
            {
                "ref_key": "[Smith, 2020]",
                "ref_text": "Smith, J. (2020). Example book.",
                "parsed": {"authors": ["Smith, J."], "year": 2020},
            }
        ]
        
        result = apa7_service.validate_coherence(citations, references)
        
        assert len(result["references_without_citations"]) == 1
        assert result["references_without_citations"][0]["ref_key"] == "[Smith, 2020]"

    def test_imperfect_match(self):
        """Test detection of imperfect matches"""
        citations = [
            {
                "citation_key": "[Smith, 2020]",
                "citation_text": "Smith (2020) states...",
                "parsed": {
                    "authors": ["Smith, J."],
                    "year": 2020,
                },
            }
        ]
        references = [
            {
                "ref_key": "[Smith, 2020]",
                "ref_text": "Smith, J., & Jones, M. (2020). Example book.",
                "parsed": {
                    "authors": ["Smith, J.", "Jones, M."],
                    "year": 2020,
                },
            }
        ]
        
        result = apa7_service.validate_coherence(citations, references)
        
        assert len(result["imperfect_matches"]) == 1
        assert result["imperfect_matches"][0]["citation_key"] == "[Smith, 2020]"
        assert len(result["imperfect_matches"][0]["citation_authors"]) == 1
        assert len(result["imperfect_matches"][0]["reference_authors"]) == 2


class TestReferenceListGeneration:
    """Tests for complete reference list generation"""

    def test_generate_reference_list_text(self):
        """Test generating reference list in text format"""
        references = [
            {
                "authors": ["Smith, J."],
                "year": 2020,
                "title": "Book Title",
                "type": "book",
            }
        ]
        result = apa7_service.generate_reference_list(references, format_output="text")
        
        assert "\t" in result  # Should have tab for hanging indent
        assert "Smith" in result

    def test_generate_reference_list_html(self):
        """Test generating reference list in HTML format"""
        references = [
            {
                "authors": ["Smith, J."],
                "year": 2020,
                "title": "Book Title",
                "type": "book",
            }
        ]
        result = apa7_service.generate_reference_list(references, format_output="html")
        
        assert "<p" in result
        assert "text-indent" in result
        assert "padding-left" in result

    def test_generate_reference_list_latex(self):
        """Test generating reference list in LaTeX format"""
        references = [
            {
                "authors": ["Smith, J."],
                "year": 2020,
                "title": "Book Title",
                "type": "book",
            }
        ]
        result = apa7_service.generate_reference_list(references, format_output="latex")
        
        assert "\\hangindent" in result
        assert "\\\\" in result

    def test_multiple_references(self):
        """Test generating list with multiple references"""
        references = [
            {
                "authors": ["Smith, J."],
                "year": 2020,
                "title": "First Book",
                "type": "book",
            },
            {
                "authors": ["Jones, M."],
                "year": 2019,
                "title": "Second Book",
                "type": "book",
            }
        ]
        result = apa7_service.generate_reference_list(references)
        
        assert "Smith" in result
        assert "Jones" in result
        assert result.count("\n") >= 1  # Should have line breaks between references

