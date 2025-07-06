import React, { useState, useEffect } from 'react';
import { 
  PlusCircle, 
  TrendingUp, 
  DollarSign, 
  Calendar,
  PieChart,
  AlertTriangle,
  Brain,
  Download,
  Upload,
  Target,
  Zap
} from 'lucide-react';
import toast from 'react-hot-toast';
import ExpenseForm from './ExpenseForm';
import ExpenseList from './ExpenseList';
import ExpenseChart from './ExpenseChart';
import BudgetManager from './BudgetManager';
import AIInsights from './AIInsights';
import Analytics from './Analytics';
import { expenseService } from '../services/expenseService';

const Dashboard = () => {
  const [expenses, setExpenses] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().substring(0, 7));
  const [showAddForm, setShowAddForm] = useState(false);
  const [aiInsights, setAiInsights] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [budgetAlerts, setBudgetAlerts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadExpenses();
    loadBudgets();
  }, []);

  useEffect(() => {
    if (expenses.length > 0) {
      generateAIInsights();
      generateAnalytics();
      checkBudgetAlerts();
    }
  }, [expenses, budgets]);

  const loadExpenses = () => {
    const savedExpenses = localStorage.getItem('expenses');
    if (savedExpenses) {
      setExpenses(JSON.parse(savedExpenses));
    }
  };

  const loadBudgets = () => {
    const savedBudgets = localStorage.getItem('budgets');
    if (savedBudgets) {
      setBudgets(JSON.parse(savedBudgets));
    }
  };

  const saveExpenses = (newExpenses) => {
    localStorage.setItem('expenses', JSON.stringify(newExpenses));
    setExpenses(newExpenses);
  };

  const saveBudgets = (newBudgets) => {
    localStorage.setItem('budgets', JSON.stringify(newBudgets));
    setBudgets(newBudgets);
  };

  const addExpense = (expense) => {
    const newExpense = {
      ...expense,
      id: Date.now().toString(),
      date: expense.date || new Date().toISOString().substring(0, 10)
    };
    
    const newExpenses = [newExpense, ...expenses];
    saveExpenses(newExpenses);
    setShowAddForm(false);
    toast.success('Expense added successfully!');
  };

  const deleteExpense = (id) => {
    const newExpenses = expenses.filter(expense => expense.id !== id);
    saveExpenses(newExpenses);
    toast.success('Expense deleted successfully!');
  };

  const generateAIInsights = async () => {
    if (expenses.length === 0) return;
    
    try {
      setLoading(true);
      const insights = await expenseService.getAIInsights(expenses);
      setAiInsights(insights);
    } catch (error) {
      console.error('Error generating AI insights:', error);
      toast.error('Failed to generate AI insights');
    } finally {
      setLoading(false);
    }
  };

  const generateAnalytics = async () => {
    if (expenses.length === 0) return;
    
    try {
      const analyticsData = await expenseService.getAnalytics(expenses);
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Error generating analytics:', error);
    }
  };

  const checkBudgetAlerts = async () => {
    if (expenses.length === 0 || budgets.length === 0) return;
    
    try {
      const alerts = await expenseService.getBudgetAlerts(expenses, budgets);
      setBudgetAlerts(alerts);
    } catch (error) {
      console.error('Error checking budget alerts:', error);
    }
  };

  const getMonthlyTotal = () => {
    const monthlyExpenses = expenses.filter(expense => 
      expense.date.startsWith(selectedMonth)
    );
    return monthlyExpenses.reduce((sum, expense) => sum + expense.amount, 0);
  };

  const exportData = () => {
    const dataStr = JSON.stringify({ expenses, budgets }, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `expense-data-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    toast.success('Data exported successfully!');
  };

  const importData = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        if (data.expenses) {
          saveExpenses(data.expenses);
        }
        if (data.budgets) {
          saveBudgets(data.budgets);
        }
        toast.success('Data imported successfully!');
      } catch (error) {
        toast.error('Invalid file format');
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold gradient-text mb-4">
            💰 Smart Expense Tracker
          </h1>
          <p className="text-xl text-gray-400">
            Track, Analyze, and Optimize Your Spending with AI
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="card p-6 animate-fade-in">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Total Expenses</p>
                <p className="text-2xl font-bold text-white">
                  ${expenses.reduce((sum, expense) => sum + expense.amount, 0).toFixed(2)}
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="card p-6 animate-fade-in">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">This Month</p>
                <p className="text-2xl font-bold text-white">
                  ${getMonthlyTotal().toFixed(2)}
                </p>
              </div>
              <Calendar className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="card p-6 animate-fade-in">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">Categories</p>
                <p className="text-2xl font-bold text-white">
                  {new Set(expenses.map(e => e.category)).size}
                </p>
              </div>
              <PieChart className="w-8 h-8 text-purple-500" />
            </div>
          </div>

          <div className="card p-6 animate-fade-in">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">AI Insights</p>
                <p className="text-2xl font-bold text-white">
                  {aiInsights.length}
                </p>
              </div>
              <Brain className="w-8 h-8 text-pink-500" />
            </div>
          </div>
        </div>

        {/* Budget Alerts */}
        {budgetAlerts.length > 0 && (
          <div className="mb-8 animate-slide-in">
            <div className="card p-6 border-l-4 border-yellow-500">
              <div className="flex items-center mb-4">
                <AlertTriangle className="w-5 h-5 text-yellow-500 mr-2" />
                <h3 className="text-lg font-semibold text-white">Budget Alerts</h3>
              </div>
              <div className="space-y-3">
                {budgetAlerts.map((alert, index) => (
                  <div key={index} className={`p-3 rounded-lg ${
                    alert.alert_type === 'danger' ? 'bg-red-900/30' : 
                    alert.alert_type === 'warning' ? 'bg-yellow-900/30' : 
                    'bg-blue-900/30'
                  }`}>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-300">{alert.category}</span>
                      <span className="text-sm font-bold text-white">
                        {alert.percentage_used.toFixed(1)}% used
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                      <div 
                        className={`h-2 rounded-full ${
                          alert.alert_type === 'danger' ? 'bg-red-500' : 
                          alert.alert_type === 'warning' ? 'bg-yellow-500' : 
                          'bg-blue-500'
                        }`}
                        style={{ width: `${Math.min(alert.percentage_used, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 mb-8">
          <button 
            onClick={() => setShowAddForm(true)}
            className="btn-primary px-6 py-3 rounded-lg flex items-center gap-2 text-white font-medium"
          >
            <PlusCircle className="w-5 h-5" />
            Add Expense
          </button>
          
          <button 
            onClick={exportData}
            className="btn-secondary px-6 py-3 rounded-lg flex items-center gap-2 text-white font-medium"
          >
            <Download className="w-5 h-5" />
            Export Data
          </button>
          
          <label className="btn-secondary px-6 py-3 rounded-lg flex items-center gap-2 text-white font-medium cursor-pointer">
            <Upload className="w-5 h-5" />
            Import Data
            <input type="file" accept=".json" onChange={importData} className="hidden" />
          </label>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Expense List */}
            <ExpenseList 
              expenses={expenses}
              selectedMonth={selectedMonth}
              onMonthChange={setSelectedMonth}
              onDeleteExpense={deleteExpense}
            />

            {/* Analytics */}
            {analytics && (
              <Analytics analytics={analytics} />
            )}
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* Expense Chart */}
            <ExpenseChart expenses={expenses} selectedMonth={selectedMonth} />

            {/* Budget Manager */}
            <BudgetManager 
              budgets={budgets}
              onBudgetChange={saveBudgets}
              expenses={expenses}
            />

            {/* AI Insights */}
            <AIInsights 
              insights={aiInsights}
              expenses={expenses}
              loading={loading}
              onRefresh={generateAIInsights}
            />
          </div>
        </div>

        {/* Add Expense Modal */}
        {showAddForm && (
          <ExpenseForm 
            onAddExpense={addExpense}
            onClose={() => setShowAddForm(false)}
          />
        )}
      </div>
    </div>
  );
};

export default Dashboard;