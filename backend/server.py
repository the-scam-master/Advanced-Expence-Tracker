from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import uuid
from datetime import datetime, timedelta
from collections import defaultdict # Import defaultdict for easier aggregation

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
ROOT_DIR = Path(__file__).parent
env_file = ROOT_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["*"])

# --- Data Storage (Removed for Backend) ---
# The frontend now manages its own data in localStorage.
# The backend will generate analytics based on its *own* static or sample data
# or potentially aggregate data if it were connected to a persistent store,
# but for this setup, it's primarily for providing analytical *structures*.

# Sample data for demo (kept for generating analytics if needed without frontend data)
# In a real scenario, this would come from a database.
# For this version, it's less critical as frontend data isn't sent to backend.
# However, if backend HAD to generate insights without frontend data, it would need data.
# Given the current structure, backend data isn't directly used by the frontend's local state logic.
# We'll keep minimal sample data for the analytics endpoint to function.

expenses_sample = [
    {'id': str(uuid.uuid4()), 'name': 'Morning Coffee', 'amount': 120.0, 'date': '2025-01-09', 'category': 'Food', 'description': 'Daily coffee from cafe'},
    {'id': str(uuid.uuid4()), 'name': 'Uber Ride', 'amount': 280.0, 'date': '2025-01-09', 'category': 'Transportation', 'description': 'Ride to office'},
    {'id': str(uuid.uuid4()), 'name': 'Lunch', 'amount': 450.0, 'date': '2025-01-08', 'category': 'Food', 'description': 'Office lunch'},
    {'id': str(uuid.uuid4()), 'name': 'Groceries', 'amount': 1200.0, 'date': '2025-01-07', 'category': 'Groceries', 'description': 'Weekly shopping'}
]
budgets_sample = [
    {'id': str(uuid.uuid4()), 'category': 'Food', 'amount': 5000.0, 'period': 'monthly'},
    {'id': str(uuid.uuid4()), 'category': 'Transportation', 'amount': 3000.0, 'period': 'monthly'}
]

# --- Helper Functions for Analytics Generation ---

def categorize_expense_backend(expense_name: str) -> str:
    # This function is not directly called by the corrected frontend logic,
    # but is kept for potential backend-driven analytics or if you decide to
    # send expense data to the backend for analysis later.
    name_lower = expense_name.lower()
    if any(word in name_lower for word in ['coffee', 'tea', 'lunch', 'dinner', 'food', 'restaurant', 'cafe']): return "Food"
    elif any(word in name_lower for word in ['uber', 'taxi', 'bus', 'metro', 'transport', 'fuel', 'petrol']): return "Transportation"
    elif any(word in name_lower for word in ['grocery', 'supermarket', 'store', 'mart']): return "Groceries"
    elif any(word in name_lower for word in ['movie', 'game', 'entertainment', 'netflix']): return "Entertainment"
    elif any(word in name_lower for word in ['rent', 'electricity', 'water', 'gas', 'internet']): return "Bills"
    else: return "Other"

# --- API Routes ---

@app.route('/api', methods=['GET'])
@app.route('/api/', methods=['GET'])
def root():
    # Basic API health check
    return jsonify({
        "message": "Smart Expense Tracker API v2.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    # Provides a simple health check with data counts (though backend data is not primary)
    # This might still be useful for monitoring the backend's status.
    return jsonify({
        "status": "healthy",
        "data_count": {"sample_expenses": len(expenses_sample), "sample_budgets": len(budgets_sample)},
        "timestamp": datetime.now().isoformat()
    })

# --- Analytics Endpoint for Insights Tab ---
# This is the main endpoint the frontend's Insights tab will call.
# It generates analytics based on *its own sample data* since it doesn't receive data from the frontend.
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    logger.info("Fetching analytics data for Insights tab.")
    try:
        # The analytics are generated based on the backend's sample data.
        # If you want insights based on frontend data, the frontend would need
        # to send that data to a new backend endpoint.

        # For this setup, we'll use the sample data to provide structure.
        # In a real app using this pattern, the frontend might send its localStorage data to a backend endpoint for analysis.
        
        # Simulate processing of sample data for analytics
        total_expenses_sample = sum(exp['amount'] for exp in expenses_sample)
        
        category_totals_sample = defaultdict(float)
        for exp in expenses_sample:
            category_totals_sample[exp['category']] += exp['amount']
        
        # Monthly trend (simplified, using sample data dates)
        monthly_data_sample = defaultdict(float)
        for exp in expenses_sample:
            try:
                # Extract year-month from date string
                month_year_str = exp['date'][:7] 
                monthly_data_sample[month_year_str] += exp['amount']
            except (ValueError, IndexError):
                logger.warning(f"Could not parse date for analytics: {exp.get('date')}")
                continue # Skip if date is malformed
        
        # Get last 6 months from sample data trend, sorted
        sorted_months_sample = sorted(monthly_data_sample.items())[-6:]
        
        # Dummy budget alerts based on sample data
        alerts_sample = []
        current_month_backend = datetime.now().strftime('%Y-%m') # Backend's current month
        for budget in budgets_sample:
            spent_sample = sum(
                exp['amount'] for exp in expenses_sample 
                if exp['category'] == budget['category'] and exp['date'].startswith(current_month_backend)
            )
            
            percentage = (spent_sample / budget['amount']) * 100 if budget['amount'] > 0 else 0
            
            if percentage >= 70:
                alert_type = "warning" if percentage < 90 else "danger"
                alerts_sample.append({
                    "category": budget['category'],
                    "budget_amount": budget['amount'],
                    "spent_amount": spent_sample,
                    "percentage_used": percentage,
                    "alert_type": alert_type
                })

        # Construct the analytics response structure expected by the frontend
        # Note: The frontend's 'insights' logic will interpret this data.
        analytics_data = {
            "total_expenses": total_expenses_sample,
            "expense_count": len(expenses_sample),
            "category_breakdown": dict(category_totals_sample), # Convert defaultdict to dict
            "monthly_trend": [{"month": month, "amount": amount} for month, amount in sorted_months_sample],
            # The frontend's dummy health/prediction logic will need to map to this data
            "health_score": {"score": 75, "grade": "Good", "message": "Based on sample data trends.", "factors": ["Sample data analysis"]}, # Dummy score
            "insights": [{"message": "Sample insight: Food spending detected."}] if any(b['category'] == 'Food' for b in budgets_sample) else [], # Dummy insight
            "prediction": {"message": "Prediction based on sample data trends."}, # Dummy prediction
            "savings_advice": [], # Dummy savings advice
            "budget_alerts": alerts_sample
        }
        
        return jsonify({"success": True, "data": analytics_data})
        
    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        return jsonify({"success": False, "error": "Failed to generate analytics"}), 500

# --- Removed Endpoints ---
# Any endpoints related to adding/deleting/fetching transactions and budgets have been removed
# as the frontend now handles this exclusively via localStorage.
# For example, /api/expenses (POST/DELETE) and /api/budgets (POST) are gone.

if __name__ == '__main__':
    # This is for local development. Vercel handles the runtime.
    # For testing locally, you might run this script directly.
    # For example: python server.py
    # Make sure to set FLASK_ENV=development or similar if needed for debugging.
    app.run(debug=True, port=8001) # Running on a different port to avoid conflict if frontend is also on 8000
