const textCorrectionService = require('../services/textCorrectionService');
const readabilityService = require('../services/readabilityService');

// @desc    Correct text (placeholder)
// @route   POST /api/editor/correct
// @access  Private
const correctText = async (req, res) => {
  try {
    const { text } = req.body;

    if (!text || typeof text !== 'string') {
      return res.status(400).json({
        success: false,
        message: 'Text is required and must be a string'
      });
    }

    // Use text correction service
    const correctedText = await textCorrectionService.correctText(text);

    res.status(200).json({
      success: true,
      data: {
        original: text,
        corrected: correctedText,
        changes: [] // Placeholder for future implementation
      }
    });
  } catch (error) {
    console.error('Correct text error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error while correcting text'
    });
  }
};

// @desc    Calculate readability statistics
// @route   POST /api/editor/statistics
// @access  Private
const getStatistics = async (req, res) => {
  try {
    const { text } = req.body;

    if (!text || typeof text !== 'string') {
      return res.status(400).json({
        success: false,
        message: 'Text is required and must be a string'
      });
    }

    // Use readability service
    const statistics = await readabilityService.calculateStatistics(text);

    res.status(200).json({
      success: true,
      data: statistics
    });
  } catch (error) {
    console.error('Get statistics error:', error);
    res.status(500).json({
      success: false,
      message: 'Server error while calculating statistics'
    });
  }
};

module.exports = {
  correctText,
  getStatistics
};

