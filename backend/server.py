from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
from pathlib import Path
import google.generativeai as genai
import json
from datetime import datetime, timedelta

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure Google Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY is not set in the environment variables.")
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        logger.info("Google Generative AI configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Google Generative AI: {e}")

# Create the main app
app = FastAPI(title="Smart Expense Tracker API", version="1.0.0",
              description="Backend API for Smart Expense Tracker with AI-powered insights.")

api_router = APIRouter(prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # TODO: Restrict to your frontend domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class Expense(BaseModel):
    id: str
    name: str
    amount: float
    date: str
    category: str
    description: Optional[str] = ""

class Budget(BaseModel):
    id: str
    category: str
    amount: float
    period: str = "monthly"

class ExpenseAnalytics(BaseModel):
    total_expenses: float
    category_breakdown: Dict[str, float]
    monthly_trend: List[Dict[str, Any]]

class AIInsight(BaseModel):
    type: str
    message: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    data: Dict[str, Any]

class ExpenseListRequest(BaseModel):
    expenses: List[Expense]

class BudgetAlert(BaseModel):
    category: str
    budget_amount: float
    spent_amount: float
    percentage_used: float = Field(..., ge=0.0)
    alert_type: str

class BudgetAlertRequest(BaseModel):
    expenses: List[Expense]
    budgets: List[Budget]

# AI Service Class with Improvements
class AIExpenseService:
    def __init__(self):
        self.model = None
        if GOOGLE_API_KEY:
            # Try multiple valid model names to ensure compatibility
            model_names = ['gemma-3-27b-it']
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    logger.info(f"AI model '{model_name}' initialized.")
                    break
                except Exception as e:
                    logger.warning(f"Failed to initialize model '{model_name}': {e}")
            if not self.model:
                logger.error("No suitable AI model could be initialized.")

    def predict_next_month_expenses(self, expenses: List[Expense]) -> AIInsight:
        if not self.model:
            return AIInsight(type="prediction", message="AI service not available.", confidence=0.0, data={})
        
        try:
            # Robust date parsing with error handling
            recent_expenses = []
            for exp in expenses:
                try:
                    exp_date = datetime.strptime(exp.date, '%Y-%m-%d')
                    if exp_date >= datetime.now() - timedelta(days=90):
                        recent_expenses.append(exp)
                except ValueError:
                    logger.warning(f"Invalid date format for expense: {exp.date}")

            if not recent_expenses:
                return AIInsight(type="prediction", message="Not enough recent expense data for accurate prediction.", confidence=0.1, data={})

            expense_data_str = json.dumps([exp.model_dump(mode='json') for exp in recent_expenses], indent=2)
            prompt = f"""
            You are an expert financial analyst. Analyze the provided recent expense data (up to last 90 days) to predict next month's spending patterns and suggest improvements.
            The currency for all amounts is Indian Rupees (₹).
            Based on this data, provide the following in STRICT JSON format wrapped in ```json and ```.
            Recent Expense Data:
            {expense_data_str}
            {{
              "predicted_total": float,
              "category_breakdown": {{"Food": float,"Transportation": float,"Bills": float,"Entertainment": float,"Housing": float,"Groceries": float,"Health": float,"Education": float,"Personal Care": float,"Savings": float,"Travel": float,"Other": float}},
              "insights": ["string"],
              "recommendations": ["string"]
            }}
            Your response must be a valid JSON object wrapped in ```json and ```. Do not include any text outside of this.
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()
            else:
                logger.warning(f"AI response not wrapped in ```json: {response_text}")
                return AIInsight(type="prediction", message="AI response format invalid.", confidence=0.2, data={})

            try:
                ai_data = json.loads(response_text)
                predicted_total = ai_data.get('predicted_total', 0.0)
                message = f"Based on your spending patterns, predicted next month expenses: ₹{predicted_total:.2f}"
                return AIInsight(type="prediction", message=message, confidence=0.9, data=ai_data)
            except json.JSONDecodeError as e:
                logger.warning(f"AI prediction response was not valid JSON: {response_text}. Error: {e}")
                return AIInsight(type="prediction", message="AI prediction parsing failed.", confidence=0.5, data={})
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return AIInsight(type="prediction", message="Unable to generate prediction at this time.", confidence=0.0, data={})

    def categorize_expense(self, expense_name: str, amount: float) -> str:
        if not self.model:
            return "Other"
        try:
            valid_categories = ["Food", "Transportation", "Bills", "Entertainment", "Housing", "Groceries", "Health", "Education", "Personal Care", "Savings", "Travel", "Other"]
            prompt = f"""
            You are an AI assistant specialized in categorizing personal expenses. Your goal is to accurately assign the best-fitting category from a predefined list.
            Infer the most likely category from the expense name. The currency is Indian Rupees (₹).
            Expense Details:
            - Item: "{expense_name}"
            - Amount: ₹{amount:.2f}
            Available Categories: {", ".join(valid_categories)}
            Respond with exactly one word: the category name from the list provided. If no clear match exists, respond with "Other".
            """
            response = self.model.generate_content(prompt)
            category = response.text.strip()
            return category if category in valid_categories else "Other"
        except Exception as e:
            logger.error(f"AI categorization error for '{expense_name}': {e}")
            return "Other"

    def get_spending_insights(self, expenses: List[Expense]) -> List[AIInsight]:
        if not self.model or not expenses:
            return []
        try:
            summary_data = {
                "total_expenses_all_time": sum(exp.amount for exp in expenses),
                "category_spending_breakdown": {cat: sum(e.amount for e in expenses if e.category == cat) for cat in set(e.category for e in expenses)}
            }
            prompt = f"""
            You are a helpful financial assistant. Analyze the following summary of expense data. The currency is Indian Rupees (₹).
            Provide 3-5 concise, actionable insights or observations. Keep insights positive and actionable.
            Expense Summary Data:
            {json.dumps(summary_data, indent=2)}
            Respond as a STRICT JSON array of insight objects wrapped in ```json and ```. Each object must have a 'message' (string) and an optional 'data' (object) field.
            Example Format:
            ```json
            [
              {{"message": "Your Food expenses are consistently high.", "data": {{"category": "Food"}}}},
              {{"message": "You've saved a good amount on Transportation recently.", "data": {{"category": "Transportation"}}}}
            ]
            ```
            Your response must be a valid JSON array wrapped in ```json and ```. Do not include any text outside of this.
            """
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()

            ai_insights = []
            try:
                ai_raw_insights = json.loads(response_text)
                if isinstance(ai_raw_insights, list):
                    for item in ai_raw_insights:
                        if isinstance(item, dict) and "message" in item:
                            clean_message = item["message"].replace("$", "₹")
                            ai_insights.append(AIInsight(type="insight", message=clean_message, confidence=0.8, data=item.get("data", {})))
                return ai_insights
            except json.JSONDecodeError as e:
                logger.warning(f"AI insights response was not valid JSON: {response_text}. Error: {e}")
                return [AIInsight(type="insight", message="Failed to process detailed AI insights.", confidence=0.3, data={})]
        except Exception as e:
            logger.error(f"AI insights generation error: {e}")
            return [AIInsight(type="insight", message="Unable to generate AI insights due to an unexpected error.", confidence=0.0, data={})]

# Initialize AI service
ai_service = AIExpenseService()

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Smart Expense Tracker API is running!"}

@api_router.post("/expenses/predict", response_model=AIInsight, summary="Predict next month's expenses with AI")
async def predict_expenses_api(request: ExpenseListRequest):
    return await run_in_threadpool(ai_service.predict_next_month_expenses, request.expenses)

@api_router.get("/expenses/categorize", summary="Suggests a category for an expense using AI")
async def categorize_expense_api(expense_name: str, amount: float):
    category = await run_in_threadpool(ai_service.categorize_expense, expense_name=expense_name, amount=amount)
    return {"suggested_category": category}

@api_router.post("/expenses/insights", response_model=List[AIInsight], summary="Get AI-powered spending insights")
async def get_spending_insights_api(request: ExpenseListRequest):
    return await run_in_threadpool(ai_service.get_spending_insights, request.expenses)

@api_router.post("/expenses/analytics", response_model=ExpenseAnalytics, summary="Get comprehensive expense analytics")
async def get_expense_analytics_api(request: ExpenseListRequest):
    expenses = request.expenses
    if not expenses:
        return ExpenseAnalytics(total_expenses=0.0, category_breakdown={}, monthly_trend=[])
    total_expenses = sum(exp.amount for exp in expenses)
    category_breakdown = {}
    for exp in expenses:
        category_breakdown[exp.category] = category_breakdown.get(exp.category, 0.0) + exp.amount
    monthly_trend = []
    today = datetime.now()
    for i in range(6):
        target_year, target_month = today.year, today.month - i
        while target_month <= 0:
            target_month += 12; target_year -= 1
        month_str = datetime(target_year, target_month, 1).strftime('%Y-%m')
        month_expenses = [exp for exp in expenses if exp.date.startswith(month_str)]
        monthly_trend.append({"month": month_str, "total": sum(exp.amount for exp in month_expenses), "count": len(month_expenses)})
    monthly_trend.sort(key=lambda x: x['month'])
    return ExpenseAnalytics(total_expenses=total_expenses, category_breakdown=category_breakdown, monthly_trend=monthly_trend)

@api_router.post("/budget/alerts", response_model=List[BudgetAlert], summary="Get budget alerts based on spending")
async def get_budget_alerts_api(request: BudgetAlertRequest):
    expenses, budgets = request.expenses, request.budgets
    alerts = []
    current_month_str = datetime.now().strftime('%Y-%m')
    for budget in budgets:
        spent = sum(exp.amount for exp in expenses if exp.category == budget.category and exp.date.startswith(current_month_str))
        percentage = (spent / budget.amount) * 100 if budget.amount > 0 else 0.0
        if percentage >= 75: 
            alert_type = "warning"
            if percentage >= 90:
                alert_type = "danger"
            alerts.append(BudgetAlert(category=budget.category, budget_amount=budget.amount, spent_amount=spent, percentage_used=percentage, alert_type=alert_type))
    return alerts

@api_router.get("/test-ai", summary="Test AI categorization")
async def test_ai():
    try:
        category = await run_in_threadpool(ai_service.categorize_expense, "Coffee at Starbucks", 150.0)
        return {"success": True, "category": category}
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_router.get("/health", summary="Health check endpoint")
async def health_check():
    return {"status": "healthy", "ai_service_status": "available" if ai_service.model else "unavailable", "timestamp": datetime.now().isoformat()}

# Include the router in the main app
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
