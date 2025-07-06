import React from 'react';
import { Pie, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { PieChart as PieChartIcon } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend);

const ExpenseChart = ({ expenses, selectedMonth }) => {
  const filteredExpenses = expenses.filter(expense => 
    expense.date.startsWith(selectedMonth)
  );

  const categoryData = filteredExpenses.reduce((acc, expense) => {
    acc[expense.category] = (acc[expense.category] || 0) + expense.amount;
    return acc;
  }, {});

  const data = {
    labels: Object.keys(categoryData),
    datasets: [
      {
        data: Object.values(categoryData),
        backgroundColor: [
          '#3B82F6', // Blue
          '#8B5CF6', // Purple
          '#10B981', // Green
          '#F59E0B', // Yellow
          '#EF4444', // Red
          '#EC4899', // Pink
          '#06B6D4', // Cyan
          '#F97316', // Orange
          '#84CC16', // Lime
          '#22C55E', // Emerald
          '#6366F1', // Indigo
          '#6B7280', // Gray
        ],
        borderColor: '#1F2937',
        borderWidth: 2,
        hoverBorderWidth: 3,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#F9FAFB',
          padding: 20,
          usePointStyle: true,
          pointStyle: 'circle',
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        backgroundColor: '#1F2937',
        titleColor: '#F9FAFB',
        bodyColor: '#F9FAFB',
        borderColor: '#374151',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const total = context.dataset.data.reduce((sum, value) => sum + value, 0);
            const percentage = ((context.parsed / total) * 100).toFixed(1);
            return `${context.label}: $${context.parsed.toFixed(2)} (${percentage}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="card p-6 animate-fade-in">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        <PieChartIcon className="w-6 h-6" />
        Expense Breakdown
      </h2>

      {Object.keys(categoryData).length === 0 ? (
        <div className="text-center py-12">
          <PieChartIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400 text-lg">No data to display</p>
          <p className="text-gray-500 text-sm mt-2">Add expenses to see the breakdown</p>
        </div>
      ) : (
        <div className="h-80">
          <Doughnut data={data} options={options} />
        </div>
      )}

      {Object.keys(categoryData).length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="text-lg font-semibold text-white">Category Summary</h3>
          <div className="space-y-2">
            {Object.entries(categoryData)
              .sort(([,a], [,b]) => b - a)
              .map(([category, amount]) => {
                const total = Object.values(categoryData).reduce((sum, value) => sum + value, 0);
                const percentage = ((amount / total) * 100).toFixed(1);
                return (
                  <div key={category} className="flex justify-between items-center p-3 glass rounded-lg">
                    <span className="text-gray-300">{category}</span>
                    <div className="text-right">
                      <div className="text-white font-semibold">${amount.toFixed(2)}</div>
                      <div className="text-sm text-gray-400">{percentage}%</div>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpenseChart;