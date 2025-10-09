# Flask Backend for Image Encryption System

This is the backend API for the Deep Learning Based Image Encryption System.

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### POST `/api/process`

Encrypt or decrypt an image.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `image`: Image file (PNG, JPEG)
  - `key`: Encryption/decryption key (string, min 8 characters)
  - `operation`: "encrypt" or "decrypt"

**Response:**
```json
{
  "success": true,
  "message": "Image encrypted successfully",
  "image": "data:image/png;base64,...",
  "operation": "encrypt"
}
```

### GET `/api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "Image Encryption API is running"
}
```

## Error Handling

All errors return a JSON response with an `error` field:

```json
{
  "success": false,
  "error": "Error message"
}
```

## CORS

CORS is enabled for all origins to allow frontend communication.
