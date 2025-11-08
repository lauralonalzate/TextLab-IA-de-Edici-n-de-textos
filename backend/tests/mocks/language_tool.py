"""
Mock for LanguageTool Python library.

Use this in tests to avoid requiring LanguageTool installation.
"""
from typing import List, Dict, Any


class MockLanguageTool:
    """Mock LanguageTool instance"""
    
    def __init__(self, language='en-US'):
        self.language = language
    
    def check(self, text: str) -> List[Dict[str, Any]]:
        """
        Mock check method that returns sample suggestions.
        
        Args:
            text: Text to check
        
        Returns:
            List of mock matches
        """
        matches = []
        
        # Simple mock: find common errors
        if "teh" in text.lower():
            matches.append({
                "ruleId": "TYPOS",
                "message": "Possible spelling mistake",
                "replacements": [{"value": "the"}],
                "offset": text.lower().index("teh"),
                "length": 3,
                "context": {"text": text, "offset": 0, "length": len(text)},
            })
        
        if "recieve" in text.lower():
            matches.append({
                "ruleId": "TYPOS",
                "message": "Possible spelling mistake",
                "replacements": [{"value": "receive"}],
                "offset": text.lower().index("recieve"),
                "length": 7,
                "context": {"text": text, "offset": 0, "length": len(text)},
            })
        
        return matches
    
    def close(self):
        """Mock close method"""
        pass


def mock_language_tool_patch():
    """
    Context manager or decorator to patch language_tool_python.
    
    Usage:
        @mock_language_tool_patch()
        def test_something():
            ...
    """
    return patch('language_tool_python.LanguageTool', MockLanguageTool)

