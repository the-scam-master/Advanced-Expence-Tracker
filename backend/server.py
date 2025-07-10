from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
from pathlib import Path
import json
from datetime import datetime, timedelta
import uuid
from transformers import pipeline  # Hugging Face transformers for gemma-3-27b-it

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize Hugging Face pipeline for gemma-3-27b-it
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
if not HUGGINGFACE_TOKEN:
    logger.error("HUGGINGFACE_TOKEN is not set in the environment variables.")
try:
    generator = pipeline('text-generation', model='google/gemma-3-27b-it', token=HUGGINGFACE_TOKEN, device=0)  # Assumes GPU
    logger.info("Gemma-3-27b-it model initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Gemma-3-27b-it: {e}")
    generator = None

# Create the main app
app = FastAPI(title="Smart Expense Tracker API", version="1.0.0",
              description="Backend API for Smart Expense Tracker with AI-powered insights.")

api_router = APIRouter(prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["https://advanced-expence-tracker.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models (same as previous server.py)
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

class ComprehensiveAnalysisRequest(BaseModel):
    expenses: List[Expense]
    income: List[Expense]

class ComprehensiveAnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

# In-memory storage
expenses_db = []
budgets_db = []

# AI Service Class for gemma-3-27b-it
class AIExpenseService:
    def __init__(self):
        self.model = generator

    def predict_next_month_expenses(self, expenses: List[Expense]) -> AIInsight:
        if not self.model:
            return AIInsight(type="prediction", message="AI service not available.", confidence=0.0, data={})
        
        try:
            recent_expenses = [
                exp for exp in expenses
                if datetime.strptime(exp.date, '%Y-%m-%d') >= datetime.now() - timedelta(days=90)
            ]
            if not recent_expenses:
                return AIInsight(type="prediction", message="Not enough recent expense data.", confidence=0.1, data={})

            expense_data_str = json.dumps([exp.dict() for exp in recent_expenses], indent=2)
            prompt = f"""
            Analyze the following expense data (last 90 days, in Indian Rupees ₹) to predict next month's spending patterns.
            Expense Data:
            {expense_data_str}
            Provide a JSON response with:
            - predicted_total: float
            - category_breakdown: object with categories (food, transportation, bills, entertainment, shopping, health, other)
            - insights: list of strings
            - recommendations: list of strings
            """
            response = self.model(prompt, max_length=2000, num_return_sequences=1)[0]['generated_text']
            response_text = response[len(prompt):].strip()
            if response_text.startswith('```json') and response_text.endswith('```'):
                response_text = response_text[7:-3].strip()
            ai_data = json.loads(response_text)
            predicted_total = ai_data.get('predicted_total', 0.0)
            message = f"Predicted next month expenses: ₹{predicted_total:.2f}"
            return AIInsight(type="prediction", message=message, confidence=0.9, data=ai_data)
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return AIInsight(type="prediction", message="Unable to generate prediction.", confidence=0.0, data={})

    def categorize_expense(self, expense_name: str, amount: float) -> str:
        if not self.model:
            return "other"
        try:
            valid_categories = ["food", "transportation", "bills", "entertainment", "shopping", "health", "other"]
            prompt = f"""
            Categorize the expense: "{expense_name}" (₹{amount:.2f}).
            Available Categories: {", ".join(valid_categories)}
            Respond with one word: the category name (lowercase).
            """
            response = self.model(prompt, max_length=50, num_return_sequences=1)[0]['generated_text']
            category = response[len(prompt):].strip().lower()
            return category if category in valid_categories else "other"
        except Exception as e:
            logger.error(f"AI categorization error: {e}")
            return "other"

    def get_spending_insights(self, expenses: List[Expense]) -> List[AIInsight]:
        if not self.model or not expenses:
            return []
        try:
            summary_data = {
                "total_expenses": sum(exp.amount for exp in expenses),
                "category_spending": {
                    cat: sum(e.amount for e in expenses if e.category == cat)
                    for cat in set(e.category for e in expenses)
                }
            }
            prompt = f"""
            Analyze the expense data (in Indian Rupees ₹):
            {json.dumps(summary_data, indent=2)}
            Provide 3-5 actionable insights in JSON format:
            [
              {{"message": "string", "data": {{"category": "string"}}}},
              ...
            ]
            """
            response = self.model(prompt, max_length=2000, num_return_sequences=1)[0]['generated_text']
            response_text = response[len(prompt):].strip()
            if response_text.startswith('```json') and response_text.endswith('```'):
                response_text = response_text[7:-3].strip()
            ai_insights = []
            for item in json.loads(response_text):
                if "message" in item:
                    ai_insights.append(AIInsight(
                        type="insight",
                        message=item["message"].replace("$", "₹"),
                        confidence=0.8,
                        data=item.get("data", {})
                    ))
            return ai_insights
        except Exception as e:
            logger.error(f"AI insights error: {e}")
            return [AIInsight(type="insight", message="Unable to generate insights.", confidence=0.0, data={})]

    def calculate_financial_health(self, expenses: List[Expense], income: List[Expense]) -> Dict[str, Any]:
        if not self.model:
            return {"score": 0, "grade": "N/A", "message": "AI service unavailable", "factors": []}
        try:
            total_income = sum(inc.amount for inc in income)
            total_expenses = sum(exp.amount for exp in expenses)
            savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
            category_spending = {
                cat: sum(e.amount for e in expenses if e.category == cat)
                for cat in set(e.category for e in expenses)
            }
            prompt = f"""
            Analyze financial data (in Indian Rupees ₹):
            - Total Income: ₹{total_income:.2f}
            - Total Expenses: ₹{total_expenses:.2f}
            - Savings Rate: {savings_rate:.2f}%
            - Category Spending: {json.dumps(category_spending, indent=2)}
            Provide a JSON response with:
            - score: float (0-100)
            - grade: string (A, B, C, D, F)
            - message: string
            - factors: list of strings
            """
            response = self.model(prompt, max_length=2000, num_return_sequences=1)[0]['generated_text']
            response_text = response[len(prompt):].strip()
            if response_text.startswith('```json') and response_text.endswith('```'):
                response_text = response_text[7:-3].strip()
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Financial health error: {e}")
            return {"score": 0, "grade": "N/A", "message": "Unable to calculate health score.", "factors": []}

    def get_savings_advice(self, expenses: List[Expense], income: List[Expense]) -> List[Dict[str, Any]]:
        if not self.model:
            return []
        try:
            total_income = sum(inc.amount for inc in income)
            total_expenses = sum(exp.amount for exp in expenses)
            category_spending = {
                cat: sum(e.amount for e in expenses if e.category == cat)
                for cat in set(e.category for e in expenses)
            }
            prompt = f"""
            Analyze financial data (in Indian Rupees ₹):
            - Total Income: ₹{total_income:.2f}
            - Total Expenses: ₹{total_expenses:.2f}
            - Category Spending: {json.dumps(category_spending, indent=2)}
            Provide 3-5 savings advice in JSON format:
            [
              {{"title": "string", "message": "string", "priority": "string", "potential_savings": float}},
              ...
            ]
            """
            response = self.model(prompt, max_length=2000, num_return_sequences=1)[0]['generated_text']
            response_text = response[len(prompt):].strip()
            if response_text.startswith('```json') and response_text.endswith('```'):
                response_text = response_text[7:-3].strip()
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Savings advice error: {e}")
            return []

# Initialize AI service
ai_service = AIExpenseService()

# API Endpoints (same as previous server.py)
@api_router.get("/")
async def root():
    return {"message": "Smart Expense Tracker API is running!"}

@api_router.get("/health", summary="Health check endpoint")
async def health_check():
    return {
        "status": "healthy",
        "ai_service_status": "available" if ai_service.model else "unavailable",
        "timestamp": datetime.now().isoformat()
    }

@api_router.get("/test", summary="Test endpoint")
async def test_endpoint():
    return {"success": True, "message": "Test endpoint is working."}

@api_router.get("/test-ai", summary="Test AI categorization")
async def test_ai():
    try:
        category = await run_in_threadpool(ai_service.categorize_expense, "Coffee at Starbucks", 150.0)
        return {"success": True, "category": category}
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_router.get("/expenses", response_model=List[Expense], summary="Get all expenses")
async def get_expenses():
    return expenses_db

@api_router.post("/expenses", response_model=Expense, summary="Add new expense")
async def add_expense(expense: Expense):
    expense.id = str(uuid.uuid4())
    expenses_db.append(expense)
    return expense

@api_router.get("/expenses/categorize", summary="Suggests a category for an expense using AI")
async def categorize_expense_api(expense_name: str, amount: float):
    category = await run_in_threadpool(ai_service.categorize_expense, expense_name, amount)
    return {"success": True, "suggested_category": category}

@api_router.post("/expenses/insights", response_model=List[AIInsight], summary="Get AI-powered spending insights")
async def get_spending_insights_api(request: ExpenseListRequest):
    return await run_in_threadpool(ai_service.get_spending_insights, request.expenses)

@api_router.post("/expenses/predict", response_model=AIInsight, summary="Predict next month's expenses with AI")
async def predict_expenses_api(request: ExpenseListRequest):
    return await run_in_threadpool(ai_service.predict_next_month_expenses, request.expenses)

@api_router.post("/expenses/analytics", response_model=ExpenseAnalytics, summary="Get comprehensive expense analytics")
async def get_expense_analytics_api(request: ExpenseListRequest):
    expenses = request.expenses
    if not expenses:
        return ExpenseAnalytics(total_expenses=0.0, category_breakdown={}, monthly_trend=[])
    total_expenses = sum(exp.amount for exp in expenses)
    category_breakdown = {exp.category: 0.0 for exp in expenses}
    for exp in expenses:
        category_breakdown[exp.category] += exp.amount
    monthly_trend = []
    today = datetime.now()
    for i in range(6):
        target_year, target_month = today.year, today.month - i
        if target_month <= 0:
            target_month += 12
            target_year -= 1
        month_str = f"{target_year}-{target_month:02d}"
        month_expenses = [exp for exp in expenses if exp.date.startswith(month_str)]
        monthly_trend.append({
            "month": month_str,
            "total": sum(exp.amount for exp in month_expenses),
            "count": len(month_expenses)
        })
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
            alert_type = "danger" if percentage >= 90 else "warning"
            alerts.append(BudgetAlert(
                category=budget.category,
                budget_amount=budget.amount,
                spent_amount=spent,
                percentage_used=percentage,
                alert_type=alert_type
            ))
    return alerts

@api_router.get("/bUDgets", response_model=List[Budget], summary="Get all budgets")
async def get_budgets():
    return budgets_db

@api_router.post("/budgets", response_model=Budget, summary="Add new budget")
async def add_budget(budget: Budget):
    budget.id = str(uuid.uuid4())
    budgets_db.append(budget)
    return budget

@api_router.post("/ai/comprehensive-analysis", response_model=ComprehensiveAnalysisResponse, summary="Get comprehensive AI analysis")
async def comprehensive_analysis(request: ComprehensiveAnalysisRequest):
    try:
        expenses = request.expenses
        income = request.income
        health_score = await run_in_threadpool(ai_service.calculate_financial_health, expenses, income)
        insights = await run_in_threadpool(ai_service.get_spending_insights, expenses)
        prediction = await run_in_threadpool(ai_service.predict_next_month_expenses, expenses)
        savings_advice = await run_in_threadpool(ai_service.get_savings_advice, expenses, income)
        return ComprehensiveAnalysisResponse(
            success=True,
            data={
                "health_score": health_score,
                "insights": [insight.dict() for insight in insights],
                "prediction": prediction.dict(),
                "savings_advice": savings_advice
            }
        )
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {e}")
        return ComprehensiveAnalysisResponse(success=False, error=str(e), data={})

# Include the router in the main app
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
