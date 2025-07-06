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
        # Using 'gemini-pro' as 'gemma-2-27b-it' might have specific access or cost implications.
        # If 'gemma-2-27b-it' is preferred and available, replace 'gemini-pro'.
        # Note: 'gemma-2-27b-it' might be a specific version or alias, 'gemini-pro' is a common choice.
        genai.configure(api_key=GOOGLE_API_KEY)
        logger.info("Google Generative AI configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Google Generative AI: {e}")

# Create the main app
app = FastAPI(title="Smart Expense Tracker API", version="1.0.0",
              description="Backend API for Smart Expense Tracker with AI-powered insights.")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # TODO: Restrict to your frontend domain in production, e.g., ["http://localhost:8000", "https://your-frontend-domain.com"]
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
    id: str # Added ID for consistent budget management (though not used for persistence on backend)
    category: str
    amount: float
    period: str = "monthly"  # monthly, weekly, yearly

class ExpenseAnalytics(BaseModel):
    total_expenses: float
    category_breakdown: Dict[str, float]
    monthly_trend: List[Dict[str, Any]]
    # budget_status is computed on frontend based on `get_budget_alerts`

class AIInsight(BaseModel):
    type: str  # prediction, recommendation, alert, insight
    message: str
    confidence: float = Field(..., ge=0.0, le=1.0) # Confidence score between 0 and 1
    data: Dict[str, Any]

class ExpenseListRequest(BaseModel):
    expenses: List[Expense]

class BudgetAlert(BaseModel):
    category: str
    budget_amount: float
    spent_amount: float
    percentage_used: float = Field(..., ge=0.0)
    alert_type: str  # warning, danger, info

class BudgetAlertRequest(BaseModel):
    expenses: List[Expense]
    budgets: List[Budget]

# AI Service Class
class AIExpenseService:
    def __init__(self):
        self.model = None
        if GOOGLE_API_KEY:
            try:
                self.model = genai.GenerativeModel('gemini-pro') 
                logger.info("AI model 'gemini-pro' initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize AI model: {e}")

    async def predict_next_month_expenses(self, expenses: List[Expense]) -> AIInsight:
        """Predict next month's expenses using AI"""
        if not self.model:
            logger.warning("AI model not available for prediction.")
            return AIInsight(
                type="prediction",
                message="AI service not available. Please check if GOOGLE_API_KEY is set.",
                confidence=0.0,
                data={"predicted_total": 0.0, "category_breakdown": {}, "insights": [], "recommendations": []}
            )
        
        try:
            # Prepare expense data, considering recent activity to manage token usage
            # Limiting to last 90 days of expenses for relevance and token management
            recent_expenses = [
                exp for exp in expenses 
                if (datetime.strptime(exp.date, '%Y-%m-%d') >= datetime.now() - timedelta(days=90))
            ]
            
            # If no recent expenses, return a basic prediction
            if not recent_expenses:
                logger.info("Not enough recent expense data for AI prediction.")
                return AIInsight(
                    type="prediction",
                    message="Not enough recent expense data for accurate prediction. Add more expenses to get insights.",
                    confidence=0.1,
                    data={"predicted_total": 0.0, "category_breakdown": {}, "insights": ["No recent spending data available."], "recommendations": []}
                )

            # Convert Pydantic models to dicts for JSON serialization
            expense_data_dicts = [exp.model_dump(mode='json') for exp in recent_expenses]
            expense_data_str = json.dumps(expense_data_dicts, indent=2)

            prompt = f"""
            You are an expert financial analyst. Analyze the provided recent expense data (up to last 90 days) to predict next month's spending patterns and suggest improvements.
            The currency for all amounts is Indian Rupees (₹).

            Recent Expense Data:
            {expense_data_str}

            Based on this data, provide the following in STRICT JSON format. Do not include any other text or explanation outside the JSON.
            Ensure all monetary values are formatted as floats.

            {{
              "predicted_total": float,  // Predicted total spending for the next month in INR
              "category_breakdown": {{  // Predicted spending per category for the next month in INR. Include all categories from the list below, even if 0.
                "Food": float,
                "Transportation": float,
                "Bills": float,
                "Entertainment": float,
                "Housing": float,
                "Groceries": float,
                "Health": float,
                "Education": float,
                "Personal Care": float,
                "Savings": float,
                "Travel": float,
                "Other": float
              }},
              "insights": [  // List of key observations about spending habits. Each item is a string.
                "string",
                "string"
              ],
              "recommendations": [  // List of actionable tips for budget optimization. Each item is a string.
                "string",
                "string"
              ]
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            
            # Extract JSON from potential markdown block
            response_text = response.text.strip()
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()

            try:
                ai_data = json.loads(response_text)
                predicted_total = ai_data.get('predicted_total', 0.0)
                message = f"Based on your spending patterns, predicted next month expenses: ₹{predicted_total:.2f}"
                
                # Ensure all required keys are present and have default types
                ai_data.setdefault('predicted_total', 0.0)
                ai_data.setdefault('category_breakdown', {})
                ai_data.setdefault('insights', [])
                ai_data.setdefault('recommendations', [])

                # Validate/normalize category breakdown to include all standard categories
                standard_categories = [
                    "Food", "Transportation", "Bills", "Entertainment", "Housing", 
                    "Groceries", "Health", "Education", "Personal Care", "Savings", 
                    "Travel", "Other"
                ]
                normalized_breakdown = {cat: ai_data['category_breakdown'].get(cat, 0.0) for cat in standard_categories}
                ai_data['category_breakdown'] = normalized_breakdown


                return AIInsight(
                    type="prediction",
                    message=message,
                    confidence=0.9, # High confidence if AI provides structured data
                    data=ai_data
                )
            except json.JSONDecodeError as e:
                logger.warning(f"AI prediction response was not valid JSON: {response_text}. Error: {e}")
                # Fallback to average monthly spending from recent expenses if AI response is invalid
                monthly_totals = {}
                for exp in recent_expenses:
                    month = exp.date[:7] # YYYY-MM
                    monthly_totals[month] = monthly_totals.get(month, 0.0) + exp.amount
                
                estimated_total = sum(monthly_totals.values()) / len(monthly_totals) if monthly_totals else 0.0
                
                # Simple fallback category breakdown based on historical proportion
                total_recent_spending = sum(e.amount for e in recent_expenses)
                fallback_category_breakdown = {}
                for cat in set(e.category for e in recent_expenses):
                    cat_total = sum(e.amount for e in recent_expenses if e.category == cat)
                    if total_recent_spending > 0:
                        fallback_category_breakdown[cat] = (cat_total / total_recent_spending) * estimated_total
                    else:
                        fallback_category_breakdown[cat] = 0.0

                return AIInsight(
                    type="prediction",
                    message=f"Estimated next month expenses: ₹{estimated_total:.2f} (AI prediction parsing failed, estimated from historical average).",
                    confidence=0.5, # Lower confidence for fallback
                    data={
                        "predicted_total": estimated_total,
                        "category_breakdown": fallback_category_breakdown,
                        "insights": ["AI struggled to provide a detailed prediction. Ensure your expense data is consistent."],
                        "recommendations": ["Review your largest historical spending categories to identify potential savings."]
                    }
                )
        except Exception as e:
            logger.error(f"AI prediction error: {e}")
            return AIInsight(
                type="prediction",
                message="Unable to generate prediction at this time. Please try again later.",
                confidence=0.0,
                data={"error": str(e)}
            )

    async def categorize_expense(self, expense_name: str, amount: float) -> str:
        """Suggest expense category using AI"""
        if not self.model:
            logger.warning("AI model not available for categorization.")
            return "Other"
        try:
            valid_categories = [
                "Food", "Transportation", "Bills", "Entertainment", "Housing", 
                "Groceries", "Health", "Education", "Personal Care", "Savings", 
                "Travel", "Other"
            ]
            categories_list_str = ", ".join(valid_categories)

            prompt = f"""
            Categorize the following expense into one of the provided categories. 
            Respond with ONLY the category name. If the expense does not clearly fit any of the provided categories, respond with "Other".
            The expense amount is in Indian Rupees (₹).

            Expense Details:
            - Item: "{expense_name}"
            - Amount: ₹{amount:.2f}

            Available Categories: {categories_list_str}
            """
            response = await self.model.generate_content_async(prompt)
            category = response.text.strip()
            
            # Ensure the response is one of the valid categories
            return category if category in valid_categories else "Other"
        except Exception as e:
            logger.error(f"AI categorization error for '{expense_name}' (Amount: ₹{amount:.2f}): {e}")
            return "Other"

    async def get_spending_insights(self, expenses: List[Expense]) -> List[AIInsight]:
        """Get AI-powered spending insights"""
        if not self.model or not expenses:
            logger.warning("AI model not available or no expenses provided for insights.")
            return []
        
        try:
            # Generate a comprehensive summary of expenses for the AI
            total_expenses = sum(exp.amount for exp in expenses)
            
            # Group expenses by category
            category_breakdown = {}
            for exp in expenses:
                category_breakdown[exp.category] = category_breakdown.get(exp.category, 0.0) + exp.amount
            category_breakdown = dict(sorted(category_breakdown.items(), key=lambda item: item[1], reverse=True))

            # Group expenses by month
            monthly_spending = {}
            for exp in expenses:
                month = exp.date[:7] # YYYY-MM
                monthly_spending[month] = monthly_spending.get(month, 0.0) + exp.amount
            monthly_spending = dict(sorted(monthly_spending.items())) # Sort by month chronologically

            # Find the largest single expense
            largest_single_expense = max(expenses, key=lambda exp: exp.amount, default=None)
            
            summary_data = {
                "total_expenses_all_time": total_expenses,
                "number_of_expenses_recorded": len(expenses),
                "data_collection_period": {
                    "start_date": min(exp.date for exp in expenses) if expenses else None,
                    "end_date": max(exp.date for exp in expenses) if expenses else None
                },
                "category_spending_breakdown": category_breakdown,
                "monthly_spending_trend": monthly_spending,
                "largest_single_expense": largest_single_expense.model_dump(mode='json') if largest_single_expense else None,
            }

            prompt = f"""
            You are a helpful financial assistant providing spending insights to a user.
            Analyze the following summary of their expense data. The currency for all amounts is Indian Rupees (₹).
            Provide 3-5 concise, actionable insights or observations based on the data. Focus on:
            - Notable spending patterns or trends (e.g., changes over time, categories with high/low spending).
            - Potential areas for savings, budget optimization, or financial planning.
            - Any noticeable anomalies or interesting facts.
            - Keep insights positive, encouraging, and actionable.

            Expense Summary Data:
            {json.dumps(summary_data, indent=2)}

            Respond as a STRICT JSON array of insight objects. Each object must have a 'message' (string) and an optional 'data' (object) field for supporting numerical values or context.
            Example Format:
            [
              {{ "message": "Your Food expenses are consistently high, totaling ₹15000 in the last month. Consider meal planning.", "data": {{ "category": "Food", "amount": 15000, "period": "last_month" }} }},
              {{ "message": "There was a significant increase in 'Entertainment' spending in November. Was this a special event?", "data": {{ "category": "Entertainment", "month": "2023-11", "trend": "increase" }} }},
              {{ "message": "You've saved a good amount by cutting down on Transportation costs recently. Keep it up!", "data": {{ "category": "Transportation", "trend": "decrease" }} }}
            ]
            """
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text.strip()
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()

            ai_insights = []
            try:
                ai_raw_insights = json.loads(response_text)
                if isinstance(ai_raw_insights, list):
                    for item in ai_raw_insights:
                        if isinstance(item, dict) and "message" in item:
                            # Replace any dollar signs that AI might generate by mistake to INR symbol
                            clean_message = item["message"].replace("$", "₹")
                            ai_insights.append(AIInsight(
                                type="insight",
                                message=clean_message,
                                confidence=0.8, # Default confidence for AI-generated insights
                                data=item.get("data", {})
                            ))
                else:
                    logger.warning(f"AI insights response was not a JSON list: {response_text}")

                if not ai_insights:
                    ai_insights.append(AIInsight(
                        type="insight",
                        message="No specific AI insights generated at this time. Track more expenses to get deeper analysis!",
                        confidence=0.5,
                        data={}
                    ))

            except json.JSONDecodeError as e:
                logger.warning(f"AI insights response was not valid JSON: {response_text}. Error: {e}")
                ai_insights.append(AIInsight(
                    type="insight",
                    message="Failed to process detailed AI insights. The AI model might have provided an unexpected format. Please try refreshing.",
                    confidence=0.3,
                    data={"raw_response": response_text, "error": str(e)}
                ))
            
            return ai_insights

        except Exception as e:
            logger.error(f"AI insights generation error: {e}")
            return [AIInsight(
                type="insight",
                message="Unable to generate AI insights at this time due to an unexpected error.",
                confidence=0.0,
                data={"error": str(e)}
            )]

# Initialize AI service
ai_service = AIExpenseService()

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Smart Expense Tracker API is running!"}

@api_router.post("/expenses/predict", response_model=AIInsight, summary="Predict next month's expenses with AI")
async def predict_expenses_api(request: ExpenseListRequest):
    """
    Predicts the user's total expenses and category-wise breakdown for the next month
    based on historical spending data using AI.
    """
    return await ai_service.predict_next_month_expenses(request.expenses)

@api_router.get("/expenses/categorize", summary="Suggests a category for an expense using AI")
async def categorize_expense_api(expense_name: str, amount: float):
    """
    Suggests an expense category for a given expense name and amount using AI,
    choosing from predefined categories.
    """
    category = await ai_service.categorize_expense(expense_name, amount)
    return {"suggested_category": category}

@api_router.post("/expenses/insights", response_model=List[AIInsight], summary="Get AI-powered spending insights")
async def get_spending_insights_api(request: ExpenseListRequest):
    """
    Generates AI-powered insights about spending patterns, trends, and recommendations
    based on the user's historical expense data.
    """
    return await ai_service.get_spending_insights(request.expenses)

@api_router.post("/expenses/analytics", response_model=ExpenseAnalytics, summary="Get comprehensive expense analytics")
async def get_expense_analytics_api(request: ExpenseListRequest):
    """
    Provides comprehensive analytics including total expenses, category breakdown,
    and monthly spending trends based on the provided expense list.
    """
    expenses = request.expenses
    if not expenses:
        return ExpenseAnalytics(
            total_expenses=0.0,
            category_breakdown={},
            monthly_trend=[],
        )

    total_expenses = sum(exp.amount for exp in expenses)
    
    category_breakdown = {}
    for exp in expenses:
        category_breakdown[exp.category] = category_breakdown.get(exp.category, 0.0) + exp.amount
    
    # Calculate monthly trend (last 6 months, ensuring correct month calculation)
    monthly_trend = []
    today = datetime.now()
    # Generate month strings for the last 6 months (inclusive of current month if data exists)
    for i in range(6):
        # Calculate the month `i` months ago
        # This handles year transitions correctly
        target_year = today.year
        target_month = today.month - i
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        
        month_str = datetime(target_year, target_month, 1).strftime('%Y-%m')
        
        month_expenses = [exp for exp in expenses if exp.date.startswith(month_str)]
        month_total = sum(exp.amount for exp in month_expenses)
        monthly_trend.append({
            "month": month_str,
            "total": month_total,
            "count": len(month_expenses)
        })
    
    # Sort monthly trend by month (oldest first for charts/display)
    monthly_trend.sort(key=lambda x: x['month'])

    return ExpenseAnalytics(
        total_expenses=total_expenses,
        category_breakdown=category_breakdown,
        monthly_trend=monthly_trend,
    )

@api_router.post("/budget/alerts", response_model=List[BudgetAlert], summary="Get budget alerts based on spending")
async def get_budget_alerts_api(request: BudgetAlertRequest):
    """
    Calculates and returns budget alerts for each category based on current month's spending
    against set budgets.
    """
    expenses = request.expenses
    budgets = request.budgets

    alerts = []
    
    current_month_str = datetime.now().strftime('%Y-%m')

    for budget in budgets:
        spent = sum(exp.amount for exp in expenses if exp.category == budget.category and exp.date.startswith(current_month_str))
        
        percentage = (spent / budget.amount) * 100 if budget.amount > 0 else 0.0
        
        # Only add an alert if percentage reaches a threshold
        if percentage >= 75: 
            alert_type = "info" # Default
            if percentage >= 90:
                alert_type = "danger"
            elif percentage >= 75: # This will catch 75-89.9%
                alert_type = "warning"
            
            alerts.append(BudgetAlert(
                category=budget.category,
                budget_amount=budget.amount,
                spent_amount=spent,
                percentage_used=percentage,
                alert_type=alert_type
            ))
    return alerts

@api_router.get("/health", summary="Health check endpoint")
async def health_check():
    """
    Checks the status of the API and AI service.
    """
    return {
        "status": "healthy",
        "ai_service_status": "available" if ai_service.model else "unavailable",
        "timestamp": datetime.now().isoformat()
    }

# Include the router in the main app
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
