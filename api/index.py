import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import the Flask app from server.py
from server import app

# Export the app for Vercel
if __name__ == '__main__':
    app.run()