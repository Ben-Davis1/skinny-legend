from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from database import init_db

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure CORS
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, origins=allowed_origins)

# Import routes
from routes import daily_logs, food_entries, barcode, images, ai_analysis, chat, nutrition, user_profile, weight_logs, exercises, supplements

# Register blueprints
app.register_blueprint(daily_logs.bp)
app.register_blueprint(food_entries.bp)
app.register_blueprint(barcode.bp)
app.register_blueprint(images.bp)
app.register_blueprint(ai_analysis.bp)
app.register_blueprint(chat.bp)
app.register_blueprint(nutrition.bp)
app.register_blueprint(user_profile.bp)
app.register_blueprint(weight_logs.bp)
app.register_blueprint(exercises.bp)
app.register_blueprint(supplements.bp)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Skinny Legend API is running'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database on first run
    if not os.path.exists('skinny_legend.db'):
        print("Initializing database...")
        init_db()

    # Create uploads directory
    upload_dir = os.getenv('UPLOAD_DIR', './uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=8000)
