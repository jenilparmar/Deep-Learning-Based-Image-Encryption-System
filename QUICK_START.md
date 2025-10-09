# 🚀 Quick Start Guide - Image Encryption System

This guide will help you run both the backend and frontend of the Image Encryption System.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

## Step 1: Setup Backend

### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Start the Flask Server

```bash
python app.py
```

The backend will start on `http://localhost:5000`

You should see:
```
🚀 Starting Flask Image Encryption API...
📡 Server running on http://localhost:5000
🔐 Endpoints:
   POST /api/process - Encrypt/Decrypt images
   GET  /api/health  - Health check
```

### Test the Backend (Optional)

Open a new terminal and run:

```bash
cd backend
python test_api.py
```

## Step 2: Setup Frontend

### Install Node Dependencies

Open a **new terminal** and run:

```bash
cd Frontend
npm install
```

### Start the Development Server

```bash
npm run dev
```

The frontend will start on `http://localhost:5173` (or another port if 5173 is busy)

## Step 3: Use the Application

1. Open your browser and go to `http://localhost:5173`
2. Select operation (Encrypt/Decrypt)
3. Generate or enter an encryption key (minimum 8 characters)
4. Upload an image (PNG or JPEG)
5. Click "Process Image"
6. Download the result

## 🔥 Both Servers Must Be Running

Make sure BOTH servers are running simultaneously:
- **Backend**: `http://localhost:5000` (Flask)
- **Frontend**: `http://localhost:5173` (Vite)

## 📝 Notes

- Images are converted to grayscale during processing
- Minimum key length: 8 characters
- Recommended key length: 16+ characters for better security
- Use the same key for encryption and decryption

## 🐛 Troubleshooting

### Backend Issues

**Error: Module not found**
```bash
# Make sure you're in the backend directory
cd backend
pip install -r requirements.txt
```

**Port 5000 already in use**
- Stop other applications using port 5000
- Or change the port in `backend/app.py` (last line)

### Frontend Issues

**Port 5173 already in use**
- The Vite dev server will automatically try the next available port
- Or stop other applications using port 5173

**CORS errors**
- Make sure the backend server is running
- Check that the backend URL in `Frontend/src/App.jsx` matches your backend port

### Connection Issues

If you see "Failed to process image":
1. Verify the backend is running (`http://localhost:5000/api/health`)
2. Check browser console for detailed error messages
3. Ensure no firewall is blocking local connections

## 🎉 Success!

If everything is working, you should be able to:
- ✅ Upload images
- ✅ Generate encryption keys
- ✅ Encrypt images
- ✅ Decrypt images (using the same key)
- ✅ Download results
