/**
 * Readability Statistics Service
 * 
 * Calculates various readability metrics for text:
 * - Word count
 * - Character count
 * - Reading time estimation
 * - Sentence count
 * - Paragraph count
 */

const calculateStatistics = (text) => {
  if (!text || typeof text !== 'string') {
    throw new Error('Text must be a non-empty string');
  }

  // Word count (split by whitespace and filter empty strings)
  const words = text.trim().split(/\s+/).filter(word => word.length > 0);
  const wordCount = words.length;

  // Character count (excluding spaces)
  const characterCount = text.replace(/\s/g, '').length;
  const characterCountWithSpaces = text.length;

  // Sentence count (split by sentence-ending punctuation)
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  const sentenceCount = sentences.length;

  // Paragraph count (split by double newlines or single newline followed by content)
  const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim().length > 0);
  const paragraphCount = paragraphs.length || 1; // At least 1 paragraph

  // Average words per sentence
  const avgWordsPerSentence = sentenceCount > 0 ? (wordCount / sentenceCount).toFixed(2) : 0;

  // Average characters per word
  const avgCharsPerWord = wordCount > 0 ? (characterCount / wordCount).toFixed(2) : 0;

  // Reading time estimation (average reading speed: 200-250 words per minute)
  // Using 225 words per minute as average
  const readingTimeMinutes = Math.ceil(wordCount / 225);
  const readingTimeSeconds = Math.ceil((wordCount / 225) * 60);

  return {
    wordCount,
    characterCount,
    characterCountWithSpaces,
    sentenceCount,
    paragraphCount,
    avgWordsPerSentence: parseFloat(avgWordsPerSentence),
    avgCharsPerWord: parseFloat(avgCharsPerWord),
    readingTime: {
      minutes: readingTimeMinutes,
      seconds: readingTimeSeconds,
      formatted: readingTimeMinutes > 0 
        ? `${readingTimeMinutes} min${readingTimeMinutes > 1 ? 's' : ''}`
        : '< 1 min'
    }
  };
};

module.exports = {
  calculateStatistics
};

