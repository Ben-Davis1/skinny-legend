# Skinny Legend - Setup Guide

## Quick Start

### Option 1: Using the start scripts (Recommended)

1. **Start the Backend** (Terminal 1):
```bash
./start-backend.sh
```
This will:
- Create a Python virtual environment
- Install all dependencies
- Initialize the database
- Start the Flask server on http://localhost:8000

2. **Start the Frontend** (Terminal 2):
```bash
./start-frontend.sh
```
This will:
- Install npm dependencies
- Start the Vite dev server on http://localhost:5173

3. **Configure API Key**:
- Edit `backend/.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

4. **Open the app**:
- Navigate to http://localhost:5173 in your browser

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run the server
python3 app.py
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Run the dev server
npm run dev
```

## Configuration

### Backend Environment Variables (backend/.env)

```
DATABASE_URL=sqlite:///./skinny_legend.db
ANTHROPIC_API_KEY=your_api_key_here
ALLOWED_ORIGINS=http://localhost:5173
UPLOAD_DIR=./uploads
```

### Frontend Environment Variables (frontend/.env)

```
VITE_API_URL=http://localhost:8000
```

## Getting an Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key to your backend/.env file

## Testing the App

### 1. Health Check
Visit http://localhost:8000/health - you should see:
```json
{
  "status": "healthy",
  "message": "Skinny Legend API is running"
}
```

### 2. Create Your Profile
1. Open http://localhost:5173
2. Navigate to the Profile page
3. Enter your details (age, weight, height, etc.)
4. Save to see your calculated BMR and TDEE

### 3. Add Food Entry
1. Go to the Dashboard
2. Fill out the food entry form
3. Click "Add Food"
4. See it appear in your daily log with updated totals

### 4. Test Barcode Scanner
1. On the Dashboard, click "Show Barcode Scanner"
2. Allow camera access
3. Scan any product barcode
4. The food will be automatically added

### 5. Test AI Features
1. **Image Analysis**:
   - Go to Saved Images
   - Upload a photo of food
   - Click "Analyze"
   - Review AI-detected nutrition info

2. **AI Chat**:
   - Go to AI Chat
   - Type: "I ate 2 eggs and toast for breakfast"
   - Click Send
   - The AI will extract food items
   - Click "Add" to log them

## Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Database errors:**
```bash
cd backend
rm skinny_legend.db  # Delete old database
python3 -c "from database import init_db; init_db()"
```

**Port already in use:**
Edit `backend/app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=8001)
```

### Frontend Issues

**"Cannot find module" errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Port already in use:**
Edit `frontend/vite.config.js`:
```javascript
server: {
  port: 5174
}
```

**API connection errors:**
- Check that backend is running on http://localhost:8000
- Verify VITE_API_URL in frontend/.env

### AI Features Not Working

**"API key error":**
- Verify your Anthropic API key is correct in backend/.env
- Check you have API credits available
- Restart the backend after updating .env

**Image analysis fails:**
- Ensure the image is in a supported format (jpg, png, webp)
- Check the image file size (should be < 5MB)
- Verify uploads directory exists and is writable

## Project Structure

```
skinny-legend/
├── backend/
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── app.py          # Flask app
│   ├── database.py     # Database utilities
│   └── schema.sql      # Database schema
├── frontend/
│   ├── src/
│   │   ├── pages/      # Page components
│   │   ├── components/ # Reusable components
│   │   └── lib/        # Utilities (API client)
│   └── index.html
├── start-backend.sh    # Backend startup script
├── start-frontend.sh   # Frontend startup script
└── README.md
```

## Next Steps

1. **Customize**: Adjust the UI styling in `frontend/src/app.css`
2. **Add Features**: Extend the API or add new components
3. **Deploy**: Follow the deployment guide in README.md
4. **Mobile**: Install as PWA on your phone for mobile use

## Support

For issues, questions, or contributions:
- Check the README.md
- Review the code comments
- Test with the health check endpoint
- Verify all environment variables are set

Happy tracking!
