# 💰 Smart Expense Tracker

A modern, AI-powered expense tracking application with a beautiful dark theme and intelligent insights. Built with Flask backend and vanilla JavaScript frontend.

![Smart Expense Tracker](https://img.shields.io/badge/Status-Ready%20to%20Use-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow)

## ✨ Features

### � Core Features
- **Expense Tracking**: Add, view, and delete expenses with categories
- **Budget Management**: Set monthly budgets and track spending
- **Visual Analytics**: Beautiful charts and spending breakdowns
- **Dark Theme**: Minimal, modern UI design
- **Responsive Design**: Works on desktop and mobile devices

### 🤖 AI Features
- **Smart Categorization**: AI suggests categories for your expenses
- **Spending Insights**: Get personalized insights about your spending habits
- **Expense Prediction**: AI predicts next month's expenses based on patterns
- **Financial Health Score**: AI-powered assessment of your financial habits

### 📊 Analytics
- **Category Breakdown**: Visual representation of spending by category
- **Monthly Trends**: Track spending patterns over time
- **Budget Alerts**: Get notified when you're close to budget limits
- **Spending Statistics**: Total expenses, average daily spend, and more

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- A modern web browser
- Google AI Studio API key (for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-expense-tracker
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   ```

4. **Start the backend server**
   ```bash
   python server.py
   ```

5. **Open the application**
   - Open your browser and go to `http://localhost:8001`
   - The frontend files are served from `frontend/public/`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Required for AI features
GOOGLE_API_KEY=your_google_api_key_here

# Optional
FLASK_ENV=development
PORT=8001
```

### Getting Google AI API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

> **Note**: AI features will work with fallback rule-based logic if no API key is provided.

## � UI Overview

### Dashboard
- **Stats Cards**: Total balance, monthly spending, budget remaining, AI score
- **Spending Chart**: Interactive donut chart with category breakdown
- **Recent Expenses**: Quick view of latest transactions
- **Quick Actions**: Fast access to add expense, get insights, set budgets

### Expense Management
- **Add Expenses**: Simple form with AI category suggestions
- **View All Expenses**: Comprehensive list with search and filters
- **Categories**: 12 predefined categories with emoji icons
- **Delete Expenses**: Easy expense removal with confirmation

### Analytics
- **Overview Stats**: Total expenses, transaction count, daily averages
- **Category Analysis**: Detailed breakdown by spending category
- **Trends**: Visual representation of spending patterns

### AI Insights
- **Smart Analysis**: AI-powered insights about spending habits
- **Recommendations**: Personalized suggestions for better financial health
- **Predictions**: Future expense forecasting

## 🏗️ Architecture

### Backend (Flask)
- **RESTful API**: Clean API endpoints for all operations
- **AI Integration**: Google Gemini AI for intelligent features
- **Data Storage**: In-memory storage (easily replaceable with database)
- **Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Cross-origin requests for frontend

### Frontend (Vanilla JavaScript)
- **Modern ES6+**: Clean, modern JavaScript without frameworks
- **Responsive Design**: Mobile-first approach with CSS Grid/Flexbox
- **Chart.js Integration**: Beautiful interactive charts
- **Dark Theme**: Carefully designed color palette and typography
- **Progressive Enhancement**: Works without JavaScript for basic features

## � API Endpoints

### Expenses
- `GET /api/expenses` - Get all expenses
- `POST /api/expenses` - Add new expense
- `DELETE /api/expenses/{id}` - Delete expense
- `GET /api/expenses/categorize` - AI category suggestion
- `POST /api/expenses/insights` - Get AI insights
- `POST /api/expenses/predict` - Get AI predictions

### Budgets
- `GET /api/budgets` - Get all budgets
- `POST /api/budgets` - Add new budget

### Analytics
- `GET /api/analytics` - Get spending analytics
- `GET /api/budget/alerts` - Get budget alerts
- `GET /api/health` - API health check

## 🎯 Usage Examples

### Adding an Expense
1. Click the "Add Expense" button or use the quick action
2. Fill in the expense details
3. Use "AI Suggest" for automatic categorization
4. Submit to save

### Setting a Budget
1. Navigate to Budgets or use quick action
2. Select category and set amount
3. Choose budget period (monthly/weekly/yearly)
4. Submit to track spending against budget

### Getting AI Insights
1. Click "AI Insights" from quick actions or navigation
2. View personalized insights about spending patterns
3. Get recommendations for better financial management

## 🌟 Key Technologies

- **Backend**: Flask, Google Generative AI, Python
- **Frontend**: HTML5, CSS3, JavaScript ES6+, Chart.js
- **AI**: Google Gemma 3-27B-IT model
- **Design**: Modern dark theme, responsive layout
- **Icons**: Unicode emojis for simplicity and universality

## � Security Features

- **Input Validation**: Comprehensive validation on both frontend and backend
- **Error Handling**: Graceful error handling without exposing sensitive information
- **CORS Configuration**: Secure cross-origin resource sharing
- **Environment Variables**: Secure storage of API keys and configuration

## 🚧 Future Enhancements

- **Database Integration**: PostgreSQL/MongoDB for persistent storage
- **User Authentication**: Multi-user support with login/signup
- **Export Features**: PDF reports, CSV exports
- **Advanced Analytics**: More detailed charts and insights
- **Notifications**: Email/SMS alerts for budget limits
- **Recurring Expenses**: Support for recurring transactions
- **Mobile App**: React Native or PWA version

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

If you encounter any issues or have questions:

1. Check the console for error messages
2. Ensure your Google API key is correctly configured
3. Verify all dependencies are installed
4. Check that the backend server is running on port 8001

## 📊 Screenshots

The application features a beautiful dark theme with:
- **Modern sidebar navigation**
- **Interactive dashboard with charts**
- **Clean expense entry forms**
- **Responsive design for all screen sizes**
- **AI-powered insights and recommendations**

---

**Built with ❤️ for better financial management**