"""
Tests for NLP service with explicit LanguageTool mocking.
"""
import pytest
from unittest.mock import patch, MagicMock

from app.services.nlp_service import nlp_service, NLPService
from tests.mocks.language_tool import MockLanguageTool, mock_language_tool_patch


class TestNLPServiceWithMock:
    """Tests for NLP service with mocked LanguageTool"""

    @mock_language_tool_patch()
    def test_analyze_text_with_mock(self):
        """Test text analysis using mocked LanguageTool"""
        text = "This is teh test text with recieve error."
        result = nlp_service.analyze_text(text)
        
        # Should return suggestions from mock
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check that mock suggestions are included
        suggestions_text = " ".join([s["suggestion"] for s in result])
        assert "the" in suggestions_text or "receive" in suggestions_text

    @patch('app.services.nlp_service.language_tool_python.LanguageTool')
    def test_analyze_text_with_patch(self, mock_lt_class):
        """Test text analysis with patched LanguageTool"""
        # Create mock instance
        mock_tool = MagicMock()
        mock_tool.check.return_value = [
            {
                "ruleId": "TYPOS",
                "message": "Possible spelling mistake",
                "replacements": [{"value": "the"}],
                "offset": 8,
                "length": 3,
                "context": {"text": "This is teh test", "offset": 0, "length": 15},
            }
        ]
        mock_lt_class.return_value = mock_tool
        
        # Reinitialize service to use mock
        service = NLPService()
        result = service.analyze_text("This is teh test")
        
        # Should return suggestions
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["error_type"] in ["SPELLING", "GRAMMAR", "TYPOS"]

    def test_analyze_text_without_language_tool(self):
        """Test that service works even without LanguageTool"""
        # Temporarily disable LanguageTool
        original_tool = nlp_service.tool
        nlp_service.tool = None
        
        try:
            text = "This is a very long sentence that should trigger style analysis because it exceeds one hundred and fifty characters and should be split into shorter sentences for better readability."
            result = nlp_service.analyze_text(text)
            
            # Should still return style suggestions
            assert isinstance(result, list)
            style_suggestions = [s for s in result if s.get("error_type") == "STYLE"]
            assert len(style_suggestions) > 0
        finally:
            # Restore original tool
            nlp_service.tool = original_tool

    @mock_language_tool_patch()
    def test_suggestion_format_with_mock(self):
        """Test that mock suggestions have correct format"""
        text = "teh recieve"
        result = nlp_service.analyze_text(text)
        
        for suggestion in result:
            assert "start" in suggestion
            assert "end" in suggestion
            assert "error_type" in suggestion
            assert "suggestion" in suggestion
            assert "confidence" in suggestion
            
            # Check that indices are valid
            assert 0 <= suggestion["start"] < len(text)
            assert suggestion["start"] < suggestion["end"] <= len(text)

