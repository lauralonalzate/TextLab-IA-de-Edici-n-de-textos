const express = require('express');
const router = express.Router();
const {
  correctText,
  getStatistics
} = require('../controllers/editorController');
const authMiddleware = require('../middlewares/authMiddleware');

// All editor routes require authentication
router.use(authMiddleware);

router.post('/correct', correctText);
router.post('/statistics', getStatistics);

module.exports = router;

