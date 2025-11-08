# TextLab Backend

Backend API for TextLab - An online academic text editor with AI-assisted correction and APA7 citation validation.

## 📋 Description

TextLab Backend is a RESTful API built with Node.js and Express.js that provides:

- **User Authentication**: Registration and login with JWT
- **Document Management**: Create, read, update, and delete documents
- **Text Correction**: AI-assisted text correction (placeholder for future implementation)
- **Readability Statistics**: Word count, reading time, and other metrics
- **APA 7 Support**: Citation validation and formatting (placeholder for future implementation)

## 🚀 Tech Stack

- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: MongoDB with Mongoose
- **Authentication**: JWT (jsonwebtoken) + bcryptjs
- **Environment**: dotenv
- **CORS**: Enabled for cross-origin requests

## 📦 Prerequisites

- Node.js (v14 or higher)
- MongoDB (local or MongoDB Atlas)
- npm or yarn

## 🏃 Quick Start

### 1. Install Dependencies

```bash
cd backend
npm install
```

### 2. Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` and update the values:

```env
PORT=3000
NODE_ENV=development
MONGODB_URI=mongodb://localhost:27017/textlab
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRE=7d
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Start MongoDB

**Local MongoDB:**
```bash
# Make sure MongoDB is running locally
mongod
```

**MongoDB Atlas:**
- Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Get your connection string
- Update `MONGODB_URI` in `.env`

### 4. Run the Server

**Development mode (with nodemon):**
```bash
npm run dev
```

**Production mode:**
```bash
npm start
```

The server will start on `http://localhost:3000` (or the port specified in `.env`).

## 📁 Project Structure

```
backend/
├── server.js                 # Main server file
├── package.json              # Dependencies and scripts
├── .env.example             # Environment variables template
├── README.md                # This file
└── src/
    ├── config/
    │   └── database.js      # MongoDB connection
    ├── models/
    │   ├── User.js          # User model
    │   └── Document.js      # Document model
    ├── controllers/
    │   ├── authController.js      # Authentication logic
    │   ├── documentController.js  # Document CRUD logic
    │   └── editorController.js    # Editor features logic
    ├── routes/
    │   ├── authRoutes.js     # Authentication routes
    │   ├── documentRoutes.js # Document routes
    │   └── editorRoutes.js   # Editor routes
    ├── middlewares/
    │   └── authMiddleware.js # JWT authentication middleware
    └── services/
        ├── textCorrectionService.js # Text correction service
        ├── readabilityService.js    # Readability statistics
        └── apaService.js             # APA 7 validation (placeholder)
```

## 🔌 API Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "...",
      "name": "John Doe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00.000Z"
    },
    "token": "jwt-token-here"
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Documents

#### Get All Documents
```http
GET /api/documents
Authorization: Bearer <token>
```

#### Get Single Document
```http
GET /api/documents/:id
Authorization: Bearer <token>
```

#### Create Document
```http
POST /api/documents
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My Document",
  "content": "Document content here..."
}
```

#### Update Document
```http
PUT /api/documents/:id
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content..."
}
```

#### Delete Document
```http
DELETE /api/documents/:id
Authorization: Bearer <token>
```

### Editor

#### Correct Text
```http
POST /api/editor/correct
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Text to correct..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "original": "Text to correct...",
    "corrected": "Text to correct...",
    "changes": []
  }
}
```

#### Get Statistics
```http
POST /api/editor/statistics
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Your text here..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "wordCount": 10,
    "characterCount": 50,
    "characterCountWithSpaces": 59,
    "sentenceCount": 2,
    "paragraphCount": 1,
    "avgWordsPerSentence": 5.00,
    "avgCharsPerWord": 5.00,
    "readingTime": {
      "minutes": 1,
      "seconds": 3,
      "formatted": "1 min"
    }
  }
}
```

### Health Check

```http
GET /health
```

## 🔐 Authentication

All protected routes require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

Tokens are returned upon successful registration or login and expire after 7 days (configurable via `JWT_EXPIRE`).

## 🧪 Testing with cURL

### Register
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"password123"}'
```

### Login
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"password123"}'
```

### Create Document
```bash
curl -X POST http://localhost:3000/api/documents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"title":"My Document","content":"Content here"}'
```

### Get Statistics
```bash
curl -X POST http://localhost:3000/api/editor/statistics \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"text":"This is a sample text for testing readability statistics."}'
```

## 🛠️ Development

### Scripts

- `npm start` - Start server in production mode
- `npm run dev` - Start server in development mode with nodemon

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 3000 |
| `NODE_ENV` | Environment (development/production) | development |
| `MONGODB_URI` | MongoDB connection string | mongodb://localhost:27017/textlab |
| `JWT_SECRET` | Secret key for JWT tokens | (required) |
| `JWT_EXPIRE` | JWT token expiration | 7d |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | - |

## 📝 Future Implementations

### Text Correction Service
- Integration with NLP libraries
- Spelling and grammar checking
- Style suggestions
- AI-powered text improvement

### APA 7 Service
- Citation format validation
- Reference list generation
- In-text citation validation
- Automatic citation formatting

## 🔒 Security Notes

- Passwords are hashed using bcryptjs
- JWT tokens are used for authentication
- Passwords are never returned in API responses
- Input validation on all endpoints
- CORS is configured for allowed origins

## 📄 License

[Add your license here]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions, please open an issue in the repository.
