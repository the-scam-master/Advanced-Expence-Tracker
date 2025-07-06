import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL + '/api';

class ExpenseService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // AI-powered expense prediction
  async predictNextMonth(expenses) {
    try {
      const response = await this.api.post('/expenses/predict', { expenses });
      return response.data;
    } catch (error) {
      console.error('Error predicting expenses:', error);
      throw error;
    }
  }

  // AI-powered category suggestion
  async suggestCategory(expenseName, amount) {
    try {
      const response = await this.api.get('/expenses/categorize', {
        params: { expense_name: expenseName, amount }
      });
      return response.data;
    } catch (error) {
      console.error('Error suggesting category:', error);
      throw error;
    }
  }

  // Get AI insights about spending patterns
  async getAIInsights(expenses) {
    try {
      const response = await this.api.post('/expenses/insights', { expenses });
      return response.data;
    } catch (error) {
      console.error('Error getting AI insights:', error);
      throw error;
    }
  }

  // Get comprehensive analytics
  async getAnalytics(expenses) {
    try {
      const response = await this.api.post('/expenses/analytics', { expenses });
      return response.data;
    } catch (error) {
      console.error('Error getting analytics:', error);
      throw error;
    }
  }

  // Get budget alerts
  async getBudgetAlerts(expenses, budgets) {
    try {
      const response = await this.api.post('/budget/alerts', { expenses, budgets });
      return response.data;
    } catch (error) {
      console.error('Error getting budget alerts:', error);
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
}

export const expenseService = new ExpenseService();