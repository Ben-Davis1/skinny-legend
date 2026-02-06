# Installation Troubleshooting

## If start-backend.sh fails

Run these commands manually:

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies one by one
pip install Flask Flask-CORS python-dotenv requests
pip install Pillow
pip install anthropic

# Verify installation
python3 -c "import flask, anthropic, PIL; print('✓ All OK')"

# Start the server
python3 app.py
```

## Quick Test

```bash
cd backend
source venv/bin/activate
python3 -c "from app import app; print('✓ Ready')"
```

The server should start on http://localhost:8000
