import React from 'react';
import { BarChart, TrendingUp, Calendar, DollarSign } from 'lucide-react';
import { format } from 'date-fns';

const Analytics = ({ analytics }) => {
  const getTopCategory = () => {
    const categories = Object.entries(analytics.category_breakdown);
    if (categories.length === 0) return null;
    
    const sorted = categories.sort(([,a], [,b]) => b - a);
    return sorted[0];
  };

  const getSpendingTrend = () => {
    const trend = analytics.monthly_trend;
    if (trend.length < 2) return null;
    
    const current = trend[0]?.total || 0;
    const previous = trend[1]?.total || 0;
    
    const change = current - previous;
    const percentage = previous > 0 ? (change / previous) * 100 : 0;
    
    return { change, percentage, isIncrease: change > 0 };
  };

  const topCategory = getTopCategory();
  const spendingTrend = getSpendingTrend();

  return (
    <div className="card p-6 animate-fade-in">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        <BarChart className="w-6 h-6" />
        Analytics Dashboard
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Total Spending */}
        <div className="glass p-4 rounded-lg">
          <div className="flex items-center gap-3 mb-3">
            <DollarSign className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">Total Spending</h3>
          </div>
          <p className="text-3xl font-bold text-white">
            ${analytics.total_expenses.toFixed(2)}
          </p>
          <p className="text-sm text-gray-400 mt-1">All time expenses</p>
        </div>

        {/* Top Category */}
        {topCategory && (
          <div className="glass p-4 rounded-lg">
            <div className="flex items-center gap-3 mb-3">
              <TrendingUp className="w-5 h-5 text-green-400" />
              <h3 className="text-lg font-semibold text-white">Top Category</h3>
            </div>
            <p className="text-xl font-bold text-white">{topCategory[0]}</p>
            <p className="text-lg text-green-400">${topCategory[1].toFixed(2)}</p>
            <p className="text-sm text-gray-400 mt-1">
              {((topCategory[1] / analytics.total_expenses) * 100).toFixed(1)}% of total
            </p>
          </div>
        )}

        {/* Spending Trend */}
        {spendingTrend && (
          <div className="glass p-4 rounded-lg">
            <div className="flex items-center gap-3 mb-3">
              <Calendar className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Monthly Trend</h3>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-lg font-bold ${spendingTrend.isIncrease ? 'text-red-400' : 'text-green-400'}`}>
                {spendingTrend.isIncrease ? '+' : ''}${spendingTrend.change.toFixed(2)}
              </span>
              <span className={`text-sm ${spendingTrend.isIncrease ? 'text-red-400' : 'text-green-400'}`}>
                ({spendingTrend.isIncrease ? '+' : ''}{spendingTrend.percentage.toFixed(1)}%)
              </span>
            </div>
            <p className="text-sm text-gray-400 mt-1">vs previous month</p>
          </div>
        )}

        {/* Average per Category */}
        <div className="glass p-4 rounded-lg">
          <div className="flex items-center gap-3 mb-3">
            <BarChart className="w-5 h-5 text-yellow-400" />
            <h3 className="text-lg font-semibold text-white">Categories</h3>
          </div>
          <p className="text-xl font-bold text-white">
            {Object.keys(analytics.category_breakdown).length}
          </p>
          <p className="text-sm text-gray-400 mt-1">Different categories used</p>
        </div>
      </div>

      {/* Monthly Breakdown */}
      {analytics.monthly_trend.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-white mb-4">Monthly Breakdown</h3>
          <div className="space-y-3">
            {analytics.monthly_trend.slice(0, 6).map((month, index) => (
              <div key={month.month} className="glass p-3 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">
                    {format(new Date(month.month + '-01'), 'MMMM yyyy')}
                  </span>
                  <div className="text-right">
                    <p className="text-white font-semibold">${month.total.toFixed(2)}</p>
                    <p className="text-sm text-gray-400">{month.count} expenses</p>
                  </div>
                </div>
                {index === 0 && (
                  <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: '100%' }}
                    ></div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Category Breakdown */}
      {Object.keys(analytics.category_breakdown).length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-white mb-4">Category Breakdown</h3>
          <div className="space-y-2">
            {Object.entries(analytics.category_breakdown)
              .sort(([,a], [,b]) => b - a)
              .map(([category, amount]) => {
                const percentage = (amount / analytics.total_expenses) * 100;
                return (
                  <div key={category} className="glass p-3 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-gray-300">{category}</span>
                      <div className="text-right">
                        <span className="text-white font-semibold">${amount.toFixed(2)}</span>
                        <span className="text-sm text-gray-400 ml-2">({percentage.toFixed(1)}%)</span>
                      </div>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${percentage}%` }}
                      ></div>
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

export default Analytics;