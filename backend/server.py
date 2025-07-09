
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
import google.generativeai as genai
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

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

# Configure Google Gemini AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
AI_ENABLED = False

if GOOGLE_API_KEY and GOOGLE_API_KEY != 'your_google_api_key_here':
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        AI_ENABLED = True
        logger.info("Google Generative AI configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Google Generative AI: {e}")
        AI_ENABLED = False
else:
    logger.warning("GOOGLE_API_KEY not found. AI features will be disabled.")

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

# AI Service Class
class AIExpenseService:
    def __init__(self):
        self.model = None
        if AI_ENABLED:
            try:
                self.model = genai.GenerativeModel('gemma-3-27b-it')
                logger.info("AI model 'gemma-3-27b-it' initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize AI model: {e}")

    def categorize_expense(self, expense_name: str, amount: float) -> str:
        """Suggest expense category using AI"""
        if not self.model:
            # Fallback rule-based categorization
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
            
        try:
            valid_categories = ["Food", "Transportation", "Bills", "Entertainment", "Housing", 
                             "Groceries", "Health", "Education", "Personal Care", "Savings", "Travel", "Other"]
            
            prompt = f"""
            Categorize this expense into one of these categories: {", ".join(valid_categories)}
            
            Expense: "{expense_name}" - ₹{amount:.2f}
            
            Respond with ONLY the category name. If unclear, respond with "Other".
            """
            
            response = self.model.generate_content(prompt)
            category = response.text.strip()
            return category if category in valid_categories else "Other"
        except Exception as e:
            logger.error(f"AI categorization error: {e}")
            return "Other"

    def get_spending_insights(self, expense_list: List[Dict]) -> List[Dict]:
        """Get AI-powered spending insights"""
        if not self.model or not expense_list:
            # Return sample insights if AI is not available
            return [
                {
                    "type": "insight",
                    "message": "Your spending patterns show consistent daily expenses. Consider setting a daily budget.",
                    "confidence": 0.7,
                    "data": {}
                },
                {
                    "type": "insight", 
                    "message": "Food expenses are your highest category. Look for meal prep opportunities to save money.",
                    "confidence": 0.8,
                    "data": {"category": "Food"}
                }
            ]
            
        try:
            total_expenses = sum(exp['amount'] for exp in expense_list)
            category_breakdown = {}
            for exp in expense_list:
                cat = exp['category']
                category_breakdown[cat] = category_breakdown.get(cat, 0) + exp['amount']

            summary_data = {
                "total_expenses": total_expenses,
                "category_breakdown": category_breakdown,
                "expense_count": len(expense_list)
            }
            
            prompt = f"""
            Analyze spending data and provide 3-5 actionable insights in JSON format.
            
            Data: {json.dumps(summary_data, indent=2)}
            
            Return as JSON array: [{{"message": "insight text", "data": {{"category": "relevant_category"}}}}]
            Keep insights positive and actionable. Use ₹ for currency.
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()

            try:
                ai_raw_insights = json.loads(response_text)
                insights = []
                if isinstance(ai_raw_insights, list):
                    for item in ai_raw_insights:
                        if isinstance(item, dict) and "message" in item:
                            insights.append({
                                "type": "insight",
                                "message": item["message"],
                                "confidence": 0.85,
                                "data": item.get("data", {})
                            })
                return insights if insights else self.get_spending_insights([])  # Fallback
            except json.JSONDecodeError:
                return self.get_spending_insights([])  # Fallback
        except Exception as e:
            logger.error(f"AI insights error: {e}")
            return self.get_spending_insights([])  # Fallback

    def predict_next_month_expenses(self, expense_list: List[Dict]) -> Dict:
        """Predict next month's expenses"""
        if not self.model or not expense_list:
            # Calculate simple prediction based on recent data
            recent_total = sum(exp['amount'] for exp in expense_list[-30:] if len(expense_list) > 30 else expense_list)
            predicted_total = recent_total * 1.1  # Simple 10% increase prediction
            
            return {
                "type": "prediction",
                "message": f"Based on recent spending, predicted next month: ₹{predicted_total:.2f}",
                "confidence": 0.6,
                "data": {"predicted_total": predicted_total}
            }
            
        try:
            # Filter recent expenses (last 60 days)
            current_date = datetime.now()
            recent_expenses = []
            for exp in expense_list:
                try:
                    exp_date = datetime.strptime(exp['date'], '%Y-%m-%d')
                    if exp_date >= current_date - timedelta(days=60):
                        recent_expenses.append(exp)
                except ValueError:
                    continue

            if not recent_expenses:
                return self.predict_next_month_expenses([])  # Fallback

            total_recent = sum(exp['amount'] for exp in recent_expenses)
            
            prompt = f"""
            Analyze recent expense data and predict next month's total expenses.
            
            Recent expenses (last 60 days): ₹{total_recent:.2f}
            Number of transactions: {len(recent_expenses)}
            
            Provide prediction in JSON format:
            {{"predicted_total": float, "insights": ["insight1", "insight2"]}}
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()

            try:
                ai_data = json.loads(response_text)
                predicted_total = ai_data.get('predicted_total', total_recent * 1.1)
                return {
                    "type": "prediction",
                    "message": f"AI predicts next month expenses: ₹{predicted_total:.2f}",
                    "confidence": 0.85,
                    "data": ai_data
                }
            except json.JSONDecodeError:
                return self.predict_next_month_expenses([])  # Fallback
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return self.predict_next_month_expenses([])  # Fallback

# Initialize AI service
ai_service = AIExpenseService()

# Load sample data
load_sample_data()

# API Routes
@app.route('/api', methods=['GET'])
@app.route('/api/', methods=['GET'])
def root():
    return jsonify({
        "message": "Smart Expense Tracker API v2.0",
        "status": "healthy",
        "ai_enabled": AI_ENABLED,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "ai_service": "available" if ai_service.model else "disabled",
        "api_key_configured": bool(GOOGLE_API_KEY and GOOGLE_API_KEY != 'your_google_api_key_here'),
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
        
        # Validate required fields
        required_fields = ['name', 'amount', 'date', 'category']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"success": False, "error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Validate data types
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({"success": False, "error": "Amount must be positive"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid amount"}), 400

        # Validate date format
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}), 400

        expense = {
            'id': str(uuid.uuid4()),
            'name': data['name'].strip(),
            'amount': amount,
            'date': data['date'],
            'category': data['category'],
            'description': data.get('description', '').strip(),
            'created_at': datetime.now().isoformat()
        }
        
        expenses.insert(0, expense)  # Add to beginning
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

@app.route('/api/expenses/categorize', methods=['GET'])
def categorize_expense():
    try:
        expense_name = request.args.get('expense_name', '').strip()
        amount_str = request.args.get('amount', '0')
        
        if not expense_name:
            return jsonify({"success": False, "error": "Expense name is required"}), 400
            
        try:
            amount = float(amount_str)
            if amount <= 0:
                return jsonify({"success": False, "error": "Amount must be positive"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid amount"}), 400
        
        category = ai_service.categorize_expense(expense_name, amount)
        return jsonify({"success": True, "suggested_category": category})
    except Exception as e:
        logger.error(f"Error categorizing expense: {e}")
        return jsonify({"success": True, "suggested_category": "Other"})

@app.route('/api/expenses/insights', methods=['POST'])
def get_insights():
    try:
        data = request.get_json() or {}
        expense_list = data.get('expenses', expenses)  # Use provided expenses or default
        insights = ai_service.get_spending_insights(expense_list)
        return jsonify({"success": True, "data": insights})
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return jsonify({"success": True, "data": []})

@app.route('/api/expenses/predict', methods=['POST'])
def predict_expenses():
    try:
        data = request.get_json() or {}
        expense_list = data.get('expenses', expenses)
        prediction = ai_service.predict_next_month_expenses(expense_list)
        return jsonify({"success": True, "data": prediction})
    except Exception as e:
        logger.error(f"Error predicting expenses: {e}")
        return jsonify({
            "success": True,
            "data": {
                "type": "prediction",
                "message": "Unable to generate prediction",
                "confidence": 0.0,
                "data": {}
            }
        })

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
        # Calculate basic analytics
        total_expenses = sum(exp['amount'] for exp in expenses)
        
        # Category breakdown
        category_totals = {}
        for exp in expenses:
            cat = exp['category']
            category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
        
        # Monthly trend (last 6 months)
        monthly_data = {}
        for exp in expenses:
            month = exp['date'][:7]  # YYYY-MM
            monthly_data[month] = monthly_data.get(month, 0) + exp['amount']
        
        # Sort by month and take last 6
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
            # Calculate spent amount for current month
            spent = sum(
                exp['amount'] for exp in expenses 
                if exp['category'] == budget['category'] and exp['date'].startswith(current_month)
            )
            
            percentage = (spent / budget['amount']) * 100 if budget['amount'] > 0 else 0
            
            if percentage >= 70:  # Alert threshold
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
    port = int(os.environ.get('PORT', 8001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
