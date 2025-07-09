# 💰 Smart Expense Tracker

A **minimal, dark-themed** AI-powered expense tracker with clean tab-based navigation and core functionality.

## ✨ Key Features

### � **Dark Theme Design**
- Clean, minimal dark interface
- Easy on the eyes with proper contrast
- Modern typography using Inter font
- Organized tab-based navigation

### 🤖 **AI-Powered**
- **Smart categorization** - AI suggests expense categories
- **Spending insights** - AI analyzes your spending patterns  
- **Google Gemini integration** using `gemma-3-27b-it` model

### � **Clean Organization**
- **Dashboard** - Overview stats and recent expenses
- **Expenses** - Complete expense list and management
- **Analytics** - Charts and AI insights
- **Budgets** - Budget tracking with progress bars

### � **Core Functionality**
- Add/edit/delete expenses
- Budget management with alerts
- Interactive donut charts
- Real-time statistics
- Mobile-responsive design

## 🚀 Quick Setup

### 1. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your Google AI API key to .env
python server.py
```

### 2. **Frontend**
Open `frontend/public/index.html` in your browser or serve it:
```bash
cd frontend/public
python -m http.server 3000
```

## 🎯 Usage

### **Adding Expenses**
1. Go to **Expenses** tab
2. Click "Add Expense" 
3. Use **AI** button for smart categorization
4. Save and track

### **Budget Management** 
1. Go to **Budgets** tab
2. Set budget limits per category
3. Monitor spending with progress bars
4. Get alerts when approaching limits

### **Analytics & Insights**
1. **Analytics** tab shows spending breakdown
2. Interactive donut chart by category
3. Click "Get AI Insights" for personalized analysis

## 🛠️ Tech Stack

- **Backend**: Flask + Python
- **Frontend**: Vanilla JavaScript + CSS
- **AI**: Google Gemini (`gemma-3-27b-it`)  
- **Charts**: Chart.js
- **Storage**: In-memory (easily expandable to database)

## � API Endpoints

```
GET    /api/expenses          # Get all expenses
POST   /api/expenses          # Add new expense  
DELETE /api/expenses/{id}     # Delete expense

GET    /api/expenses/categorize # AI category suggestion
POST   /api/expenses/insights   # AI spending insights

GET    /api/budgets           # Get budgets
POST   /api/budgets           # Add budget
POST   /api/budget/alerts     # Budget alerts
```

## 🎨 Design Philosophy

- **Minimalism** - Only essential features, no clutter
- **Dark Theme** - Easy on eyes, modern look
- **Clean Separation** - Each function in dedicated tab
- **High Functionality** - Powerful features in simple interface
- **No Bloat** - Core expense tracking without unnecessary extras

## 🚀 Deployment

### **Vercel**
```bash
vercel
# Set GOOGLE_API_KEY in environment variables
```

### **Local Development**
- Backend: `python backend/server.py` 
- Frontend: Serve `frontend/public/` directory

## 🔑 Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_google_ai_api_key

# Optional  
FLASK_ENV=development
```

## 🎯 Perfect For

- Personal expense tracking
- Budget monitoring  
- AI-powered spending insights
- Clean, distraction-free interface
- Mobile and desktop use

---

**Simple. Dark. Powerful. No nonsense expense tracking with AI.**