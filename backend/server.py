
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
load_dotenv(ROOT_DIR / '.env')

# Configure Google Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        logger.info("Google Generative AI configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Google Generative AI: {e}")
else:
    logger.warning("GOOGLE_API_KEY not found in environment variables.")

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["*"])  # Configure CORS for all origins

# In-memory storage (in production, use a proper database)
expenses = []
budgets = []

# AI Service Class
class AIExpenseService:
    def __init__(self):
        self.model = None
        if GOOGLE_API_KEY:
            try:
                self.model = genai.GenerativeModel('gemma-3-27b-it')
                logger.info("AI model 'gemma-3-27b-it' initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize AI model: {e}")

    def predict_next_month_expenses(self, expense_list: List[Dict]) -> Dict:
        """Predict next month's expenses using AI"""
        if not self.model:
            return {
                "type": "prediction",
                "message": "AI service not available.",
                "confidence": 0.0,
                "data": {}
            }
        
        try:
            # Filter recent expenses (last 90 days)
            current_date = datetime.now()
            recent_expenses = []
            for exp in expense_list:
                try:
                    exp_date = datetime.strptime(exp['date'], '%Y-%m-%d')
                    if exp_date >= current_date - timedelta(days=90):
                        recent_expenses.append(exp)
                except ValueError:
                    continue

            if not recent_expenses:
                return {
                    "type": "prediction",
                    "message": "Not enough recent expense data for accurate prediction.",
                    "confidence": 0.1,
                    "data": {}
                }

            expense_data_str = json.dumps(recent_expenses, indent=2)
            prompt = f"""
            You are an expert financial analyst. Analyze the provided recent expense data (up to last 90 days) to predict next month's spending patterns.
            The currency for all amounts is Indian Rupees (₹).
            Based on this data, provide the following in STRICT JSON format only:

            Recent Expense Data:
            {expense_data_str}

            {{
              "predicted_total": float,
              "category_breakdown": {{"Food": float,"Transportation": float,"Bills": float,"Entertainment": float,"Housing": float,"Groceries": float,"Health": float,"Education": float,"Personal Care": float,"Savings": float,"Travel": float,"Other": float}},
              "insights": ["string"],
              "recommendations": ["string"]
            }}
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean JSON response
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()

            try:
                ai_data = json.loads(response_text)
                predicted_total = ai_data.get('predicted_total', 0.0)
                message = f"Based on your spending patterns, predicted next month expenses: ₹{predicted_total:.2f}"
                return {
                    "type": "prediction",
                    "message": message,
                    "confidence": 0.9,
                    "data": ai_data
                }
            except json.JSONDecodeError as e:
                logger.warning(f"AI prediction response was not valid JSON: {response_text}. Error: {e}")
                return {
                    "type": "prediction",
                    "message": "AI prediction parsing failed.",
                    "confidence": 0.5,
                    "data": {}
                }
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return {
                "type": "prediction",
                "message": "Unable to generate prediction at this time.",
                "confidence": 0.0,
                "data": {"error": str(e)}
            }

    def categorize_expense(self, expense_name: str, amount: float) -> str:
        """Suggest expense category using AI"""
        if not self.model:
            return "Other"
            
        try:
            valid_categories = ["Food", "Transportation", "Bills", "Entertainment", "Housing", 
                             "Groceries", "Health", "Education", "Personal Care", "Savings", "Travel", "Other"]
            
            prompt = f"""
            You are an AI assistant specialized in categorizing personal expenses. 
            Categorize this expense into one of these categories: {", ".join(valid_categories)}
            
            Expense Details:
            - Item: "{expense_name}"
            - Amount: ₹{amount:.2f}
            
            Respond with ONLY the category name. If no clear match exists, respond with "Other".
            """
            
            response = self.model.generate_content(prompt)
            category = response.text.strip()
            return category if category in valid_categories else "Other"
        except Exception as e:
            logger.error(f"AI categorization error for '{expense_name}': {e}")
            return "Other"

    def get_spending_insights(self, expense_list: List[Dict]) -> List[Dict]:
        """Get AI-powered spending insights"""
        if not self.model or not expense_list:
            return []
            
        try:
            total_expenses = sum(exp['amount'] for exp in expense_list)
            category_breakdown = {}
            for exp in expense_list:
                cat = exp['category']
                category_breakdown[cat] = category_breakdown.get(cat, 0) + exp['amount']

            summary_data = {
                "total_expenses": total_expenses,
                "category_breakdown": category_breakdown
            }
            
            prompt = f"""
            You are a helpful financial assistant. Analyze the following expense data and provide 3-5 concise, actionable insights.
            The currency is Indian Rupees (₹). Keep insights positive and actionable.

            Expense Summary:
            {json.dumps(summary_data, indent=2)}

            Respond as a STRICT JSON array of insight objects. Each object must have a 'message' (string) and optional 'data' (object) field.
            Example: [{{"message": "Your Food expenses are consistently high.", "data": {{"category": "Food"}}}}]
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()

            try:
                ai_raw_insights = json.loads(response_text)
                ai_insights = []
                if isinstance(ai_raw_insights, list):
                    for item in ai_raw_insights:
                        if isinstance(item, dict) and "message" in item:
                            clean_message = item["message"].replace("$", "₹")
                            ai_insights.append({
                                "type": "insight",
                                "message": clean_message,
                                "confidence": 0.8,
                                "data": item.get("data", {})
                            })
                return ai_insights
            except json.JSONDecodeError as e:
                logger.warning(f"AI insights response was not valid JSON: {response_text}. Error: {e}")
                return [{
                    "type": "insight",
                    "message": "Failed to process detailed AI insights.",
                    "confidence": 0.3,
                    "data": {"error": str(e)}
                }]
        except Exception as e:
            logger.error(f"AI insights generation error: {e}")
            return [{
                "type": "insight",
                "message": "Unable to generate AI insights due to an unexpected error.",
                "confidence": 0.0,
                "data": {"error": str(e)}
            }]

# Initialize AI service
ai_service = AIExpenseService()

# API Routes
@app.route('/api', methods=['GET'])
def root():
    return jsonify({"message": "Smart Expense Tracker API is running!", "status": "healthy"})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "ai_service_status": "available" if ai_service.model else "unavailable",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    return jsonify(expenses)

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'amount', 'date', 'category']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        expense = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'amount': float(data['amount']),
            'date': data['date'],
            'category': data['category'],
            'description': data.get('description', '')
        }
        
        expenses.insert(0, expense)  # Add to beginning for recent expenses
        return jsonify(expense), 201
    except Exception as e:
        logger.error(f"Error adding expense: {e}")
        return jsonify({"error": "Failed to add expense"}), 500

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        global expenses
        expenses = [exp for exp in expenses if exp['id'] != expense_id]
        return jsonify({"message": "Expense deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting expense: {e}")
        return jsonify({"error": "Failed to delete expense"}), 500

@app.route('/api/expenses/categorize', methods=['GET'])
def categorize_expense():
    try:
        expense_name = request.args.get('expense_name', '')
        amount = float(request.args.get('amount', 0))
        
        if not expense_name or amount <= 0:
            return jsonify({"error": "Invalid expense name or amount"}), 400
        
        category = ai_service.categorize_expense(expense_name, amount)
        return jsonify({"suggested_category": category})
    except Exception as e:
        logger.error(f"Error categorizing expense: {e}")
        return jsonify({"suggested_category": "Other"})

@app.route('/api/expenses/insights', methods=['POST'])
def get_insights():
    try:
        data = request.get_json()
        expense_list = data.get('expenses', [])
        insights = ai_service.get_spending_insights(expense_list)
        return jsonify(insights)
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        return jsonify([])

@app.route('/api/expenses/predict', methods=['POST'])
def predict_expenses():
    try:
        data = request.get_json()
        expense_list = data.get('expenses', [])
        prediction = ai_service.predict_next_month_expenses(expense_list)
        return jsonify(prediction)
    except Exception as e:
        logger.error(f"Error predicting expenses: {e}")
        return jsonify({
            "type": "prediction",
            "message": "Unable to generate prediction at this time.",
            "confidence": 0.0,
            "data": {}
        })

@app.route('/api/budgets', methods=['GET'])
def get_budgets():
    return jsonify(budgets)

@app.route('/api/budgets', methods=['POST'])
def add_budget():
    try:
        data = request.get_json()
        
        required_fields = ['category', 'amount']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        budget = {
            'id': str(uuid.uuid4()),
            'category': data['category'],
            'amount': float(data['amount']),
            'period': data.get('period', 'monthly')
        }
        
        budgets.append(budget)
        return jsonify(budget), 201
    except Exception as e:
        logger.error(f"Error adding budget: {e}")
        return jsonify({"error": "Failed to add budget"}), 500

@app.route('/api/budget/alerts', methods=['POST'])
def get_budget_alerts():
    try:
        data = request.get_json()
        expense_list = data.get('expenses', [])
        budget_list = data.get('budgets', [])
        
        alerts = []
        current_month = datetime.now().strftime('%Y-%m')
        
        for budget in budget_list:
            # Calculate spent amount for current month
            spent = sum(
                exp['amount'] for exp in expense_list 
                if exp['category'] == budget['category'] and exp['date'].startswith(current_month)
            )
            
            percentage = (spent / budget['amount']) * 100 if budget['amount'] > 0 else 0.0
            
            if percentage >= 75:  # Alert threshold
                alert_type = "warning"
                if percentage >= 90:
                    alert_type = "danger"
                    
                alerts.append({
                    "category": budget['category'],
                    "budget_amount": budget['amount'],
                    "spent_amount": spent,
                    "percentage_used": percentage,
                    "alert_type": alert_type
                })
        
        return jsonify(alerts)
    except Exception as e:
        logger.error(f"Error getting budget alerts: {e}")
        return jsonify([])

@app.route('/api/expenses/analytics', methods=['POST'])
def get_analytics():
    try:
        data = request.get_json()
        expense_list = data.get('expenses', [])
        
        if not expense_list:
            return jsonify({
                "total_expenses": 0.0,
                "category_breakdown": {},
                "monthly_trend": []
            })
        
        # Calculate total expenses
        total_expenses = sum(exp['amount'] for exp in expense_list)
        
        # Calculate category breakdown
        category_breakdown = {}
        for exp in expense_list:
            cat = exp['category']
            category_breakdown[cat] = category_breakdown.get(cat, 0.0) + exp['amount']
        
        # Calculate monthly trend (last 6 months)
        monthly_trend = []
        today = datetime.now()
        
        for i in range(6):
            target_year, target_month = today.year, today.month - i
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            month_str = f"{target_year:04d}-{target_month:02d}"
            month_expenses = [exp for exp in expense_list if exp['date'].startswith(month_str)]
            
            monthly_trend.append({
                "month": month_str,
                "total": sum(exp['amount'] for exp in month_expenses),
                "count": len(month_expenses)
            })
        
        monthly_trend.sort(key=lambda x: x['month'])
        
        return jsonify({
            "total_expenses": total_expenses,
            "category_breakdown": category_breakdown,
            "monthly_trend": monthly_trend
        })
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({
            "total_expenses": 0.0,
            "category_breakdown": {},
            "monthly_trend": []
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
