# Smart Expense Tracker - AI-Powered Financial Management

A modern, AI-powered expense tracking application with intelligent categorization, predictive analytics, and personalized financial insights. Built with a mobile-first design and professional UI inspired by modern banking applications.

![Smart Expense Tracker](https://img.shields.io/badge/Version-2.0-blue.svg)
![AI Powered](https://img.shields.io/badge/AI-Powered-green.svg)
![Mobile First](https://img.shields.io/badge/Design-Mobile--First-orange.svg)

## 🌟 Key Features

### 🤖 AI-Powered Intelligence
- **Smart Categorization**: Automatically categorizes expenses using Google Gemini AI
- **Predictive Analytics**: AI predicts monthly spending based on current patterns
- **Financial Health Score**: Real-time assessment of spending habits
- **Personalized Insights**: Tailored recommendations for better financial management
- **Savings Advice**: AI-generated suggestions for optimizing spending and increasing savings

### 💳 Core Functionality
- **Expense Tracking**: Add, edit, and delete expenses with ease
- **Budget Management**: Set monthly budgets and track progress
- **Salary Integration**: Input monthly income for comprehensive financial overview
- **Category Breakdown**: Visual representation of spending across categories
- **Real-time Updates**: Live dashboard with current spending metrics

### 🎨 Modern UI/UX
- **Professional Icons**: Font Awesome icons for a polished look
- **Dark Theme**: Easy on the eyes with modern dark design
- **Mobile-First**: Optimized for mobile devices with responsive design
- **Smooth Animations**: Fluid transitions and hover effects
- **Intuitive Navigation**: Bottom navigation for easy access

### 🎓 User Onboarding
- **5-Step Guided Tour**: Comprehensive introduction for new users
- **Feature Explanations**: Interactive walkthrough of all capabilities
- **Setup Assistance**: Guided budget and salary setup
- **Help System**: Accessible help through the header question mark icon

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+ (optional, for development)
- Google Gemini API key (for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-expense-tracker
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the backend directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   FLASK_DEBUG=False
   PORT=8001
   FRONTEND_URL=http://localhost:3000
   ```

4. **Start the Application**
   ```bash
   python server.py
   ```

5. **Access the App**
   Open your browser and navigate to `http://localhost:8001`

### Getting Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file

## 📱 How to Use

### First Time Setup

1. **Launch the App**: Open the application in your browser
2. **Onboarding Tour**: Follow the 5-step guided tour to learn about features
3. **Set Monthly Salary**: Click the wallet icon in the header to input your income
4. **Set Monthly Budget**: Use the budget card or onboarding to set spending limits

### Adding Expenses

1. **Click "Add Expense"** button or the floating "+" button
2. **Enter Details**: 
   - Expense name (e.g., "Coffee at Starbucks")
   - Amount in ₹
   - Date of expense
   - Optional description
3. **Category Selection**: 
   - Let AI automatically categorize
   - Or manually select from dropdown
   - Use "AI" button for smart suggestions
4. **Save**: Click "Add Expense" to save

### Dashboard Overview

#### Financial Cards
- **Monthly Budget Card**: Shows budget progress with visual indicator
- **This Month Card**: Displays current month's spending and statistics
- **AI Prediction Card**: Shows predicted monthly spending with confidence score

#### Quick Actions
- **Add Expense**: Quick access to expense form
- **AI Analysis**: Get detailed financial health analysis
- **Savings Tips**: Receive personalized savings recommendations

#### Category Breakdown
- Visual representation of spending by category
- Percentage and amount for each category
- Professional icons for easy identification

#### Recent Expenses
- List of recent transactions
- Category icons and metadata
- Quick delete functionality

### AI Features

#### Smart Categorization
- Analyzes expense name and amount
- Uses context-aware AI for accurate categorization
- Supports 14 different categories with professional icons

#### Predictive Analytics
- Analyzes spending patterns
- Predicts end-of-month spending
- Provides confidence score for predictions
- Updates in real-time as expenses are added

#### Financial Health Score
- Comprehensive analysis of spending habits
- Score from 0-100 based on multiple factors
- Personalized recommendations for improvement

#### Savings Advice
- Analyzes income vs. spending
- Suggests optimal budget allocations
- Recommends emergency fund targets
- Provides actionable savings strategies

### Navigation

#### Bottom Navigation
- **Dashboard**: Overview of finances
- **Expenses**: Detailed expense list
- **Analytics**: AI-powered insights
- **Profile**: User information and statistics

#### Header Actions
- **Wallet Icon**: Set/update monthly salary
- **Question Mark**: Open onboarding guide anytime
- **Settings Icon**: Future settings access

## 🏗️ Architecture

### Frontend
- **Pure JavaScript**: No external frameworks for fast loading
- **Modern CSS**: CSS Grid, Flexbox, and custom properties
- **Font Awesome**: Professional icon library
- **Responsive Design**: Mobile-first approach

### Backend
- **Flask**: Lightweight Python web framework
- **Google Gemini AI**: Advanced AI for expense analysis
- **JSON Storage**: Simple file-based data persistence
- **RESTful API**: Clean API design for frontend communication

### File Structure
```
smart-expense-tracker/
├── backend/
│   ├── server.py              # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   └── data/                  # JSON data storage
├── frontend/
│   └── public/
│       ├── index.html         # Main HTML file
│       ├── styles.css         # Comprehensive styling
│       └── scripts.js         # Application logic
├── vercel.json               # Deployment configuration
└── README.md                 # This file
```

## 🎨 Design System

### Colors
- **Primary**: Modern blue gradient (#667eea to #764ba2)
- **Success**: Green (#10b981)
- **Warning**: Orange (#f59e0b)
- **Danger**: Red (#ef4444)
- **Background**: Dark theme (#0a0a0a, #1e1e1e)

### Typography
- **Font**: Inter (Google Fonts)
- **Hierarchy**: 6 different font sizes
- **Weight**: 300-700 font weights

### Spacing
- **Consistent**: 8px grid system
- **Responsive**: Adapts to screen size
- **Logical**: Semantic spacing names

### Icons
- **Font Awesome 6**: Professional icon library
- **Consistent**: Same style across the app
- **Semantic**: Icons match their function

## 🔧 API Endpoints

### Expenses
- `GET /api/expenses` - Get all expenses
- `POST /api/expenses` - Add new expense
- `DELETE /api/expenses/{id}` - Delete expense
- `POST /api/expenses/categorize` - AI categorization
- `POST /api/expenses/analyze` - Get AI analysis
- `POST /api/expenses/predict-month` - Get spending prediction

### Budget & Salary
- `GET /api/budgets` - Get budget information
- `POST /api/budgets` - Set monthly budget
- `GET /api/salary` - Get salary information
- `POST /api/salary` - Set monthly salary

### AI Features
- `POST /api/savings/allocate` - Get savings advice
- `GET /api/financial-health` - Get financial health score
- `GET /api/dashboard` - Get dashboard data

## 🚀 Deployment

### Vercel (Recommended)
1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

3. **Set Environment Variables**
   - Add `GOOGLE_API_KEY` in Vercel dashboard

### Manual Deployment
1. **Prepare Environment**
   - Set production environment variables
   - Ensure all dependencies are installed

2. **Run Production Server**
   ```bash
   python server.py
   ```

## 🔒 Security Features

- **Input Validation**: All user inputs are validated
- **Error Handling**: Graceful error handling throughout
- **File Locking**: Prevents data corruption during concurrent access
- **CORS Configuration**: Restricted to specific origins
- **API Rate Limiting**: Built-in protection against abuse

## 📊 Data Management

### Storage
- **File-based**: Simple JSON file storage
- **Atomic Operations**: File locking ensures data integrity
- **Backup**: Easy to backup and restore

### Categories
The app supports 14 expense categories:
- 🍽️ Food & Dining
- 🚗 Transportation
- 📋 Bills & Utilities
- 🎬 Entertainment
- 🛍️ Shopping
- 🛒 Groceries
- 💊 Healthcare
- 🎓 Education
- ✈️ Travel
- 🧴 Personal Care
- 📈 Investment
- 🛡️ Insurance
- 🏠 Rent
- 📦 Other

## 🎯 Future Enhancements

- [ ] Multiple currency support
- [ ] Export data to CSV/PDF
- [ ] Recurring expense templates
- [ ] Bill reminders and notifications
- [ ] Advanced analytics and charts
- [ ] Multi-user support
- [ ] Bank account integration
- [ ] Receipt photo scanning
- [ ] Expense sharing and splitting
- [ ] Investment tracking

## 🐛 Troubleshooting

### Common Issues

**AI Features Not Working**
- Ensure `GOOGLE_API_KEY` is set correctly
- Check API key permissions in Google Console
- Verify internet connection

**Data Not Persisting**
- Check file permissions in `backend/data/` directory
- Ensure sufficient disk space
- Verify no other instances are running

**UI Not Loading**
- Clear browser cache
- Check developer console for errors
- Ensure all static files are accessible

### Performance Tips

- **Clear Data**: Periodically backup and clear old data
- **Browser**: Use modern browsers for best performance
- **Network**: Ensure stable internet for AI features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## � License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for intelligent expense categorization
- **Font Awesome** for professional icons
- **Inter Font** for beautiful typography
- **Flask Community** for the excellent web framework

## � Support

For support, feature requests, or bug reports:
- Create an issue in the repository
- Check the troubleshooting section
- Review the onboarding guide in the app

---

**Built with ❤️ for better financial management**