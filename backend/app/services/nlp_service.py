"""
NLP Service for text analysis (spelling, grammar, style).

Supports both synchronous and asynchronous execution.
"""
import hashlib
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False
    logger.warning("language_tool_python not available. NLP service will use mock responses.")


class Suggestion:
    """Represents a text correction suggestion"""
    def __init__(
        self,
        start: int,
        end: int,
        error_type: str,
        suggestion: str,
        rule_id: Optional[str] = None,
        confidence: float = 1.0,
    ):
        self.start = start
        self.end = end
        self.error_type = error_type
        self.suggestion = suggestion
        self.rule_id = rule_id
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "start": self.start,
            "end": self.end,
            "error_type": self.error_type,
            "suggestion": self.suggestion,
            "rule_id": self.rule_id,
            "confidence": self.confidence,
        }


class NLPService:
    """Service for NLP text analysis"""
    
    def __init__(self):
        self.tool = None
        if LANGUAGE_TOOL_AVAILABLE:
            try:
                self.tool = language_tool_python.LanguageTool('es-ES')  # Default to Spanish
            except Exception as e:
                logger.warning(f"Failed to initialize LanguageTool: {e}")
                self.tool = None

    def analyze_text(self, text: str, language: str = "es-ES") -> List[Dict[str, Any]]:
        """
        Analyze text for spelling, grammar, and style errors.
        
        Args:
            text: Text to analyze
            language: Language code (default: es-ES)
        
        Returns:
            List of suggestion dictionaries
        """
        if not text or not text.strip():
            return []
        
        suggestions = []
        
        # Use LanguageTool if available
        if self.tool and LANGUAGE_TOOL_AVAILABLE:
            try:
                # Reinitialize tool if language changed
                if hasattr(self.tool, 'language') and self.tool.language != language:
                    self.tool = language_tool_python.LanguageTool(language)
                
                matches = self.tool.check(text)
                
                for match in matches:
                    suggestion = Suggestion(
                        start=match.offset,
                        end=match.offset + match.errorLength,
                        error_type=match.rule.category,
                        suggestion=match.replacements[0] if match.replacements else "",
                        rule_id=match.ruleId,
                        confidence=1.0 - (match.rule.quality.typoRatio if hasattr(match.rule.quality, 'typoRatio') else 0.0),
                    )
                    suggestions.append(suggestion.to_dict())
            
            except Exception as e:
                logger.error(f"Error in LanguageTool analysis: {e}")
                # Fall back to mock if LanguageTool fails
                suggestions = self._mock_analysis(text)
        
        else:
            # Use mock analysis if LanguageTool is not available
            suggestions = self._mock_analysis(text)
        
        # Add style analysis
        style_suggestions = self._analyze_style(text)
        suggestions.extend(style_suggestions)
        
        return suggestions

    def _analyze_style(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze text for style issues (simple rules).
        
        Returns style suggestions based on:
        - Long sentences
        - Passive voice (basic detection)
        - Adverb usage
        """
        suggestions = []
        sentences = text.split('.')
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check for long sentences (>150 characters)
            if len(sentence) > 150:
                # Find sentence position in original text
                start_pos = text.find(sentence)
                if start_pos != -1:
                    suggestions.append({
                        "start": start_pos,
                        "end": start_pos + len(sentence),
                        "error_type": "STYLE",
                        "suggestion": "Consider breaking this long sentence into shorter ones for better readability.",
                        "rule_id": "LONG_SENTENCE",
                        "confidence": 0.7,
                    })
            
            # Check for passive voice indicators (basic)
            passive_indicators = [" fue ", " fueron ", " es ", " son ", " está ", " están "]
            for indicator in passive_indicators:
                if indicator in sentence.lower():
                    start_pos = text.find(sentence)
                    if start_pos != -1:
                        suggestions.append({
                            "start": start_pos,
                            "end": start_pos + len(sentence),
                            "error_type": "STYLE",
                            "suggestion": "Consider using active voice instead of passive voice.",
                            "rule_id": "PASSIVE_VOICE",
                            "confidence": 0.5,
                        })
                        break
        
        return suggestions

    def _mock_analysis(self, text: str) -> List[Dict[str, Any]]:
        """
        Mock analysis for testing when LanguageTool is not available.
        
        Returns some example suggestions.
        """
        suggestions = []
        
        # Simple mock: find common errors
        common_errors = {
            "tecnologia": "tecnología",
            "organizacion": "organización",
            "comunicacion": "comunicación",
        }
        
        text_lower = text.lower()
        for error, correction in common_errors.items():
            if error in text_lower:
                pos = text_lower.find(error)
                suggestions.append({
                    "start": pos,
                    "end": pos + len(error),
                    "error_type": "SPELLING",
                    "suggestion": correction,
                    "rule_id": "MOCK_SPELLING",
                    "confidence": 0.9,
                })
        
        return suggestions

    @staticmethod
    def compute_text_hash(text: str) -> str:
        """Compute SHA-256 hash of text"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Singleton instance
nlp_service = NLPService()

