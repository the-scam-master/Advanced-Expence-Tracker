import React from 'react';
import { Trash2, Calendar, DollarSign, Tag } from 'lucide-react';
import { format } from 'date-fns';

const ExpenseList = ({ expenses, selectedMonth, onMonthChange, onDeleteExpense }) => {
  const getCategoryIcon = (category) => {
    const icons = {
      'Food': '🍽️',
      'Transportation': '🚗',
      'Bills': '📋',
      'Entertainment': '🎬',
      'Housing': '🏠',
      'Groceries': '🛒',
      'Health': '💊',
      'Education': '📚',
      'Personal Care': '🧴',
      'Savings': '💰',
      'Travel': '✈️',
      'Other': '📦'
    };
    return icons[category] || '📦';
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Food': 'text-yellow-400',
      'Transportation': 'text-blue-400',
      'Bills': 'text-red-400',
      'Entertainment': 'text-pink-400',
      'Housing': 'text-green-400',
      'Groceries': 'text-purple-400',
      'Health': 'text-cyan-400',
      'Education': 'text-orange-400',
      'Personal Care': 'text-lime-400',
      'Savings': 'text-emerald-400',
      'Travel': 'text-indigo-400',
      'Other': 'text-gray-400'
    };
    return colors[category] || 'text-gray-400';
  };

  const filteredExpenses = expenses.filter(expense => 
    expense.date.startsWith(selectedMonth)
  );

  const sortedExpenses = filteredExpenses.sort((a, b) => 
    new Date(b.date) - new Date(a.date)
  );

  const getAvailableMonths = () => {
    const months = [...new Set(expenses.map(expense => expense.date.substring(0, 7)))];
    const currentMonth = new Date().toISOString().substring(0, 7);
    
    if (!months.includes(currentMonth)) {
      months.push(currentMonth);
    }
    
    return months.sort((a, b) => b.localeCompare(a));
  };

  return (
    <div className="card p-6 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Calendar className="w-6 h-6" />
          Expense History
        </h2>
        <select
          value={selectedMonth}
          onChange={(e) => onMonthChange(e.target.value)}
          className="input-dark px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {getAvailableMonths().map(month => (
            <option key={month} value={month}>
              {format(new Date(month + '-01'), 'MMMM yyyy')}
            </option>
          ))}
        </select>
      </div>

      {sortedExpenses.length === 0 ? (
        <div className="text-center py-12">
          <DollarSign className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400 text-lg">No expenses found for this month</p>
          <p className="text-gray-500 text-sm mt-2">Start by adding your first expense</p>
        </div>
      ) : (
        <div className="space-y-3">
          {sortedExpenses.map(expense => (
            <div
              key={expense.id}
              className="glass p-4 rounded-lg hover:bg-gray-700/50 transition-all duration-200 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1">
                  <div className="text-2xl">
                    {getCategoryIcon(expense.category)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-white text-lg truncate">
                      {expense.name}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-400 mt-1">
                      <span className={`flex items-center gap-1 ${getCategoryColor(expense.category)}`}>
                        <Tag className="w-3 h-3" />
                        {expense.category}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {format(new Date(expense.date), 'MMM dd')}
                      </span>
                    </div>
                    {expense.description && (
                      <p className="text-sm text-gray-500 mt-1 truncate">
                        {expense.description}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-2xl font-bold text-white">
                      ${expense.amount.toFixed(2)}
                    </p>
                  </div>
                  <button
                    onClick={() => onDeleteExpense(expense.id)}
                    className="text-gray-400 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100 p-2 rounded-lg hover:bg-red-900/20"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {sortedExpenses.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-700">
          <div className="flex justify-between items-center">
            <span className="text-gray-400">Total for {format(new Date(selectedMonth + '-01'), 'MMMM yyyy')}</span>
            <span className="text-2xl font-bold text-white">
              ${sortedExpenses.reduce((sum, expense) => sum + expense.amount, 0).toFixed(2)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpenseList;