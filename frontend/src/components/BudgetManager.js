import React, { useState, useEffect } from 'react';
import { Target, Plus, Trash2, AlertCircle, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const BudgetManager = ({ budgets, onBudgetChange, expenses }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newBudget, setNewBudget] = useState({
    category: '',
    amount: '',
    period: 'monthly'
  });

  const categories = [
    'Food', 'Transportation', 'Bills', 'Entertainment', 'Housing',
    'Groceries', 'Health', 'Education', 'Personal Care', 'Savings',
    'Travel', 'Other'
  ];

  const getCurrentMonthExpenses = (category) => {
    const currentMonth = new Date().toISOString().substring(0, 7);
    return expenses
      .filter(expense => 
        expense.date.startsWith(currentMonth) && expense.category === category
      )
      .reduce((sum, expense) => sum + expense.amount, 0);
  };

  const getBudgetStatus = (budget) => {
    const spent = getCurrentMonthExpenses(budget.category);
    const percentage = (spent / budget.amount) * 100;
    
    if (percentage >= 100) return { status: 'exceeded', color: 'text-red-400', bgColor: 'bg-red-900/20' };
    if (percentage >= 80) return { status: 'warning', color: 'text-yellow-400', bgColor: 'bg-yellow-900/20' };
    if (percentage >= 60) return { status: 'caution', color: 'text-orange-400', bgColor: 'bg-orange-900/20' };
    return { status: 'good', color: 'text-green-400', bgColor: 'bg-green-900/20' };
  };

  const addBudget = () => {
    if (!newBudget.category || !newBudget.amount) {
      toast.error('Please fill in all fields');
      return;
    }

    const existingBudget = budgets.find(b => b.category === newBudget.category);
    if (existingBudget) {
      toast.error('Budget already exists for this category');
      return;
    }

    const budget = {
      ...newBudget,
      amount: parseFloat(newBudget.amount),
      id: Date.now().toString()
    };

    onBudgetChange([...budgets, budget]);
    setNewBudget({ category: '', amount: '', period: 'monthly' });
    setShowAddForm(false);
    toast.success('Budget added successfully!');
  };

  const removeBudget = (budgetId) => {
    onBudgetChange(budgets.filter(b => b.id !== budgetId));
    toast.success('Budget removed successfully!');
  };

  const getProgressBarWidth = (budget) => {
    const spent = getCurrentMonthExpenses(budget.category);
    const percentage = (spent / budget.amount) * 100;
    return Math.min(percentage, 100);
  };

  return (
    <div className="card p-6 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Target className="w-6 h-6" />
          Budget Manager
        </h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="btn-primary px-4 py-2 rounded-lg flex items-center gap-2 text-white font-medium"
        >
          <Plus className="w-4 h-4" />
          Add Budget
        </button>
      </div>

      {showAddForm && (
        <div className="glass p-4 rounded-lg mb-6">
          <h3 className="text-lg font-semibold text-white mb-4">Add New Budget</h3>
          <div className="space-y-3">
            <select
              value={newBudget.category}
              onChange={(e) => setNewBudget(prev => ({ ...prev, category: e.target.value }))}
              className="input-dark w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Category</option>
              {categories.filter(cat => !budgets.some(b => b.category === cat)).map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
            
            <input
              type="number"
              value={newBudget.amount}
              onChange={(e) => setNewBudget(prev => ({ ...prev, amount: e.target.value }))}
              className="input-dark w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Budget amount"
              step="0.01"
              min="0"
            />
            
            <select
              value={newBudget.period}
              onChange={(e) => setNewBudget(prev => ({ ...prev, period: e.target.value }))}
              className="input-dark w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="monthly">Monthly</option>
              <option value="weekly">Weekly</option>
              <option value="yearly">Yearly</option>
            </select>
            
            <div className="flex gap-2">
              <button
                onClick={() => setShowAddForm(false)}
                className="btn-secondary flex-1 py-2 rounded-lg text-white font-medium"
              >
                Cancel
              </button>
              <button
                onClick={addBudget}
                className="btn-primary flex-1 py-2 rounded-lg text-white font-medium"
              >
                Add Budget
              </button>
            </div>
          </div>
        </div>
      )}

      {budgets.length === 0 ? (
        <div className="text-center py-12">
          <Target className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400 text-lg">No budgets set</p>
          <p className="text-gray-500 text-sm mt-2">Create budgets to track your spending</p>
        </div>
      ) : (
        <div className="space-y-4">
          {budgets.map(budget => {
            const spent = getCurrentMonthExpenses(budget.category);
            const remaining = budget.amount - spent;
            const percentage = (spent / budget.amount) * 100;
            const status = getBudgetStatus(budget);
            
            return (
              <div key={budget.id} className={`glass p-4 rounded-lg ${status.bgColor}`}>
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-white text-lg">{budget.category}</h3>
                    <p className="text-sm text-gray-400 capitalize">{budget.period} budget</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right">
                      <p className="text-white font-semibold">${spent.toFixed(2)} / ${budget.amount.toFixed(2)}</p>
                      <p className={`text-sm ${status.color}`}>
                        {remaining >= 0 ? `$${remaining.toFixed(2)} remaining` : `$${Math.abs(remaining).toFixed(2)} over`}
                      </p>
                    </div>
                    <button
                      onClick={() => removeBudget(budget.id)}
                      className="text-gray-400 hover:text-red-400 transition-colors p-1 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                <div className="mb-3">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400">Progress</span>
                    <span className={status.color}>{percentage.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        percentage >= 100 ? 'bg-red-500' : 
                        percentage >= 80 ? 'bg-yellow-500' : 
                        percentage >= 60 ? 'bg-orange-500' : 
                        'bg-green-500'
                      }`}
                      style={{ width: `${getProgressBarWidth(budget)}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 text-sm">
                  {status.status === 'exceeded' ? (
                    <AlertCircle className="w-4 h-4 text-red-400" />
                  ) : (
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  )}
                  <span className={status.color}>
                    {status.status === 'exceeded' ? 'Budget exceeded!' :
                     status.status === 'warning' ? 'Close to budget limit' :
                     status.status === 'caution' ? 'Approaching budget limit' :
                     'Within budget'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default BudgetManager;