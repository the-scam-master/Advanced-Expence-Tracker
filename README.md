# Smart Expense Tracker

An AI-powered expense tracking application with smart insights and predictions.

## Features

- 📊 Expense tracking with categories
- 🤖 AI-powered expense categorization
- 💡 Smart spending insights
- 📈 Financial health scoring
- 💰 Savings advice
- 📅 Transaction history with calendar view
- 📱 Mobile-responsive design

## Deployment on Vercel

### Prerequisites

1. **Google AI API Key**: Get a Google Generative AI API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)

### Setup

1. **Fork/Clone this repository**

2. **Set Environment Variables in Vercel**:
   - Go to your Vercel project dashboard
   - Navigate to Settings → Environment Variables
   - Add: `GOOGLE_API_KEY` = your Google AI API key

3. **Deploy**:
   ```bash
   vercel --prod
   ```

### Environment Variables

- `GOOGLE_API_KEY`: Your Google Generative AI API key (required for AI features)

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/test` - Test endpoint
- `GET /api/expenses` - Get all expenses
- `POST /api/expenses` - Add new expense
- `GET /api/expenses/categorize` - AI expense categorization
- `POST /api/ai/comprehensive-analysis` - Get AI insights
- `GET /api/budgets` - Get budgets
- `POST /api/budgets` - Add budget

## Troubleshooting

### AI Features Not Working

1. **Check API Key**: Ensure `GOOGLE_API_KEY` is set correctly in Vercel
2. **Check Logs**: View Vercel function logs for errors
3. **Test Endpoint**: Visit `/api/test` to verify AI categorization works

### Common Issues

- **CORS Errors**: The backend has CORS configured for all origins
- **Model Not Available**: The app will fall back to rule-based categorization if AI models are unavailable
- **API Timeout**: Vercel has a 10-second timeout limit for serverless functions

## Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variable**:
   ```bash
   export GOOGLE_API_KEY=your_api_key_here
   ```

3. **Run backend**:
   ```bash
   cd backend
   python server.py
   ```

4. **Serve frontend**:
   ```bash
   cd frontend/public
   python -m http.server 8000
   ```

## AI Features

The app uses Google's Generative AI for:
- **Expense Categorization**: Automatically suggests categories for expenses
- **Spending Insights**: Provides personalized spending analysis
- **Financial Health Score**: Calculates overall financial health
- **Savings Advice**: Offers actionable savings recommendations
- **Expense Prediction**: Predicts future spending based on patterns

If AI is unavailable, the app provides rule-based fallbacks for all features.