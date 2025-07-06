import React, { useState } from 'react';
import { X, DollarSign, Calendar, Tag, FileText, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { expenseService } from '../services/expenseService';

const ExpenseForm = ({ onAddExpense, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    amount: '',
    date: new Date().toISOString().substring(0, 10),
    category: '',
    description: ''
  });
  const [loading, setLoading] = useState(false);
  const [suggestedCategory, setSuggestedCategory] = useState('');

  const categories = [
    'Food', 'Transportation', 'Bills', 'Entertainment', 'Housing',
    'Groceries', 'Health', 'Education', 'Personal Care', 'Savings',
    'Travel', 'Other'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const suggestCategory = async () => {
    if (!formData.name || !formData.amount) {
      toast.error('Please enter expense name and amount first');
      return;
    }

    try {
      setLoading(true);
      const suggestion = await expenseService.suggestCategory(formData.name, parseFloat(formData.amount));
      setSuggestedCategory(suggestion.suggested_category);
      setFormData(prev => ({
        ...prev,
        category: suggestion.suggested_category
      }));
      toast.success(`Category suggested: ${suggestion.suggested_category}`);
    } catch (error) {
      console.error('Error suggesting category:', error);
      toast.error('Failed to suggest category');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.amount || !formData.category) {
      toast.error('Please fill in all required fields');
      return;
    }

    const expense = {
      ...formData,
      amount: parseFloat(formData.amount)
    };

    onAddExpense(expense);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
      <div className="card max-w-md w-full p-6 animate-fade-in">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Add New Expense</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Expense Name */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <FileText className="inline w-4 h-4 mr-1" />
              Expense Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="input-dark w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Coffee, Groceries, Gas"
              required
            />
          </div>

          {/* Amount */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <DollarSign className="inline w-4 h-4 mr-1" />
              Amount *
            </label>
            <input
              type="number"
              name="amount"
              value={formData.amount}
              onChange={handleInputChange}
              className="input-dark w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0.00"
              step="0.01"
              min="0"
              required
            />
          </div>

          {/* Date */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <Calendar className="inline w-4 h-4 mr-1" />
              Date *
            </label>
            <input
              type="date"
              name="date"
              value={formData.date}
              onChange={handleInputChange}
              className="input-dark w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              <Tag className="inline w-4 h-4 mr-1" />
              Category *
            </label>
            <div className="flex gap-2">
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="input-dark flex-1 px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select category</option>
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={suggestCategory}
                disabled={loading}
                className="btn-secondary px-3 py-2 rounded-lg flex items-center gap-1 text-sm"
              >
                <Sparkles className="w-4 h-4" />
                AI
              </button>
            </div>
            {suggestedCategory && (
              <p className="text-xs text-blue-400 mt-1">
                AI suggested: {suggestedCategory}
              </p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Description (optional)
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              className="input-dark w-full px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add a note about this expense..."
              rows="3"
            />
          </div>

          {/* Submit Button */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1 py-3 rounded-lg text-white font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1 py-3 rounded-lg text-white font-medium disabled:opacity-50"
            >
              {loading ? 'Adding...' : 'Add Expense'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ExpenseForm;