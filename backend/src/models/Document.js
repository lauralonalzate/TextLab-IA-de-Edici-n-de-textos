const mongoose = require('mongoose');

const documentSchema = new mongoose.Schema({
  title: {
    type: String,
    required: [true, 'Document title is required'],
    trim: true,
    maxlength: [200, 'Title cannot exceed 200 characters']
  },
  content: {
    type: String,
    required: [true, 'Document content is required'],
    default: ''
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'User ID is required']
  }
}, {
  timestamps: true
});

// Index for faster queries
documentSchema.index({ user: 1, createdAt: -1 });
documentSchema.index({ title: 'text', content: 'text' }); // Text search index

const Document = mongoose.model('Document', documentSchema);

module.exports = Document;

