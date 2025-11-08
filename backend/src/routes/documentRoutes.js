const express = require('express');
const router = express.Router();
const {
  getDocuments,
  getDocument,
  createDocument,
  updateDocument,
  deleteDocument
} = require('../controllers/documentController');
const authMiddleware = require('../middlewares/authMiddleware');

// All document routes require authentication
router.use(authMiddleware);

router.route('/')
  .get(getDocuments)
  .post(createDocument);

router.route('/:id')
  .get(getDocument)
  .put(updateDocument)
  .delete(deleteDocument);

module.exports = router;

