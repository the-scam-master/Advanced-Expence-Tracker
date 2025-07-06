import React, { useState } from 'react';
import { Brain, RefreshCw, TrendingUp, AlertTriangle, Lightbulb, Target, Zap } from 'lucide-react';
import toast from 'react-hot-toast';
import { expenseService } from '../services/expenseService';

const AIInsights = ({ insights, expenses, loading, onRefresh }) => {
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);

  const generatePrediction = async () => {
    if (expenses.length === 0) {
      toast.error('Add some expenses to get predictions');
      return;
    }

    try {
      setPredictionLoading(true);
      const result = await expenseService.predictNextMonth(expenses);
      setPrediction(result);
      toast.success('Prediction generated successfully!');
    } catch (error) {
      console.error('Error generating prediction:', error);
      toast.error('Failed to generate prediction');
    } finally {
      setPredictionLoading(false);
    }
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'prediction':
        return <TrendingUp className="w-5 h-5 text-blue-400" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'recommendation':
        return <Lightbulb className="w-5 h-5 text-green-400" />;
      case 'insight':
        return <Brain className="w-5 h-5 text-purple-400" />;
      default:
        return <Zap className="w-5 h-5 text-cyan-400" />;
    }
  };

  const getInsightBgColor = (type) => {
    switch (type) {
      case 'prediction':
        return 'bg-blue-900/20 border-blue-500/30';
      case 'warning':
        return 'bg-yellow-900/20 border-yellow-500/30';
      case 'recommendation':
        return 'bg-green-900/20 border-green-500/30';
      case 'insight':
        return 'bg-purple-900/20 border-purple-500/30';
      default:
        return 'bg-cyan-900/20 border-cyan-500/30';
    }
  };

  return (
    <div className="card p-6 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Brain className="w-6 h-6" />
          AI Insights
        </h2>
        <div className="flex gap-2">
          <button
            onClick={generatePrediction}
            disabled={predictionLoading || expenses.length === 0}
            className="btn-primary px-3 py-2 rounded-lg flex items-center gap-2 text-white font-medium text-sm disabled:opacity-50"
          >
            <Target className="w-4 h-4" />
            {predictionLoading ? 'Predicting...' : 'Predict'}
          </button>
          <button
            onClick={onRefresh}
            disabled={loading || expenses.length === 0}
            className="btn-secondary px-3 py-2 rounded-lg flex items-center gap-2 text-white font-medium text-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Prediction Section */}
      {prediction && (
        <div className="glass p-4 rounded-lg mb-6 bg-blue-900/20 border border-blue-500/30">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">Next Month Prediction</h3>
          </div>
          <p className="text-gray-300 mb-3">{prediction.message}</p>
          
          {prediction.data && prediction.data.category_breakdown && (
            <div className="space-y-2">
              <p className="text-sm text-gray-400">Category Breakdown:</p>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(prediction.data.category_breakdown).map(([category, amount]) => (
                  <div key={category} className="flex justify-between text-sm">
                    <span className="text-gray-300">{category}</span>
                    <span className="text-white font-medium">${amount.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          <div className="mt-3 pt-3 border-t border-blue-500/30">
            <div className="flex items-center gap-2 text-sm text-blue-300">
              <span>Confidence: {(prediction.confidence * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Insights List */}
      {insights.length === 0 && !loading ? (
        <div className="text-center py-12">
          <Brain className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400 text-lg">No insights available</p>
          <p className="text-gray-500 text-sm mt-2">
            Add more expenses to get AI-powered insights
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="glass p-4 rounded-lg animate-pulse">
                  <div className="flex items-center gap-3">
                    <div className="w-5 h-5 bg-gray-600 rounded"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-600 rounded w-3/4"></div>
                      <div className="h-3 bg-gray-700 rounded w-1/2"></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            insights.map((insight, index) => (
              <div
                key={index}
                className={`glass p-4 rounded-lg border ${getInsightBgColor(insight.type)}`}
              >
                <div className="flex items-start gap-3">
                  {getInsightIcon(insight.type)}
                  <div className="flex-1">
                    <p className="text-white font-medium mb-1">{insight.message}</p>
                    
                    {insight.data && Object.keys(insight.data).length > 0 && (
                      <div className="text-sm text-gray-400 space-y-1">
                        {Object.entries(insight.data).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                            <span className="text-white">
                              {typeof value === 'number' ? 
                                (key.includes('amount') || key.includes('spending') ? `$${value.toFixed(2)}` : value) : 
                                String(value)
                              }
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    <div className="flex items-center gap-2 mt-3 text-xs text-gray-500">
                      <span>AI Confidence: {(insight.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tips Section */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          Smart Tips
        </h3>
        <div className="space-y-2 text-sm text-gray-300">
          <p>• Add more expenses to get better AI predictions</p>
          <p>• Set budgets to receive spending alerts</p>
          <p>• Review your spending patterns weekly</p>
          <p>• Use categories consistently for better insights</p>
        </div>
      </div>
    </div>
  );
};

export default AIInsights;