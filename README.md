# � Smart Expense Tracker

A beautiful, modern AI-powered expense tracking application with stunning UI design and intelligent insights.

![Smart Expense Tracker](https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&h=400&fit=crop)

## ✨ Features

### 🎨 Beautiful Modern UI
- **Clean, minimalist design** inspired by modern fintech apps
- **Mobile-first responsive** layout that works perfectly on all devices
- **Smooth animations** and transitions for delightful user experience
- **Card-based interface** with beautiful gradients and shadows
- **Professional typography** using Inter font family

### 🤖 AI-Powered Intelligence
- **Smart categorization** - AI suggests expense categories automatically
- **Intelligent insights** - Get personalized spending analysis
- **Expense predictions** - AI forecasts your future spending patterns
- **Natural language processing** for expense descriptions

### 📊 Comprehensive Analytics
- **Real-time dashboard** with expense overview
- **Interactive charts** showing spending breakdown
- **Category-wise analysis** with visual representations
- **Monthly trends** and spending patterns
- **Budget tracking** with smart alerts

### 🚀 Modern Technology Stack
- **Backend**: Flask (Python) with RESTful API design
- **Frontend**: Modern vanilla JavaScript with ES6+ features
- **AI Integration**: Google Gemini AI (gemma-3-27b-it model)
- **Charts**: Chart.js for beautiful data visualizations
- **Styling**: Modern CSS with custom properties and flexbox/grid

## 🖼️ Screenshots

The app features a beautiful, clean interface with:
- **Dashboard**: Overview of expenses with beautiful cards
- **Transaction List**: Clean list of recent expenses
- **Sidebar Statistics**: Real-time analytics with donut charts
- **Smart Modals**: Modern popup forms for adding expenses
- **AI Integration**: Intelligent category suggestions

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google AI API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-expense-tracker.git
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
   # Edit .env and add your Google AI API key
   ```

4. **Run the Flask backend**
   ```bash
   python server.py
   ```
   The backend will start at `http://localhost:8001`

5. **Serve the frontend**
   Open `frontend/public/index.html` in your browser or use a local server:
   ```bash
   cd frontend/public
   python -m http.server 3000
   ```
   Visit `http://localhost:3000`

## 🎯 Usage

### Adding Expenses
1. Click the **floating + button** or press the "Add Expense" button
2. Fill in the expense details
3. Use **AI Suggest** to automatically categorize your expense
4. Click "Add Expense" to save

### AI Features
- **Smart Categorization**: The AI analyzes your expense name and suggests the most appropriate category
- **Spending Insights**: Get personalized insights about your spending patterns
- **Predictions**: AI forecasts your future expenses based on historical data

### Analytics Dashboard
- View your **total expenses** and **monthly spending**
- Explore **category breakdowns** with interactive charts
- Track **spending trends** over time
- Monitor **budget alerts** and recommendations

## 🛠️ API Endpoints

### Expenses
- `GET /api/expenses` - Get all expenses
- `POST /api/expenses` - Add new expense
- `DELETE /api/expenses/{id}` - Delete expense

### AI Features
- `GET /api/expenses/categorize` - Get AI category suggestion
- `POST /api/expenses/insights` - Get AI spending insights
- `POST /api/expenses/predict` - Get AI expense predictions

### Analytics
- `POST /api/expenses/analytics` - Get expense analytics
- `POST /api/budget/alerts` - Get budget alerts

## 🎨 Design System

### Color Palette
- **Primary**: #007AFF (iOS Blue)
- **Secondary**: #5856D6 (Purple)
- **Success**: #30D158 (Green)
- **Warning**: #FF9F0A (Orange)
- **Danger**: #FF453A (Red)

### Typography
- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700, 800

### Components
- Modern cards with subtle shadows
- Smooth transitions and hover effects
- Consistent spacing using CSS custom properties
- Mobile-first responsive design

## 🧠 AI Integration

The app uses Google's Gemini AI model (`gemma-3-27b-it`) for:

1. **Expense Categorization**
   - Analyzes expense names and amounts
   - Suggests the most appropriate category
   - Learns from patterns in your data

2. **Spending Insights**
   - Provides personalized analysis
   - Identifies spending patterns
   - Offers actionable recommendations

3. **Expense Prediction**
   - Forecasts future expenses
   - Predicts category-wise spending
   - Helps with budget planning

## 🚀 Deployment

### Vercel (Recommended)
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the project root
3. Add your `GOOGLE_API_KEY` in Vercel environment variables
4. Deploy!

### Manual Deployment
1. **Backend**: Deploy Flask app to any Python hosting service
2. **Frontend**: Deploy static files to any CDN or static hosting
3. **Environment**: Set `GOOGLE_API_KEY` in production environment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Design Inspiration**: Modern fintech and banking apps
- **AI Provider**: Google Gemini AI
- **Icons**: Emojis for clean, universal design
- **Charts**: Chart.js for beautiful data visualization

## 🔮 Future Enhancements

- [ ] **Receipt scanning** with OCR technology
- [ ] **Bank integration** for automatic expense import
- [ ] **Multi-currency support** for international users
- [ ] **Collaborative budgets** for families and teams
- [ ] **Advanced analytics** with machine learning insights
- [ ] **Mobile apps** for iOS and Android
- [ ] **Export capabilities** (PDF, Excel, CSV)
- [ ] **Recurring expense management**
- [ ] **Investment tracking** integration
- [ ] **Smart notifications** and reminders

---

**Built with ❤️ using modern web technologies and AI**