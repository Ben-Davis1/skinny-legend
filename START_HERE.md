# 🚀 START HERE - Skinny Legend Quick Start

## ✅ Installation Complete!

All dependencies are now installed. Follow these simple steps to run the app:

## Step 1: Add Your API Key

Edit the file `backend/.env` and add your Anthropic API key:

```bash
# Open with any text editor
open backend/.env

# Or use vim/nano
nano backend/.env
```

Change this line:
```
ANTHROPIC_API_KEY=your_api_key_here
```

To your actual API key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**Get an API key:** https://console.anthropic.com/settings/keys

## Step 2: Start the Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
python3 app.py
```

You should see:
```
* Running on http://localhost:8000
```

**Keep this terminal running!**

## Step 3: Start the Frontend (Terminal 2)

Open a NEW terminal and run:

```bash
cd frontend
npm install
npm run dev
```

You should see:
```
Local: http://localhost:5173/
```

## Step 4: Open the App

Open your browser and go to:
**http://localhost:5173**

## ✅ Quick Test

1. **Backend Health Check:** Visit http://localhost:8000/health
   - Should return: `{"status": "healthy", ...}`

2. **Create Profile:**
   - Go to the Profile page
   - Enter your details
   - Save to see BMR/TDEE calculations

3. **Add Food:**
   - Go to Dashboard
   - Fill out the food form
   - Click "Add Food"
   - See your daily totals update

## 🎯 What You Can Do

- **Dashboard:** Track daily food, water, exercise
- **History:** View charts and past data
- **Nutrition:** See detailed macro/micro breakdown
- **Saved Images:** Upload food photos for AI analysis
- **AI Chat:** Type what you ate in natural language
- **Profile:** Calculate your BMR and calorie goals
- **Barcode Scanner:** Scan products (requires HTTPS or localhost)

## 🔧 If Something Goes Wrong

### Backend won't start?
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-CORS python-dotenv requests Pillow anthropic
python3 app.py
```

### Frontend won't start?
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Database issues?
```bash
cd backend
rm skinny_legend.db
source venv/bin/activate
python3 -c "from database import init_db; init_db()"
```

## 📚 More Help

- **SETUP.md** - Detailed setup instructions
- **README.md** - Full documentation
- **QUICK_REFERENCE.md** - API reference
- **INSTALL.md** - Troubleshooting

## 🎉 You're All Set!

The backend is running on **http://localhost:8000**
The frontend should run on **http://localhost:5173**

Enjoy tracking your nutrition!
