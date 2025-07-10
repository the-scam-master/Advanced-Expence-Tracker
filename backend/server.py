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
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your_google_api_key_here')

# Check API key (don't fail if missing)
if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'your_google_api_key_here':
    logger.warning("GOOGLE_API_KEY not found or invalid in environment. AI features will be disabled.")
    GOOGLE_API_KEY = None

# Configure Google Gemini AI
AI_ENABLED = False
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    AI_ENABLED = True
    logger.info("Google Generative AI configured successfully.")
except Exception as e:
    logger.error(f"Failed to configure Google Generative AI: {e}")
    # Don't raise here, let the app start without AI

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
                # Try different models in order of preference
                model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                available_models = [m.name for m in genai.list_models()]
                logger.info(f"Available models: {available_models}")
                
                for model_name in model_names:
                    if model_name in available_models:
                        self.model = genai.GenerativeModel(model_name)
                        logger.info(f"AI model initialized: {self.model.name}")
                        break
                
                if not self.model:
                    logger.warning("No suitable AI model found, falling back to rule-based categorization")
                    
            except Exception as e:
                logger.error(f"Failed to initialize AI model: {e}")
                self.model = None

    def categorize_expense(self, expense_name: str, amount: float) -> str:
        """Suggest expense category using AI"""
        if not self.model:
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
        if not expense_list:
            return [
                {
                    "type": "insight",
                    "message": "Start tracking your expenses to get personalized insights.",
                    "confidence": 0.7,
                    "data": {}
                }
            ]
            
        if not self.model:
            # Rule-based insights when AI is not available
            total_expenses = sum(exp['amount'] for exp in expense_list)
            category_breakdown = {}
            for exp in expense_list:
                cat = exp['category']
                category_breakdown[cat] = category_breakdown.get(cat, 0) + exp['amount']
            
            insights = []
            if total_expenses > 0:
                max_category = max(category_breakdown.items(), key=lambda x: x[1])
                insights.append({
                    "type": "insight",
                    "message": f"Your highest spending category is {max_category[0]} (₹{max_category[1]:.0f}). Consider setting a budget for this category.",
                    "confidence": 0.8,
                    "data": {"category": max_category[0]}
                })
                
                if len(expense_list) > 10:
                    insights.append({
                        "type": "insight",
                        "message": "You have many transactions. Consider consolidating small purchases to better track your spending.",
                        "confidence": 0.7,
                        "data": {}
                    })
                
                if total_expenses > 5000:
                    insights.append({
                        "type": "insight",
                        "message": "Your total expenses are ₹{:.0f}. Review your spending to identify areas for savings.",
                        "confidence": 0.6,
                        "data": {}
                    })
            
            return insights if insights else [
                {
                    "type": "insight",
                    "message": "Your spending patterns show consistent daily expenses. Consider setting a daily budget.",
                    "confidence": 0.7,
                    "data": {}
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

    def calculate_financial_health_score(self, expense_list: List[Dict], income_list: List[Dict] = None) -> Dict:
        """Calculate financial health score based on spending patterns"""
        if not expense_list:
            return {
                "score": 75,
                "grade": "B",
                "message": "No spending data available. Start tracking to get personalized insights.",
                "factors": ["No data available"],
                "recommendations": ["Begin tracking your expenses", "Set up a budget", "Monitor your spending patterns"]
            }
        
        try:
            total_expenses = sum(exp['amount'] for exp in expense_list)
            total_income = sum(inc['amount'] for inc in income_list) if income_list else total_expenses * 1.2  # Estimate
            
            savings_rate = max(0, (total_income - total_expenses) / total_income) if total_income > 0 else 0
            expense_diversity = len(set(exp['category'] for exp in expense_list))
            avg_daily_spending = total_expenses / max(len(set(exp['date'] for exp in expense_list)), 1)
            
            score = 0
            if savings_rate >= 0.3:
                score += 40
            elif savings_rate >= 0.2:
                score += 30
            elif savings_rate >= 0.1:
                score += 20
            elif savings_rate >= 0:
                score += 10
            
            if expense_diversity >= 8:
                score += 20
            elif expense_diversity >= 5:
                score += 15
            elif expense_diversity >= 3:
                score += 10
            else:
                score += 5
            
            if avg_daily_spending <= 500:
                score += 20
            elif avg_daily_spending <= 1000:
                score += 15
            elif avg_daily_spending <= 2000:
                score += 10
            else:
                score += 5
            
            category_totals = {}
            for exp in expense_list:
                cat = exp['category']
                category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
            
            max_category_percentage = max(category_totals.values()) / total_expenses if total_expenses > 0 else 0
            if max_category_percentage <= 0.3:
                score += 20
            elif max_category_percentage <= 0.5:
                score += 15
            elif max_category_percentage <= 0.7:
                score += 10
            else:
                score += 5
            
            if score >= 90:
                grade = "A+"
                message = "Excellent financial health! You're managing your money very well."
            elif score >= 80:
                grade = "A"
                message = "Great financial health! Keep up the good work."
            elif score >= 70:
                grade = "B+"
                message = "Good financial health with room for improvement."
            elif score >= 60:
                grade = "B"
                message = "Fair financial health. Consider the recommendations below."
            elif score >= 50:
                grade = "C"
                message = "Your financial health needs attention. Focus on the areas below."
            else:
                grade = "D"
                message = "Your financial health requires immediate attention."
            
            factors = []
            recommendations = []
            if savings_rate < 0.2:
                factors.append("Low savings rate")
                recommendations.append("Increase your savings by 20% of income")
            if expense_diversity < 5:
                factors.append("Limited expense categories")
                recommendations.append("Diversify your spending across more categories")
            if avg_daily_spending > 1000:
                factors.append("High daily spending")
                recommendations.append("Reduce daily expenses and look for cost-cutting opportunities")
            if max_category_percentage > 0.5:
                factors.append("Over-concentration in one category")
                recommendations.append(f"Reduce spending in {max(category_totals, key=category_totals.get)} category")
            
            return {
                "score": score,
                "grade": grade,
                "message": message,
                "factors": factors,
                "recommendations": recommendations,
                "metrics": {
                    "savings_rate": round(savings_rate * 100, 1),
                    "expense_diversity": expense_diversity,
                    "avg_daily_spending": round(avg_daily_spending, 2),
                    "max_category_percentage": round(max_category_percentage * 100, 1)
                }
            }
        except Exception as e:
            logger.error(f"Financial health score calculation error: {e}")
            return {
                "score": 50,
                "grade": "C",
                "message": "Unable to calculate financial health score.",
                "factors": ["Calculation error"],
                "recommendations": ["Contact support if this persists"]
            }

    def get_savings_advice(self, expense_list: List[Dict], income_list: List[Dict] = None) -> List[Dict]:
        """Get AI-powered savings advice"""
        if not expense_list:
            return [
                {
                    "type": "advice",
                    "title": "Start Tracking",
                    "message": "Begin by tracking all your expenses to understand your spending patterns.",
                    "priority": "high",
                    "potential_savings": 0
                }
            ]
        
        if not self.model:
            # Rule-based advice when AI is not available
            total_expenses = sum(exp['amount'] for exp in expense_list)
            category_totals = {}
            for exp in expense_list:
                cat = exp['category']
                category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
            
            advice_list = []
            
            # Analyze highest spending categories
            if category_totals:
                sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
                top_category = sorted_categories[0]
                
                if top_category[1] > total_expenses * 0.3:
                    advice_list.append({
                        "type": "advice",
                        "title": f"Reduce {top_category[0]} Spending",
                        "message": f"You're spending ₹{top_category[1]:.0f} on {top_category[0]}. Consider setting a budget and looking for cost-cutting opportunities.",
                        "priority": "high",
                        "potential_savings": top_category[1] * 0.2
                    })
                
                if len(expense_list) > 20:
                    avg_expense = total_expenses / len(expense_list)
                    if avg_expense > 500:
                        advice_list.append({
                            "type": "advice",
                            "title": "Review Small Expenses",
                            "message": f"Average expense is ₹{avg_expense:.0f}. Small daily expenses add up quickly. Track every rupee spent.",
                            "priority": "medium",
                            "potential_savings": total_expenses * 0.1
                        })
                
                if not any(exp['category'] == 'Savings' for exp in expense_list):
                    advice_list.append({
                        "type": "advice",
                        "title": "Build Emergency Fund",
                        "message": "Start saving 10% of your income for emergencies. Aim for 3-6 months of expenses.",
                        "priority": "high",
                        "potential_savings": total_expenses * 0.1
                    })
            
            return advice_list[:3] if advice_list else [
                {
                    "type": "advice",
                    "title": "General Savings Tips",
                    "message": "Track all expenses, set budgets, and look for ways to reduce spending in your highest categories.",
                    "priority": "medium",
                    "potential_savings": 0
                }
            ]
        
        try:
            total_expenses = sum(exp['amount'] for exp in expense_list)
            category_totals = {}
            for exp in expense_list:
                cat = exp['category']
                category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
            
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            advice_list = []
            
            if 'Food' in category_totals and category_totals['Food'] > total_expenses * 0.3:
                advice_list.append({
                    "type": "advice",
                    "title": "Optimize Food Spending",
                    "message": f"You're spending ₹{category_totals['Food']:.0f} on food. Consider meal prepping, cooking at home, and using grocery lists to save 20-30%.",
                    "priority": "high",
                    "potential_savings": category_totals['Food'] * 0.25
                })
            
            if 'Transportation' in category_totals and category_totals['Transportation'] > total_expenses * 0.2:
                advice_list.append({
                    "type": "advice",
                    "title": "Reduce Transportation Costs",
                    "message": f"Transportation costs are ₹{category_totals['Transportation']:.0f}. Consider public transport, carpooling, or walking for short distances.",
                    "priority": "medium",
                    "potential_savings": category_totals['Transportation'] * 0.15
                })
            
            if 'Entertainment' in category_totals and category_totals['Entertainment'] > total_expenses * 0.15:
                advice_list.append({
                    "type": "advice",
                    "title": "Smart Entertainment Choices",
                    "message": f"Entertainment spending is ₹{category_totals['Entertainment']:.0f}. Look for free events, use student discounts, and limit premium subscriptions.",
                    "priority": "medium",
                    "potential_savings": category_totals['Entertainment'] * 0.20
                })
            
            if len(expense_list) > 20:
                avg_expense = total_expenses / len(expense_list)
                if avg_expense > 500:
                    advice_list.append({
                        "type": "advice",
                        "title": "Review Small Expenses",
                        "message": f"Average expense is ₹{avg_expense:.0f}. Small daily expenses add up quickly. Track every rupee spent.",
                        "priority": "medium",
                        "potential_savings": total_expenses * 0.10
                    })
            
            if not any(exp['category'] == 'Savings' for exp in expense_list):
                advice_list.append({
                    "type": "advice",
                    "title": "Build Emergency Fund",
                    "message": "Start saving 10% of your income for emergencies. Aim for 3-6 months of expenses.",
                    "priority": "high",
                    "potential_savings": total_expenses * 0.10
                })
            
            advice_list.sort(key=lambda x: x['potential_savings'], reverse=True)
            return advice_list[:5]
        except Exception as e:
            logger.error(f"Savings advice error: {e}")
            return [
                {
                    "type": "advice",
                    "title": "General Savings Tips",
                    "message": "Track all expenses, set budgets, and look for ways to reduce spending in your highest categories.",
                    "priority": "medium",
                    "potential_savings": 0
                }
            ]

    def predict_next_month_expenses(self, expense_list: List[Dict]) -> Dict:
        """Predict next month's expenses"""
        if not expense_list:
            return {
                "type": "prediction",
                "message": "No expense data available for prediction. Start tracking expenses to get predictions.",
                "confidence": 0.0,
                "data": {"predicted_total": 0}
            }
            
        if not self.model:
            # Rule-based prediction when AI is not available
            recent_expenses = expense_list[-30:] if len(expense_list) > 30 else expense_list
            recent_total = sum(exp['amount'] for exp in recent_expenses)
            
            # Simple prediction based on recent average
            if len(recent_expenses) > 0:
                avg_daily = recent_total / len(recent_expenses)
                predicted_total = avg_daily * 30  # Assume 30 days
                
                # Add some variation based on spending patterns
                if recent_total > 10000:
                    predicted_total *= 1.1  # High spender trend
                elif recent_total < 3000:
                    predicted_total *= 0.9  # Low spender trend
                    
                return {
                    "type": "prediction",
                    "message": f"Based on recent spending patterns, predicted next month: ₹{predicted_total:.0f}",
                    "confidence": 0.6,
                    "data": {
                        "predicted_total": predicted_total,
                        "insights": [
                            "Prediction based on recent 30-day average",
                            "Consider seasonal factors that may affect spending"
                        ]
                    }
                }
            else:
                return {
                    "type": "prediction",
                    "message": "Insufficient data for prediction. Continue tracking expenses.",
                    "confidence": 0.0,
                    "data": {"predicted_total": 0}
                }
            
        try:
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
                return self.predict_next_month_expenses([])

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
                return self.predict_next_month_expenses([])
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return self.predict_next_month_expenses([])

# Initialize AI service
ai_service = AIExpenseService()

# Load sample data
load_sample_data()

# Test AI service
if ai_service.model:
    logger.info(f"AI service initialized with model: {ai_service.model.name}")
    # Test categorization
    test_category = ai_service.categorize_expense("Coffee", 100.0)
    logger.info(f"Test categorization result: {test_category}")
else:
    logger.warning("AI service not available, using rule-based fallbacks")

# API Routes
@app.route('/api', methods=['GET'])
@app.route('/api/', methods=['GET'])
def root():
    return jsonify({
        "message": "Smart Expense Tracker API v2.0",
        "status": "healthy",
        "ai_enabled": AI_ENABLED,
        "ai_model": ai_service.model.name if ai_service.model else "None",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        available_models = [m.name for m in genai.list_models()] if AI_ENABLED else []
    except Exception as e:
        logger.warning(f"Could not list models: {e}")
        available_models = []
    
    return jsonify({
        "status": "healthy",
        "ai_service": "available" if ai_service.model else "disabled",
        "ai_model": ai_service.model.name if ai_service.model else "None",
        "api_key_configured": bool(GOOGLE_API_KEY and GOOGLE_API_KEY != 'your_google_api_key_here'),
        "data_count": {"expenses": len(expenses), "budgets": len(budgets)},
        "timestamp": datetime.now().isoformat(),
        "available_models": available_models
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint to verify API is working"""
    return jsonify({
        "message": "API is working!",
        "test_categorization": ai_service.categorize_expense("Test Coffee", 150.0),
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
        
        required_fields = ['name', 'amount', 'date', 'category']
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

        expense = {
            'id': str(uuid.uuid4()),
            'name': data['name'].strip(),
            'amount': amount,
            'date': data['date'],
            'category': data['category'],
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
        expense_list = data.get('expenses', expenses)
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

@app.route('/api/ai/health-score', methods=['POST'])
def get_financial_health_score():
    try:
        data = request.get_json() or {}
        expense_list = data.get('expenses', expenses)
        income_list = data.get('income', [])
        health_score = ai_service.calculate_financial_health_score(expense_list, income_list)
        return jsonify({"success": True, "data": health_score})
    except Exception as e:
        logger.error(f"Error calculating financial health score: {e}")
        return jsonify({
            "success": True,
            "data": {
                "score": 50,
                "grade": "C",
                "message": "Unable to calculate financial health score.",
                "factors": ["Calculation error"],
                "recommendations": ["Contact support if this persists"]
            }
        })

@app.route('/api/ai/savings-advice', methods=['POST'])
def get_savings_advice():
    try:
        data = request.get_json() or {}
        expense_list = data.get('expenses', expenses)
        income_list = data.get('income', [])
        advice = ai_service.get_savings_advice(expense_list, income_list)
        return jsonify({"success": True, "data": advice})
    except Exception as e:
        logger.error(f"Error getting savings advice: {e}")
        return jsonify({
            "success": True,
            "data": [
                {
                    "type": "advice",
                    "title": "General Savings Tips",
                    "message": "Track all expenses, set budgets, and look for ways to reduce spending.",
                    "priority": "medium",
                    "potential_savings": 0
                }
            ]
        })

@app.route('/api/ai/comprehensive-analysis', methods=['POST'])
def get_comprehensive_analysis():
    try:
        data = request.get_json() or {}
        expense_list = data.get('expenses', expenses)
        income_list = data.get('income', [])
        
        insights = ai_service.get_spending_insights(expense_list)
        prediction = ai_service.predict_next_month_expenses(expense_list)
        health_score = ai_service.calculate_financial_health_score(expense_list, income_list)
        savings_advice = ai_service.get_savings_advice(expense_list, income_list)
        
        comprehensive_data = {
            "insights": insights,
            "prediction": prediction,
            "health_score": health_score,
            "savings_advice": savings_advice,
            "summary": {
                "total_expenses": sum(exp['amount'] for exp in expense_list),
                "expense_count": len(expense_list),
                "categories_analyzed": len(set(exp['category'] for exp in expense_list))
            }
        }
        
        return jsonify({"success": True, "data": comprehensive_data})
    except Exception as e:
        logger.error(f"Error getting comprehensive analysis: {e}")
        return jsonify({
            "success": True,
            "data": {
                "insights": [],
                "prediction": {"message": "Unable to generate prediction"},
                "health_score": {"score": 50, "grade": "C", "message": "Unable to calculate"},
                "savings_advice": [],
                "summary": {"total_expenses": 0, "expense_count": 0, "categories_analyzed": 0}
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
