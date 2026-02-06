# Skinny Legend - Quick Reference Guide

## Getting Started (2 minutes)

```bash
# Terminal 1 - Backend
./start-backend.sh

# Edit backend/.env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-...

# Terminal 2 - Frontend
./start-frontend.sh

# Browser
# Open http://localhost:5173
```

## Common Commands

### Backend
```bash
cd backend
source venv/bin/activate           # Activate virtual environment
python3 app.py                     # Start server
python3 -c "from database import init_db; init_db()"  # Reset database
```

### Frontend
```bash
cd frontend
npm run dev                        # Start dev server
npm run build                      # Build for production
npm run preview                    # Preview production build
```

## API Quick Reference

### Daily Logs
```bash
GET    /api/daily-logs              # Get all logs
GET    /api/daily-logs/2024-01-15   # Get specific date
POST   /api/daily-logs              # Create log
PUT    /api/daily-logs/1            # Update log
DELETE /api/daily-logs/1            # Delete log
```

### Food Entries
```bash
GET    /api/food-entries/1          # Get entries for log
POST   /api/food-entries            # Create entry
PUT    /api/food-entries/1          # Update entry
DELETE /api/food-entries/1          # Delete entry
```

### Barcode
```bash
GET    /api/barcode/5449000000996   # Lookup product
```

### Images
```bash
POST   /api/images/upload           # Upload image
GET    /api/images                  # Get all images
GET    /api/images/1                # Get image file
DELETE /api/images/1                # Delete image
```

### AI
```bash
POST   /api/ai/analyze-image        # Analyze food image
POST   /api/chat                    # Chat with AI
POST   /api/ai/calculate-goals      # Calculate TDEE
```

### Profile
```bash
GET    /api/profile                 # Get profile
POST   /api/profile                 # Create profile
PUT    /api/profile                 # Update profile
GET    /api/profile/calculations    # Get BMR/TDEE
```

### Nutrition
```bash
GET    /api/nutrition/2024-01-15    # Get nutrition for date
GET    /api/nutrition/history       # Get date range
GET    /api/nutrition/targets       # Get vitamin targets
POST   /api/nutrition/targets       # Set target
```

## Example API Calls

### Create Food Entry
```bash
curl -X POST http://localhost:8000/api/food-entries \
  -H "Content-Type: application/json" \
  -d '{
    "daily_log_id": 1,
    "name": "Chicken Breast",
    "calories": 165,
    "protein_g": 31,
    "carbs_g": 0,
    "fat_g": 3.6,
    "serving_size": "100g",
    "meal_type": "lunch"
  }'
```

### Analyze Image
```bash
curl -X POST http://localhost:8000/api/ai/analyze-image \
  -H "Content-Type: application/json" \
  -d '{"image_id": 1}'
```

### Chat with AI
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I ate 2 eggs and toast for breakfast",
    "history": []
  }'
```

## Database Schema Quick Reference

### Key Tables

**daily_logs**
- id, user_id, date, total_calories, total_water_ml, exercise_minutes, notes

**food_entries**
- id, daily_log_id, name, calories, protein_g, carbs_g, fat_g, fiber_g, sugar_g, meal_type, serving_size

**micronutrients**
- id, food_entry_id, vitamin_a_mcg, vitamin_c_mg, vitamin_d_mcg, calcium_mg, iron_mg, etc.

**user_profile**
- id, user_id, age, weight_kg, height_cm, gender, activity_level, goal, bmr, tdee

## Formulas Used

### BMR (Basal Metabolic Rate) - Mifflin-St Jeor
```
Male:   BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
Female: BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161
```

### TDEE (Total Daily Energy Expenditure)
```
Sedentary:         BMR × 1.2
Lightly Active:    BMR × 1.375
Moderately Active: BMR × 1.55
Very Active:       BMR × 1.725
Extra Active:      BMR × 1.9
```

### Calorie Goals
```
Weight Loss:    TDEE - 500 cal
Maintenance:    TDEE
Weight Gain:    TDEE + 500 cal
```

### BMI (Body Mass Index)
```
BMI = weight_kg / (height_m)²
```

## Component Reference

### Pages (frontend/src/pages/)
- `Dashboard.svelte` - Main daily tracking view
- `History.svelte` - Charts and historical data
- `Nutrition.svelte` - Macro/micro breakdown
- `SavedImages.svelte` - Image gallery and AI analysis
- `AIChat.svelte` - Chat interface
- `Profile.svelte` - User settings and calculations

### Components (frontend/src/components/)
- `FoodEntry.svelte` - Food entry form
- `WaterTracker.svelte` - Water intake tracker
- `BarcodeScanner.svelte` - Camera barcode scanner

### Services (backend/services/)
- `ai_service.py` - Claude API integration
- `image_service.py` - Image processing
- `calculations.py` - BMR/TDEE formulas
- `barcode_service.py` - (using OpenFoodFacts directly)

## Troubleshooting

### Backend won't start
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database is corrupted
```bash
cd backend
rm skinny_legend.db
python3 -c "from database import init_db; init_db()"
```

### AI features not working
1. Check ANTHROPIC_API_KEY in backend/.env
2. Verify API credits at console.anthropic.com
3. Restart backend after changing .env

### Can't access camera
1. Use HTTPS or localhost only
2. Grant camera permissions in browser
3. Check browser console for errors

## File Locations

### Configuration
- Backend env: `backend/.env`
- Frontend env: `frontend/.env`
- Database: `backend/skinny_legend.db`
- Uploads: `backend/uploads/`

### Logs
- Backend: Terminal output
- Frontend: Browser console

## Useful Development URLs

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Health Check: http://localhost:8000/health
- API Docs: See README.md

## Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
# Output in: dist/
```

### Environment Variables (Production)
```
Backend:
- DATABASE_URL (PostgreSQL recommended)
- ANTHROPIC_API_KEY
- ALLOWED_ORIGINS (your frontend URL)
- UPLOAD_DIR

Frontend:
- VITE_API_URL (your backend URL)
```

## Need Help?

1. Check SETUP.md for detailed setup instructions
2. Read README.md for full documentation
3. Review IMPLEMENTATION_SUMMARY.md for architecture details
4. Check code comments in source files
5. Test with /health endpoint to verify backend
