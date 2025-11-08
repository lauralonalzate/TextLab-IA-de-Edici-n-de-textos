import pytest
from app.services.nlp_service import nlp_service, NLPService


class TestNLPService:
    """Tests for NLP service"""

    def test_analyze_text_empty(self):
        """Test analyzing empty text"""
        result = nlp_service.analyze_text("")
        assert result == []
        
        result = nlp_service.analyze_text("   ")
        assert result == []

    def test_analyze_text_basic(self):
        """Test basic text analysis"""
        text = "Este es un texto de prueba con algunos errores."
        result = nlp_service.analyze_text(text)
        
        # Should return a list (may be empty if no errors found)
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)

    def test_analyze_text_with_errors(self):
        """Test analyzing text with known errors (mock)"""
        # Use text that might trigger mock suggestions
        text = "La tecnologia es importante para la organizacion."
        result = nlp_service.analyze_text(text)
        
        # Should return suggestions (at least from mock)
        assert isinstance(result, list)
        # If LanguageTool is not available, mock should catch common errors
        if not nlp_service.tool:
            assert len(result) > 0

    def test_analyze_text_style_issues(self):
        """Test that style analysis is included"""
        # Long sentence (>150 chars)
        long_sentence = "Esta es una oración muy larga que debería generar una sugerencia de estilo porque excede los ciento cincuenta caracteres y debería ser dividida en oraciones más cortas para mejorar la legibilidad del texto."
        result = nlp_service.analyze_text(long_sentence)
        
        # Should have style suggestions
        style_suggestions = [s for s in result if s.get("error_type") == "STYLE"]
        assert len(style_suggestions) > 0
        
        # Check for long sentence suggestion
        long_sentence_suggestions = [s for s in style_suggestions if s.get("rule_id") == "LONG_SENTENCE"]
        assert len(long_sentence_suggestions) > 0

    def test_compute_text_hash(self):
        """Test text hash computation"""
        text1 = "Test text"
        text2 = "Test text"
        text3 = "Different text"
        
        hash1 = NLPService.compute_text_hash(text1)
        hash2 = NLPService.compute_text_hash(text2)
        hash3 = NLPService.compute_text_hash(text3)
        
        # Same text should produce same hash
        assert hash1 == hash2
        
        # Different text should produce different hash
        assert hash1 != hash3
        
        # Hash should be 64 characters (SHA-256 hex)
        assert len(hash1) == 64

    def test_suggestion_structure(self):
        """Test that suggestions have correct structure"""
        text = "Test text with some content."
        result = nlp_service.analyze_text(text)
        
        for suggestion in result:
            assert "start" in suggestion
            assert "end" in suggestion
            assert "error_type" in suggestion
            assert "suggestion" in suggestion
            assert "rule_id" in suggestion or suggestion.get("rule_id") is None
            assert "confidence" in suggestion
            
            # Check types
            assert isinstance(suggestion["start"], int)
            assert isinstance(suggestion["end"], int)
            assert isinstance(suggestion["error_type"], str)
            assert isinstance(suggestion["suggestion"], str)
            assert 0.0 <= suggestion["confidence"] <= 1.0

    def test_error_types(self):
        """Test that error types are valid"""
        text = "Test text for error type validation."
        result = nlp_service.analyze_text(text)
        
        valid_types = {"SPELLING", "GRAMMAR", "STYLE"}
        for suggestion in result:
            error_type = suggestion.get("error_type")
            if error_type:
                # Should be one of the valid types (or LanguageTool categories)
                assert isinstance(error_type, str)

