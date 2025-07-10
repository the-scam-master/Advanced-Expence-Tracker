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
import google.generativeai as genai
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression

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
              description="Backend API for Smart Expense Tracker with enhanced AI-powered insights.")

api_router = APIRouter(prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["https://advanced-expence-tracker.vercel.app"],
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

class ComprehensiveAnalysisRequest(BaseModel):
    expenses: List[Expense]
    budgets: List[Budget]

class ComprehensiveAnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None

# In-memory storage
expenses_db = []
budgets_db = []

# Enhanced AI Service Class
class AIExpenseService:
    def __init__(self):
        self.model = None
        self.valid_categories = ["Food", "Transportation", "Bills", "Entertainment", "Housing", "Groceries", 
                                "Health", "Education", "Personal Care", "Savings", "Travel", "Other"]
        if GOOGLE_API_KEY:
            try:
                self.model = genai.GenerativeModel('gemma-3-27b-it')
                logger.info("AI model 'gemma-3-27b-it' initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize AI model: {e}")

    def predict_next_month_expenses(self, expenses: List[Expense]) -> AIInsight:
        if not self.model:
            logger.warning("AI model not available for prediction.")
            return AIInsight(type="prediction", message="AI service not available.", confidence=0.0, data={})

        try:
            # Filter recent expenses (last 90 days)
            recent_expenses = [
                exp for exp in expenses
                if datetime.strptime(exp.date, '%Y-%m-%d') >= datetime.now() - timedelta(days=90)
            ]
            if not recent_expenses:
                logger.info("Not enough recent expense data for AI prediction.")
                return AIInsight(type="prediction", message="Not enough recent expense data for accurate prediction.", confidence=0.1, data={})

            # Aggregate expenses by category and month for trend analysis
            monthly_data = defaultdict(list)
            for exp in recent_expenses:
                date = datetime.strptime(exp.date, '%Y-%m-%d')
                month_key = f"{date.year}-{date.month}"
                monthly_data[month_key].append(exp)

            # Linear regression for each category
            category_totals = defaultdict(list)
            for month, exps in monthly_data.items():
                month_cats = defaultdict(float)
                for exp in exps:
                    month_cats[exp.category] += exp.amount
                for cat in self.valid_categories:
                    category_totals[cat].append(month_cats.get(cat, 0.0))

            predictions = {}
            total_predicted = 0.0
            for cat in self.valid_categories:
                amounts = category_totals[cat]
                if len(amounts) >= 2:
                    X = np.array(range(len(amounts))).reshape(-1, 1)
                    y = np.array(amounts)
                    model = LinearRegression()
                    model.fit(X, y)
                    next_month_pred = model.predict([[len(amounts)]])[0]
                    predictions[cat] = max(0, float(next_month_pred))
                    total_predicted += predictions[cat]
                else:
                    predictions[cat] = sum(amounts) / len(amounts) if amounts else 0.0
                    total_predicted += predictions[cat]

            # Generate insights using Gemini
            expense_data_str = json.dumps([exp.model_dump(mode='json') for exp in recent_expenses], indent=2)
            prompt = f"""
            You are an expert financial analyst. Analyze the provided recent expense data (up to last 90 days) to predict next month's spending patterns and suggest improvements.
            The currency for all amounts is Indian Rupees (₹).
            Recent Expense Data:
            {expense_data_str}
            Predicted category breakdown (based on trend analysis):
            {json.dumps(predictions, indent=2)}
            Provide the following in STRICT JSON format. Do not include any other text or explanation outside the JSON.
            {{
              "predicted_total": float,
              "category_breakdown": {json.dumps({cat: float(amt) for cat, amt in predictions.items()})},
              "insights": ["string"],
              "recommendations": ["string"]
            }}
            """
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()

            try:
                ai_data = json.loads(response_text)
                ai_data['predicted_total'] = total_predicted
                ai_data['category_breakdown'] = predictions
                message = f"Based on your spending patterns, predicted next month expenses: ₹{total_predicted:.2f}"
                return AIInsight(type="prediction", message=message, confidence=0.9, data=ai_data)
            except json.JSONDecodeError as e:
                logger.warning(f"AI prediction response was not valid JSON: {response_text}. Error: {e}")
                return AIInsight(type="prediction", message="AI prediction parsing failed.", confidence=0.5, data={})
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return AIInsight(type="prediction", message="Unable to generate prediction at this time.", confidence=0.0, data={"error": str(e)})

    def categorize_expense(self, expense_name: str, amount: float) -> str:
        if not self.model:
            logger.warning("AI model not available for categorization.")
            return "Other"
        try:
            prompt = f"""
            You are an AI assistant specialized in categorizing personal expenses. Your goal is to accurately assign the best-fitting category from a predefined list.
            Infer the most likely category from the expense name. The currency is Indian Rupees (₹).
            Expense Details:
            - Item: "{expense_name}"
            - Amount: ₹{amount:.2f}
            Available Categories: {", ".join(self.valid_categories)}
            Examples of Expense to Category Mapping:
            - Expense: "Morning Coffee" -> Food
            - Expense: "Local Bus Fare" -> Transportation
            - Expense: "Electricity Bill" -> Bills
            - Expense: "Movie Tickets" -> Entertainment
            - Expense: "New T-shirt" -> Personal Care
            Respond with ONLY the category name. If no clear match exists, respond with "Other".
            """
            response = self.model.generate_content(prompt)
            category = response.text.strip()
            return category if category in self.valid_categories else "Other"
        except Exception as e:
            logger.error(f"AI categorization error for '{expense_name}': {e}")
            return "Other"

    def get_spending_insights(self, expenses: List[Expense]) -> List[AIInsight]:
        if not self.model or not expenses:
            logger.warning("AI model not available or no expenses provided for insights.")
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
            Respond as a STRICT JSON array of insight objects. Each object must have a 'message' (string) and an optional 'data' (object) field.
            Example Format:
            [
              {{"message": "Your Food expenses are consistently high.", "data": {{"category": "Food"}}}},
              {{"message": "You've saved a good amount on Transportation recently.", "data": {{"category": "Transportation"}}}}
            ]
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
                return [AIInsight(type="insight", message="Failed to process detailed AI insights.", confidence=0.3, data={"error": str(e)})]
        except Exception as e:
            logger.error(f"AI insights generation error: {e}")
            return [AIInsight(type="insight", message="Unable to generate AI insights due to an unexpected error.", confidence=0.0, data={"error": str(e)})]

    def comprehensive_analysis(self, expenses: List[Expense], budgets: List[Budget]) -> ComprehensiveAnalysisResponse:
        try:
            if not expenses and not budgets:
                return ComprehensiveAnalysisResponse(success=False, data={}, error="No expenses or budgets provided.")

            # Aggregate expense data
            total_expenses = sum(exp.amount for exp in expenses)
            category_breakdown = defaultdict(float)
            for exp in expenses:
                category_breakdown[exp.category] += exp.amount

            # Analyze budget adherence
            budget_status = {}
            current_month_str = datetime.now().strftime('%Y-%m')
            for budget in budgets:
                spent = sum(exp.amount for exp in expenses if exp.category == budget.category and exp.date.startswith(current_month_str))
                percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0.0
                budget_status[budget.category] = {
                    "budget_amount": budget.amount,
                    "spent_amount": spent,
                    "percentage_used": percentage,
                    "status": "over" if percentage > 100 else "warning" if percentage >= 80 else "good"
                }

            # Generate AI-driven financial health insights
            if not self.model:
                return ComprehensiveAnalysisResponse(success=False, data={}, error="AI model not available.")

            expense_data_str = json.dumps([exp.model_dump(mode='json') for exp in expenses], indent=2)
            budget_data_str = json.dumps([budget.model_dump(mode='json') for budget in budgets], indent=2)
            prompt = f"""
            You are an expert financial analyst. Analyze the following expense and budget data to provide a comprehensive financial health analysis.
            The currency is Indian Rupees (₹).
            Expense Data:
            {expense_data_str}
            Budget Data:
            {budget_data_str}
            Provide a JSON response with:
            - financial_health_score: float (0-100)
            - summary: string
            - recommendations: list of 3-5 strings
            - key_metrics: object with total_expenses, top_category, budget_adherence
            """
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()

            try:
                ai_data = json.loads(response_text)
                ai_data["key_metrics"] = {
                    "total_expenses": total_expenses,
                    "category_breakdown": dict(category_breakdown),
                    "budget_status": budget_status
                }
                return ComprehensiveAnalysisResponse(success=True, data=ai_data, error=None)
            except json.JSONDecodeError as e:
                logger.warning(f"AI analysis response was not valid JSON: {response_text}. Error: {e}")
                return ComprehensiveAnalysisResponse(success=False, data={}, error="Failed to parse AI analysis response.")
        except Exception as e:
            logger.error(f"Comprehensive analysis error: {e}")
            return ComprehensiveAnalysisResponse(success=False, data={}, error=str(e))

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
            target_month += 12
            target_year -= 1
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
            alert_type = "warning" if percentage < 90 else "danger"
            alerts.append(BudgetAlert(category=budget.category, budget_amount=budget.amount, spent_amount=spent, percentage_used=percentage, alert_type=alert_type))
    return alerts

@api_router.post("/analysis/comprehensive", response_model=ComprehensiveAnalysisResponse, summary="Get comprehensive financial analysis")
async def get_comprehensive_analysis_api(request: ComprehensiveAnalysisRequest):
    return await run_in_threadpool(ai_service.comprehensive_analysis, request.expenses, request.budgets)

@api_router.get("/health", summary="Health check endpoint")
async def health_check():
    return {"status": "healthy", "ai_service_status": "available" if ai_service.model else "unavailable", "timestamp": datetime.now().isoformat()}

# Include the router in the main app
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
