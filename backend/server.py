from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import uuid
from datetime import datetime, timedelta

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

# In-memory storage (replace with database in production)
expenses = []
budgets = []

# Sample data for demo
def load_sample_data():
    global expenses, budgets
    if not expenses:
        sample_expenses = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Morning Coffee',
                'amount': 120.0,
                'date': '2025-01-09',
                'category': 'Food',
                'description': 'Daily coffee from cafe'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Uber Ride',
                'amount': 280.0,
                'date': '2025-01-09',
                'category': 'Transportation',
                'description': 'Ride to office'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Lunch',
                'amount': 450.0,
                'date': '2025-01-08',
                'category': 'Food',
                'description': 'Office lunch'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Groceries',
                'amount': 1200.0,
                'date': '2025-01-07',
                'category': 'Groceries',
                'description': 'Weekly shopping'
            }
        ]
        expenses.extend(sample_expenses)
        
    if not budgets:
        sample_budgets = [
            {
                'id': str(uuid.uuid4()),
                'category': 'Food',
                'amount': 5000.0,
                'period': 'monthly'
            },
            {
                'id': str(uuid.uuid4()),
                'category': 'Transportation',
                'amount': 3000.0,
                'period': 'monthly'
            }
        ]
        budgets.extend(sample_budgets)

# Load sample data
load_sample_data()

# Helper function for rule-based categorization
def categorize_expense(expense_name: str) -> str:
    name_lower = expense_name.lower()
    if any(word in name_lower for word in ['coffee', 'tea', 'lunch', 'dinner', 'food', 'restaurant', 'cafe']):
        return "Food"
    elif any(word in name_lower for word in ['uber', 'taxi', 'bus', 'metro', 'transport', 'fuel', 'petrol']):
        return "Transportation"
    elif any(word in name_lower for word in ['grocery', 'supermarket', 'store', 'mart']):
        return "Groceries"
    elif any(word in name_lower for word in ['movie', 'game', 'entertainment', 'netflix']):
        return "Entertainment"
    elif any(word in name_lower for word in ['rent', 'electricity', 'water', 'gas', 'internet']):
        return "Bills"
    else:
        return "Other"

# API Routes
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
        "data_count": {"expenses": len(expenses), "budgets": len(budgets)},
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    try:
        return jsonify({"success": True, "data": expenses, "count": len(expenses)})
    except Exception as e:
        logger.error(f"Error getting expenses: {e}")
        return jsonify({"success": False, "error": "Failed to get expenses"}), 500

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'amount', 'date']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"success": False, "error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({"success": False, "error": "Amount must be positive"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid amount"}), 400

        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Use rule-based categorization if category not provided
        category = data.get('category', categorize_expense(data['name']))

        expense = {
            'id': str(uuid.uuid4()),
            'name': data['name'].strip(),
            'amount': amount,
            'date': data['date'],
            'category': category,
            'description': data.get('description', '').strip(),
            'created_at': datetime.now().isoformat()
        }
        
        expenses.insert(0, expense)
        return jsonify({"success": True, "data": expense}), 201
    except Exception as e:
        logger.error(f"Error adding expense: {e}")
        return jsonify({"success": False, "error": "Failed to add expense"}), 500

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        global expenses
        original_count = len(expenses)
        expenses = [exp for exp in expenses if exp['id'] != expense_id]
        
        if len(expenses) == original_count:
            return jsonify({"success": False, "error": "Expense not found"}), 404
            
        return jsonify({"success": True, "message": "Expense deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting expense: {e}")
        return jsonify({"success": False, "error": "Failed to delete expense"}), 500

@app.route('/api/budgets', methods=['GET'])
def get_budgets():
    try:
        return jsonify({"success": True, "data": budgets, "count": len(budgets)})
    except Exception as e:
        logger.error(f"Error getting budgets: {e}")
        return jsonify({"success": False, "error": "Failed to get budgets"}), 500

@app.route('/api/budgets', methods=['POST'])
def add_budget():
    try:
        data = request.get_json()
        
        required_fields = ['category', 'amount']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"success": False, "error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({"success": False, "error": "Budget amount must be positive"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid amount"}), 400

        budget = {
            'id': str(uuid.uuid4()),
            'category': data['category'],
            'amount': amount,
            'period': data.get('period', 'monthly'),
            'created_at': datetime.now().isoformat()
        }
        
        budgets.append(budget)
        return jsonify({"success": True, "data": budget}), 201
    except Exception as e:
        logger.error(f"Error adding budget: {e}")
        return jsonify({"success": False, "error": "Failed to add budget"}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        total_expenses = sum(exp['amount'] for exp in expenses)
        
        category_totals = {}
        for exp in expenses:
            cat = exp['category']
            category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
        
        monthly_data = {}
        for exp in expenses:
            month = exp['date'][:7]
            monthly_data[month] = monthly_data.get(month, 0) + exp['amount']
        
        sorted_months = sorted(monthly_data.items())[-6:]
        
        analytics = {
            "total_expenses": total_expenses,
            "expense_count": len(expenses),
            "category_breakdown": category_totals,
            "monthly_trend": [{"month": month, "amount": amount} for month, amount in sorted_months],
            "average_per_day": total_expenses / max(len(set(exp['date'] for exp in expenses)), 1)
        }
        
        return jsonify({"success": True, "data": analytics})
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({"success": False, "error": "Failed to get analytics"}), 500

@app.route('/api/budget/alerts', methods=['GET'])
def get_budget_alerts():
    try:
        alerts = []
        current_month = datetime.now().strftime('%Y-%m')
        
        for budget in budgets:
            spent = sum(
                exp['amount'] for exp in expenses 
                if exp['category'] == budget['category'] and exp['date'].startswith(current_month)
            )
            
            percentage = (spent / budget['amount']) * 100 if budget['amount'] > 0 else 0
            
            if percentage >= 70:
                alert_type = "warning" if percentage < 90 else "danger"
                alerts.append({
                    "category": budget['category'],
                    "budget_amount": budget['amount'],
                    "spent_amount": spent,
                    "percentage_used": percentage,
                    "alert_type": alert_type
                })
        
        return jsonify({"success": True, "data": alerts})
    except Exception as e:
        logger.error(f"Error getting budget alerts: {e}")
        return jsonify({"success": True, "data": []})

if __name__ == '__main__':
    pass  # Vercel handles runtime
