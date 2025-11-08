"""
APA 7 Citation and Reference Service

Handles generation of in-text citations and reference list entries
following APA 7th edition style guide.
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class APA7Service:
    """Service for APA 7 citation and reference formatting"""
    
    # Common DOI patterns
    DOI_PATTERN = re.compile(r'10\.\d{4,}/[^\s]+', re.IGNORECASE)
    
    def generate_citation(self, parsed_ref: Dict[str, Any]) -> str:
        """
        Generate in-text citation in APA 7 format.
        
        Args:
            parsed_ref: Dictionary with parsed reference fields:
                - authors: List of author names
                - year: Publication year
                - title: Title of work
                - type: Type of source (book, article, web, chapter, etc.)
        
        Returns:
            Formatted in-text citation string
        """
        authors = parsed_ref.get("authors", [])
        year = parsed_ref.get("year")
        citation_key = parsed_ref.get("citation_key", "")
        
        if not authors and not year:
            return citation_key if citation_key else "(n.d.)"
        
        # Format authors
        if not authors:
            # No authors, use title or citation_key
            if citation_key:
                return f"({citation_key}, {year})" if year else f"({citation_key}, n.d.)"
            return f"(n.d., {year})" if year else "(n.d.)"
        
        # Format author names for citation
        author_count = len(authors)
        
        if author_count == 1:
            author_str = self._format_author_name(authors[0], for_citation=True)
            return f"({author_str}, {year})" if year else f"({author_str}, n.d.)"
        
        elif author_count == 2:
            author1 = self._format_author_name(authors[0], for_citation=True)
            author2 = self._format_author_name(authors[1], for_citation=True)
            return f"({author1} & {author2}, {year})" if year else f"({author1} & {author2}, n.d.)"
        
        elif author_count <= 5:
            # List all authors
            author_list = [self._format_author_name(a, for_citation=True) for a in authors]
            authors_str = ", ".join(author_list[:-1]) + f", & {author_list[-1]}"
            return f"({authors_str}, {year})" if year else f"({authors_str}, n.d.)"
        
        else:
            # More than 5 authors: first author et al.
            first_author = self._format_author_name(authors[0], for_citation=True)
            return f"({first_author} et al., {year})" if year else f"({first_author} et al., n.d.)"
    
    def generate_reference(self, parsed_ref: Dict[str, Any]) -> str:
        """
        Generate reference list entry in APA 7 format with hanging indent.
        
        Args:
            parsed_ref: Dictionary with parsed reference fields
        
        Returns:
            Formatted reference string with hanging indent
        """
        ref_type = parsed_ref.get("type", "book").lower()
        
        if ref_type == "book":
            return self._format_book_reference(parsed_ref)
        elif ref_type == "article":
            return self._format_article_reference(parsed_ref)
        elif ref_type == "web" or ref_type == "website":
            return self._format_web_reference(parsed_ref)
        elif ref_type == "chapter":
            return self._format_chapter_reference(parsed_ref)
        else:
            # Default: try to format as generic reference
            return self._format_generic_reference(parsed_ref)
    
    def parse_reference_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Parse raw reference text into structured components.
        
        Uses heuristics and regex patterns to extract:
        - authors
        - year
        - title
        - source/publication
        - doi/url
        
        Args:
            raw_text: Raw reference text
        
        Returns:
            Dictionary with parsed fields
        """
        parsed = {
            "authors": [],
            "year": None,
            "title": None,
            "source": None,
            "type": "book",
            "doi": None,
            "url": None,
            "publisher": None,
            "volume": None,
            "issue": None,
            "pages": None,
        }
        
        # Extract DOI
        doi_match = self.DOI_PATTERN.search(raw_text)
        if doi_match:
            parsed["doi"] = doi_match.group(0)
            # Try to fetch metadata from DOI (optional, would need external API)
        
        # Extract URL
        url_pattern = re.compile(r'https?://[^\s]+', re.IGNORECASE)
        url_match = url_pattern.search(raw_text)
        if url_match:
            parsed["url"] = url_match.group(0)
            parsed["type"] = "web"
        
        # Extract year (4-digit year, typically in parentheses or at start)
        year_pattern = re.compile(r'\b(19|20)\d{2}\b')
        year_matches = year_pattern.findall(raw_text)
        if year_matches:
            # Get the most likely year (usually the first 4-digit year)
            full_year_match = re.search(r'\b(19|20)\d{2}\b', raw_text)
            if full_year_match:
                parsed["year"] = int(full_year_match.group(0))
        
        # Extract authors (heuristic: names before year, typically in format "Last, First" or "Last, F.")
        # Look for patterns like "Last, F., & Last, F." or "Last, F. M."
        author_pattern = re.compile(r'([A-Z][a-z]+(?:,\s*[A-Z]\.?\s*[A-Z]?\.?)?(?:\s*&\s*)?)+')
        # More specific: look for comma-separated names before year
        before_year = raw_text[:raw_text.find(str(parsed["year"]))] if parsed["year"] else raw_text
        
        # Try to extract author names (simplified heuristic)
        # Look for patterns like "Smith, J., & Jones, M."
        author_section = before_year.split('.')[0] if '.' in before_year else before_year
        author_names = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z]\.?)+)', author_section)
        if author_names:
            parsed["authors"] = author_names[:5]  # Limit to 5 authors
        
        # Extract title (usually after authors, before publication info)
        # Title is often in italics or quotes, or just the longest sentence
        # Simplified: look for text between author section and year
        if parsed["year"]:
            year_pos = raw_text.find(str(parsed["year"]))
            title_section = raw_text[len(author_section):year_pos].strip()
            # Remove common punctuation
            title_section = re.sub(r'^[.,;:\s]+', '', title_section)
            if title_section and len(title_section) > 10:
                parsed["title"] = title_section
        
        # Extract publication/source info
        # Look for journal names, publisher names, etc.
        # This is a simplified heuristic
        if "Journal" in raw_text or "Review" in raw_text:
            parsed["type"] = "article"
            journal_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Journal|Review|Magazine))', raw_text)
            if journal_match:
                parsed["source"] = journal_match.group(1)
        
        # Extract volume, issue, pages for articles
        volume_match = re.search(r'(\d+)\s*\((\d+)\)', raw_text)  # Volume(Issue)
        if volume_match:
            parsed["volume"] = volume_match.group(1)
            parsed["issue"] = volume_match.group(2)
        
        pages_match = re.search(r'(\d+)\s*[-–]\s*(\d+)', raw_text)  # Pages
        if pages_match:
            parsed["pages"] = f"{pages_match.group(1)}-{pages_match.group(2)}"
        
        return parsed
    
    def validate_coherence(
        self,
        citations: List[Dict[str, Any]],
        references: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate coherence between citations and references.
        
        Args:
            citations: List of citation dictionaries with citation_key
            references: List of reference dictionaries with ref_key
        
        Returns:
            Dictionary with validation results:
            - citations_without_reference: List of citation keys without matching reference
            - references_without_citations: List of reference keys without matching citation
            - imperfect_matches: List of matches with issues (same authors/year but different formatting)
        """
        result = {
            "citations_without_reference": [],
            "references_without_citations": [],
            "imperfect_matches": [],
        }
        
        # Create lookup dictionaries
        citation_keys = {c.get("citation_key", ""): c for c in citations if c.get("citation_key")}
        reference_keys = {r.get("ref_key", ""): r for r in references if r.get("ref_key")}
        
        # Find citations without references
        for citation_key, citation in citation_keys.items():
            if citation_key not in reference_keys:
                result["citations_without_reference"].append({
                    "citation_key": citation_key,
                    "citation_text": citation.get("citation_text", ""),
                })
        
        # Find references without citations
        for ref_key, reference in reference_keys.items():
            if ref_key not in citation_keys:
                result["references_without_citations"].append({
                    "ref_key": ref_key,
                    "ref_text": reference.get("ref_text", ""),
                })
        
        # Find imperfect matches (same authors/year but different keys)
        for citation_key, citation in citation_keys.items():
            if citation_key in reference_keys:
                reference = reference_keys[citation_key]
                
                # Check if authors and year match
                cit_authors = citation.get("parsed", {}).get("authors", [])
                ref_authors = reference.get("parsed", {}).get("authors", [])
                cit_year = citation.get("parsed", {}).get("year")
                ref_year = reference.get("parsed", {}).get("year")
                
                # Normalize authors for comparison
                cit_authors_normalized = [self._normalize_author(a) for a in cit_authors]
                ref_authors_normalized = [self._normalize_author(a) for a in ref_authors]
                
                # Check for mismatches
                if (cit_authors_normalized != ref_authors_normalized or cit_year != ref_year):
                    result["imperfect_matches"].append({
                        "citation_key": citation_key,
                        "ref_key": citation_key,
                        "citation_authors": cit_authors,
                        "reference_authors": ref_authors,
                        "citation_year": cit_year,
                        "reference_year": ref_year,
                        "issue": "Authors or year mismatch between citation and reference",
                    })
        
        return result
    
    def _format_author_name(self, name: str, for_citation: bool = False) -> str:
        """Format author name for citation or reference"""
        # Handle different name formats
        if "," in name:
            # Format: "Last, First" or "Last, F."
            parts = [p.strip() for p in name.split(",")]
            if len(parts) >= 2:
                last = parts[0]
                first = parts[1]
                if for_citation:
                    return f"{last}, {first[0]}." if len(first) == 1 else f"{last}, {first}"
                else:
                    return f"{last}, {first[0]}." if len(first) == 1 else f"{last}, {first}"
        
        # Format: "First Last"
        parts = name.split()
        if len(parts) >= 2:
            last = parts[-1]
            first = " ".join(parts[:-1])
            if for_citation:
                return f"{last}, {first[0]}." if len(first) == 1 else f"{last}, {first}"
            else:
                return f"{last}, {first[0]}." if len(first) == 1 else f"{last}, {first}"
        
        return name
    
    def _format_book_reference(self, ref: Dict[str, Any]) -> str:
        """Format book reference in APA 7 style"""
        authors = ref.get("authors", [])
        year = ref.get("year", "n.d.")
        title = ref.get("title", "")
        publisher = ref.get("publisher", "")
        location = ref.get("location", "")
        
        # Format authors
        author_str = self._format_author_list(ref.get("authors", []))
        
        # Format: Author, A. A. (Year). Title. Publisher.
        parts = []
        if author_str:
            parts.append(author_str)
        if year:
            parts.append(f"({year}).")
        if title:
            parts.append(f"{title}.")
        if publisher:
            if location:
                parts.append(f"{location}: {publisher}.")
            else:
                parts.append(f"{publisher}.")
        
        return " ".join(parts)
    
    def _format_article_reference(self, ref: Dict[str, Any]) -> str:
        """Format journal article reference in APA 7 style"""
        authors = ref.get("authors", [])
        year = ref.get("year", "n.d.")
        title = ref.get("title", "")
        source = ref.get("source", ref.get("journal", ""))
        volume = ref.get("volume")
        issue = ref.get("issue")
        pages = ref.get("pages")
        doi = ref.get("doi")
        
        # Format authors
        author_str = self._format_author_list(authors)
        
        # Format: Author, A. A. (Year). Title. Journal, Volume(Issue), Pages. https://doi.org/xx
        parts = []
        if author_str:
            parts.append(author_str)
        if year:
            parts.append(f"({year}).")
        if title:
            parts.append(f"{title}.")
        if source:
            if volume:
                if issue:
                    parts.append(f"{source}, {volume}({issue}),")
                else:
                    parts.append(f"{source}, {volume},")
            else:
                parts.append(f"{source},")
        if pages:
            parts.append(f"{pages}.")
        if doi:
            parts.append(f"https://doi.org/{doi}")
        
        return " ".join(parts)
    
    def _format_web_reference(self, ref: Dict[str, Any]) -> str:
        """Format web/website reference in APA 7 style"""
        authors = ref.get("authors", [])
        year = ref.get("year", "n.d.")
        title = ref.get("title", "")
        site_name = ref.get("site_name", ref.get("source", ""))
        url = ref.get("url", "")
        retrieved_date = ref.get("retrieved_date", datetime.now().strftime("%B %d, %Y"))
        
        # Format authors (or use site name if no authors)
        if authors:
            author_str = self._format_author_list(authors)
        elif site_name:
            author_str = site_name
        else:
            author_str = ""
        
        # Format: Author, A. A. (Year, Month Day). Title. Site Name. URL
        parts = []
        if author_str:
            parts.append(author_str)
        if year and year != "n.d.":
            parts.append(f"({year}).")
        elif retrieved_date:
            parts.append(f"({retrieved_date}).")
        if title:
            parts.append(f"{title}.")
        if site_name and authors:  # Don't repeat if site_name was used as author
            parts.append(f"{site_name}.")
        if url:
            parts.append(url)
        
        return " ".join(parts)
    
    def _format_chapter_reference(self, ref: Dict[str, Any]) -> str:
        """Format book chapter reference in APA 7 style"""
        authors = ref.get("authors", [])
        year = ref.get("year", "n.d.")
        chapter_title = ref.get("title", ref.get("chapter_title", ""))
        editors = ref.get("editors", [])
        book_title = ref.get("book_title", ref.get("source", ""))
        publisher = ref.get("publisher", "")
        pages = ref.get("pages", "")
        
        # Format chapter authors
        author_str = self._format_author_list(authors)
        
        # Format editors
        editor_str = self._format_author_list(editors, is_editor=True)
        
        # Format: Author, A. A. (Year). Chapter title. In E. E. Editor (Ed.), Book title (pp. pages). Publisher.
        parts = []
        if author_str:
            parts.append(author_str)
        if year:
            parts.append(f"({year}).")
        if chapter_title:
            parts.append(f"{chapter_title}.")
        if editor_str and book_title:
            parts.append(f"In {editor_str} (Ed.), {book_title}")
        elif book_title:
            parts.append(f"In {book_title}")
        if pages:
            parts.append(f"(pp. {pages}).")
        elif book_title:
            parts.append(".")
        if publisher:
            parts.append(f"{publisher}.")
        
        return " ".join(parts)
    
    def _format_generic_reference(self, ref: Dict[str, Any]) -> str:
        """Format generic reference when type is unknown"""
        authors = ref.get("authors", [])
        year = ref.get("year", "n.d.")
        title = ref.get("title", "")
        source = ref.get("source", "")
        
        author_str = self._format_author_list(authors)
        
        parts = []
        if author_str:
            parts.append(author_str)
        if year:
            parts.append(f"({year}).")
        if title:
            parts.append(f"{title}.")
        if source:
            parts.append(f"{source}.")
        
        return " ".join(parts)
    
    def _format_author_list(self, authors: List[str], is_editor: bool = False) -> str:
        """Format list of authors for reference list"""
        if not authors:
            return ""
        
        if len(authors) == 1:
            return self._format_author_name(authors[0], for_citation=False)
        
        elif len(authors) <= 7:
            formatted = [self._format_author_name(a, for_citation=False) for a in authors]
            if len(formatted) == 2:
                return f"{formatted[0]} & {formatted[1]}"
            else:
                return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"
        
        else:
            # More than 7 authors: list first 6, then et al.
            formatted = [self._format_author_name(a, for_citation=False) for a in authors[:6]]
            return ", ".join(formatted) + " et al."
    
    def _normalize_author(self, author: str) -> str:
        """Normalize author name for comparison"""
        # Remove extra spaces, convert to lowercase, remove punctuation
        normalized = re.sub(r'[^\w\s]', '', author.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def generate_reference_list(
        self,
        references: List[Dict[str, Any]],
        format_output: str = "text"
    ) -> str:
        """
        Generate complete reference list from multiple references.
        
        Args:
            references: List of parsed reference dictionaries
            format_output: Output format ("text", "html", "latex")
        
        Returns:
            Formatted reference list with hanging indent
        """
        formatted_refs = []
        for ref in references:
            formatted = self.generate_reference(ref)
            if format_output == "html":
                formatted_refs.append(f'<p style="text-indent: -36px; padding-left: 36px;">{formatted}</p>')
            elif format_output == "latex":
                formatted_refs.append(f"\\hangindent=36pt {formatted}\\\\")
            else:  # text
                formatted_refs.append(f"\t{formatted}")
        
        return "\n".join(formatted_refs)


# Singleton instance
apa7_service = APA7Service()

