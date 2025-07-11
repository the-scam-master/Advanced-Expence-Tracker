from flask import Flask, jsonify
from flask_cors import CORS
import logging
from datetime import datetime

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/api', methods=['GET'])
@app.route('/api/', methods=['GET'])
def root():
    return jsonify({
        "message": "Smart Expense Tracker API v2.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=8001)
