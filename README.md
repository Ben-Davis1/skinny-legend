# Skinny Legend - Calorie & Health Tracking App

A comprehensive calorie and nutrition tracking application with AI-powered food recognition, barcode scanning, and personalized health recommendations.

## Features

- **Daily Food Tracking**: Log meals with detailed macro and micronutrient information
- **Barcode Scanner**: Scan product barcodes for instant nutritional data
- **AI Image Analysis**: Take photos of food and get AI-powered nutrition estimates
- **AI Chat Assistant**: Describe your meals in natural language
- **Water & Exercise Tracking**: Monitor hydration and physical activity
- **Nutrition Breakdown**: Detailed macro and micronutrient analysis
- **History & Analytics**: Visualize your progress with charts
- **Personalized Goals**: Calculate BMR, TDEE, and calorie goals
- **Progressive Web App**: Install on mobile devices for offline use

## Tech Stack

### Frontend
- Svelte + Vite
- Chart.js for visualizations
- html5-qrcode for barcode scanning
- Svelte SPA Router

### Backend
- Python 3.11+ with Flask
- SQLite database
- Anthropic Claude API for AI features
- OpenFoodFacts API for barcode data
- Pillow for image processing

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Anthropic API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Edit `.env` and add your Anthropic API key:
```
DATABASE_URL=sqlite:///./skinny_legend.db
ANTHROPIC_API_KEY=your_api_key_here
ALLOWED_ORIGINS=http://localhost:5173
UPLOAD_DIR=./uploads
```

5. Run the backend:
```bash
python app.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. The default API URL should work:
```
VITE_API_URL=http://localhost:8000
```

5. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Adding Food Entries

1. **Manual Entry**: Fill out the food entry form on the Dashboard
2. **Barcode Scan**: Use the barcode scanner to scan packaged foods
3. **AI Image Analysis**: Upload a food photo and let AI extract nutrition data
4. **AI Chat**: Describe your meal in natural language

### Setting Up Your Profile

1. Navigate to the Profile page
2. Enter your age, weight, height, gender, activity level, and goal
3. View your calculated BMR, TDEE, and personalized calorie goal

### Tracking Progress

- View daily summaries on the Dashboard
- Check historical data and charts on the History page
- Monitor macro and micronutrient intake on the Nutrition page

## API Endpoints

### Daily Logs
- `GET /api/daily-logs` - Get all logs
- `GET /api/daily-logs/{date}` - Get specific day
- `POST /api/daily-logs` - Create new log
- `PUT /api/daily-logs/{id}` - Update log
- `DELETE /api/daily-logs/{id}` - Delete log

### Food Entries
- `GET /api/food-entries/{daily_log_id}` - Get entries for a day
- `POST /api/food-entries` - Add food entry
- `PUT /api/food-entries/{id}` - Update entry
- `DELETE /api/food-entries/{id}` - Delete entry

### Barcode
- `GET /api/barcode/{code}` - Lookup product by barcode

### Images
- `POST /api/images/upload` - Upload food image
- `GET /api/images` - Get all saved images
- `DELETE /api/images/{id}` - Delete image

### AI
- `POST /api/ai/analyze-image` - Analyze food image with AI
- `POST /api/chat` - Chat with AI to add food
- `POST /api/ai/calculate-goals` - Calculate personalized goals

### User Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile
- `GET /api/profile/calculations` - Get BMR/TDEE/goals

### Nutrition
- `GET /api/nutrition/{date}` - Get nutrition breakdown
- `GET /api/nutrition/history` - Get historical data
- `GET /api/nutrition/targets` - Get vitamin targets
- `POST /api/nutrition/targets` - Set vitamin target

## Database Schema

The app uses SQLite with the following tables:
- `users` - User accounts
- `daily_logs` - Daily tracking logs
- `food_entries` - Individual food items
- `micronutrients` - Detailed vitamin/mineral data
- `vitamin_targets` - User-defined nutrient goals
- `saved_images` - Uploaded food photos
- `user_profile` - User health profile and goals

## Deployment

### Backend (Render)
1. Create a new Web Service on Render
2. Connect your repository
3. Set environment variables (ANTHROPIC_API_KEY)
4. Deploy

### Frontend (Netlify)
1. Build the frontend: `npm run build`
2. Deploy the `dist` folder to Netlify
3. Set the API URL environment variable

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Acknowledgments

- Anthropic Claude API for AI features
- OpenFoodFacts for barcode data
- Chart.js for visualizations
- The Svelte community
