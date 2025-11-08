"""
Statistics Service for calculating document metrics.

Calculates word count, character count, reading time, and readability metrics.
"""
import logging
from typing import Dict, Any
from datetime import datetime

try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    logging.warning("textstat not available. Readability metrics will not be calculated.")

logger = logging.getLogger(__name__)


class StatsService:
    """Service for calculating document statistics"""
    
    # Reading speed in words per minute
    READING_SPEED_WPM = 200
    
    def calculate_stats(self, content: str) -> Dict[str, Any]:
        """
        Calculate comprehensive document statistics.
        
        Args:
            content: Document content text
        
        Returns:
            Dictionary with all calculated statistics
        """
        if not content:
            return self._empty_stats()
        
        # Basic counts
        word_count = len(content.split())
        char_count = len(content)
        char_count_no_spaces = len(content.replace(" ", ""))
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        sentence_count = len([s for s in content.split('.') if s.strip()])
        
        # Reading time (200 words per minute)
        reading_time_minutes = word_count / self.READING_SPEED_WPM
        reading_time_seconds = int(reading_time_minutes * 60)
        
        # Format reading time
        if reading_time_minutes < 1:
            reading_time_display = f"{reading_time_seconds} seconds"
        elif reading_time_minutes < 60:
            reading_time_display = f"{int(reading_time_minutes)} minutes"
        else:
            hours = int(reading_time_minutes // 60)
            minutes = int(reading_time_minutes % 60)
            reading_time_display = f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
        
        stats = {
            "word_count": word_count,
            "character_count": char_count,
            "character_count_no_spaces": char_count_no_spaces,
            "paragraph_count": paragraph_count,
            "sentence_count": sentence_count,
            "reading_time_minutes": round(reading_time_minutes, 2),
            "reading_time_seconds": reading_time_seconds,
            "reading_time_display": reading_time_display,
            "average_words_per_sentence": round(word_count / sentence_count, 2) if sentence_count > 0 else 0,
            "average_sentences_per_paragraph": round(sentence_count / paragraph_count, 2) if paragraph_count > 0 else 0,
        }
        
        # Readability metrics (if textstat available)
        if TEXTSTAT_AVAILABLE:
            try:
                stats["flesch_reading_ease"] = round(textstat.flesch_reading_ease(content), 2)
                stats["flesch_kincaid_grade"] = round(textstat.flesch_kincaid_grade(content), 2)
                stats["automated_readability_index"] = round(textstat.automated_readability_index(content), 2)
                stats["coleman_liau_index"] = round(textstat.coleman_liau_index(content), 2)
                stats["dale_chall_readability_score"] = round(textstat.dale_chall_readability_score(content), 2)
            except Exception as e:
                logger.warning(f"Error calculating readability metrics: {e}")
                stats["flesch_reading_ease"] = None
                stats["flesch_kincaid_grade"] = None
                stats["automated_readability_index"] = None
                stats["coleman_liau_index"] = None
                stats["dale_chall_readability_score"] = None
        else:
            stats["flesch_reading_ease"] = None
            stats["flesch_kincaid_grade"] = None
            stats["automated_readability_index"] = None
            stats["coleman_liau_index"] = None
            stats["dale_chall_readability_score"] = None
        
        # Add metadata
        stats["calculated_at"] = datetime.utcnow().isoformat()
        stats["reading_speed_wpm"] = self.READING_SPEED_WPM
        
        return stats
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty stats structure"""
        return {
            "word_count": 0,
            "character_count": 0,
            "character_count_no_spaces": 0,
            "paragraph_count": 0,
            "sentence_count": 0,
            "reading_time_minutes": 0,
            "reading_time_seconds": 0,
            "reading_time_display": "0 seconds",
            "average_words_per_sentence": 0,
            "average_sentences_per_paragraph": 0,
            "flesch_reading_ease": None,
            "flesch_kincaid_grade": None,
            "automated_readability_index": None,
            "coleman_liau_index": None,
            "dale_chall_readability_score": None,
            "calculated_at": datetime.utcnow().isoformat(),
            "reading_speed_wpm": self.READING_SPEED_WPM,
        }


# Singleton instance
stats_service = StatsService()

