from fastapi import FastAPI, APIRouter, HTTPException
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
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure Google Gemini
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Create the main app
app = FastAPI(title="Expense Tracker API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
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
    category: str
    amount: float
    period: str = "monthly"  # monthly, weekly, yearly

class ExpenseAnalytics(BaseModel):
    total_expenses: float
    category_breakdown: Dict[str, float]
    monthly_trend: List[Dict[str, Any]]
    budget_status: Dict[str, Any]

class AIInsight(BaseModel):
    type: str  # prediction, recommendation, alert
    message: str
    confidence: float
    data: Dict[str, Any]

class ExpenseListRequest(BaseModel):
    expenses: List[Expense]

class BudgetAlert(BaseModel):
    category: str
    budget_amount: float
    spent_amount: float
    percentage_used: float
    alert_type: str  # warning, danger, info

# AI Service Class
class AIExpenseService:
    def __init__(self):
        self.model = None
        if GOOGLE_API_KEY:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                logging.error(f"Failed to initialize Gemini model: {e}")

    async def predict_next_month_expenses(self, expenses: List[Expense]) -> AIInsight:
        """Predict next month's expenses using AI"""
        try:
            if not self.model:
                return AIInsight(
                    type="prediction",
                    message="AI service not available. Please set GOOGLE_API_KEY in .env file.",
                    confidence=0.0,
                    data={"predicted_amount": 0}
                )

            # Prepare expense data for analysis
            expense_data = []
            for expense in expenses:
                expense_data.append({
                    "date": expense.date,
                    "amount": expense.amount,
                    "category": expense.category,
                    "name": expense.name
                })

            # Create prompt for AI
            prompt = f"""
            Analyze the following expense data and predict next month's total expenses:
            
            Expense Data: {json.dumps(expense_data, indent=2)}
            
            Please provide:
            1. Predicted total amount for next month
            2. Category-wise breakdown
            3. Key insights about spending patterns
            4. Recommendations for budget optimization
            
            Respond in JSON format with keys: predicted_total, category_breakdown, insights, recommendations
            """

            response = self.model.generate_content(prompt)
            
            # Parse AI response
            try:
                ai_data = json.loads(response.text)
                return AIInsight(
                    type="prediction",
                    message=f"Based on your spending patterns, predicted next month expenses: ${ai_data.get('predicted_total', 0):.2f}",
                    confidence=0.85,
                    data=ai_data
                )
            except json.JSONDecodeError:
                # Fallback to simple calculation if AI response is not JSON
                total_last_month = sum(exp.amount for exp in expenses[-30:]) if expenses else 0
                return AIInsight(
                    type="prediction",
                    message=f"Estimated next month expenses: ${total_last_month:.2f}",
                    confidence=0.6,
                    data={"predicted_total": total_last_month}
                )

        except Exception as e:
            logging.error(f"AI prediction error: {e}")
            return AIInsight(
                type="prediction",
                message="Unable to generate prediction at this time",
                confidence=0.0,
                data={"error": str(e)}
            )

    async def categorize_expense(self, expense_name: str, amount: float) -> str:
        """Suggest expense category using AI"""
        try:
            if not self.model:
                return "Other"

            prompt = f"""
            Categorize this expense: "{expense_name}" (Amount: ${amount})
            
            Choose from these categories:
            Food, Transportation, Bills, Entertainment, Housing, Groceries, Health, Education, Personal Care, Savings, Travel, Other
            
            Respond with just the category name.
            """

            response = self.model.generate_content(prompt)
            category = response.text.strip()
            
            valid_categories = ["Food", "Transportation", "Bills", "Entertainment", "Housing", "Groceries", "Health", "Education", "Personal Care", "Savings", "Travel", "Other"]
            
            return category if category in valid_categories else "Other"

        except Exception as e:
            logging.error(f"AI categorization error: {e}")
            return "Other"

    async def get_spending_insights(self, expenses: List[Expense]) -> List[AIInsight]:
        """Get AI-powered spending insights"""
        try:
            if not self.model or not expenses:
                return []

            # Analyze spending patterns
            df = pd.DataFrame([{
                'date': exp.date,
                'amount': exp.amount,
                'category': exp.category,
                'name': exp.name
            } for exp in expenses])

            # Generate insights
            insights = []
            
            # Top spending category
            top_category = df.groupby('category')['amount'].sum().idxmax()
            top_amount = df.groupby('category')['amount'].sum().max()
            
            insights.append(AIInsight(
                type="insight",
                message=f"Your highest spending category is {top_category} with ${top_amount:.2f}",
                confidence=0.9,
                data={"category": top_category, "amount": top_amount}
            ))

            # Spending trend
            recent_expenses = df[df['date'] >= (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')]
            if len(recent_expenses) > 0:
                weekly_total = recent_expenses['amount'].sum()
                insights.append(AIInsight(
                    type="insight",
                    message=f"You've spent ${weekly_total:.2f} in the last 7 days",
                    confidence=0.8,
                    data={"weekly_spending": weekly_total}
                ))

            return insights

        except Exception as e:
            logging.error(f"AI insights error: {e}")
            return []

# Initialize AI service
ai_service = AIExpenseService()

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Expense Tracker API is running!"}

@api_router.post("/expenses/predict", response_model=AIInsight)
async def predict_expenses(request: ExpenseListRequest):
    """Predict next month's expenses using AI"""
    return await ai_service.predict_next_month_expenses(request.expenses)

@api_router.get("/expenses/categorize")
async def categorize_expense(expense_name: str, amount: float):
    """Suggest category for an expense"""
    category = await ai_service.categorize_expense(expense_name, amount)
    return {"suggested_category": category}

@api_router.post("/expenses/insights", response_model=List[AIInsight])
async def get_spending_insights(request: ExpenseListRequest):
    """Get AI-powered spending insights"""
    return await ai_service.get_spending_insights(request.expenses)

@api_router.post("/expenses/analytics")
async def get_expense_analytics(request: ExpenseListRequest):
    """Get comprehensive expense analytics"""
    expenses = request.expenses
    
    if not expenses:
        return ExpenseAnalytics(
            total_expenses=0,
            category_breakdown={},
            monthly_trend=[],
            budget_status={}
        )

    # Calculate analytics
    total_expenses = sum(exp.amount for exp in expenses)
    
    # Category breakdown
    category_breakdown = {}
    for exp in expenses:
        category_breakdown[exp.category] = category_breakdown.get(exp.category, 0) + exp.amount

    # Monthly trend (last 6 months)
    monthly_trend = []
    for i in range(6):
        month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
        month_str = month_start.strftime('%Y-%m')
        
        month_expenses = [exp for exp in expenses if exp.date.startswith(month_str)]
        month_total = sum(exp.amount for exp in month_expenses)
        
        monthly_trend.append({
            "month": month_str,
            "total": month_total,
            "count": len(month_expenses)
        })

    return ExpenseAnalytics(
        total_expenses=total_expenses,
        category_breakdown=category_breakdown,
        monthly_trend=monthly_trend,
        budget_status={}
    )

@api_router.post("/budget/alerts")
async def get_budget_alerts(expenses: List[Expense], budgets: List[Budget]):
    """Get budget alerts based on spending"""
    alerts = []
    
    for budget in budgets:
        # Calculate spent amount for this category
        spent = sum(exp.amount for exp in expenses if exp.category == budget.category)
        percentage = (spent / budget.amount) * 100 if budget.amount > 0 else 0
        
        alert_type = "info"
        if percentage >= 90:
            alert_type = "danger"
        elif percentage >= 75:
            alert_type = "warning"
        
        alerts.append(BudgetAlert(
            category=budget.category,
            budget_amount=budget.amount,
            spent_amount=spent,
            percentage_used=percentage,
            alert_type=alert_type
        ))
    
    return alerts

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_service": "available" if GOOGLE_API_KEY else "unavailable",
        "timestamp": datetime.now().isoformat()
    }

# Include the router in the main app
app.include_router(api_router)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)