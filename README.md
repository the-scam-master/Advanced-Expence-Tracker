Smart Expense Tracker
A mobile-responsive expense tracking application with budgeting and visualizations.
Features

📊 Expense and income tracking with categories
📈 Budget management with progress tracking
📅 Transaction history with calendar view
💡 Spending visualizations via pie chart
💰 Balance and statistics tracking
📱 Mobile-responsive design
⚙️ User settings (name, data export/import, reset)

Deployment on Vercel
Prerequisites

Vercel Account: Sign up at vercel.com

Setup

Fork/Clone this repository

Deploy:
vercel --prod



Local Development

Install dependencies:
pip install -r requirements.txt


Run backend:
cd backend
python server.py


Serve frontend:
cd frontend/public
python -m http.server 8000



API Endpoints

GET /api - Root endpoint
GET /api/health - Health check

Troubleshooting
Common Issues

CORS Errors: The backend has CORS configured for all origins
API Timeout: Vercel has a 10-second timeout limit for serverless functions
Chart.js Not Loading: Ensure chart.min.js is included in frontend/public

Notes

All data is stored locally in the browser using localStorage.
The backend provides basic health checks but is not used for data storage.
Monthly data resets automatically, storing the previous month's data for export.
