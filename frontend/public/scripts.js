// Global variables
let expenses = [];
let budgets = [];
let chart = null;
const API_BASE_URL = '/api';

// Chart.js reference
const Chart = window.Chart;

// Categories with icons
const categories = {
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

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadData();
    initializeEventListeners();
    populateMonthSelector();
    populateBudgetCategories();
    updateStats();
    updateExpenseList();
    updateChart();
    updateBudgetList();
    checkBudgetAlerts();
    setCurrentDate();
});

// Load data from localStorage
function loadData() {
    const savedExpenses = localStorage.getItem('expenses');
    const savedBudgets = localStorage.getItem('budgets');
    
    if (savedExpenses) {
        expenses = JSON.parse(savedExpenses);
    }
    
    if (savedBudgets) {
        budgets = JSON.parse(savedBudgets);
    }
}

// Save data to localStorage
function saveExpenses() {
    localStorage.setItem('expenses', JSON.stringify(expenses));
}

function saveBudgets() {
    localStorage.setItem('budgets', JSON.stringify(budgets));
}

// Initialize event listeners
function initializeEventListeners() {
    // Add Expense Modal
    document.getElementById('add-expense-btn').addEventListener('click', showExpenseModal);
    document.getElementById('close-modal').addEventListener('click', hideExpenseModal);
    document.getElementById('cancel-expense').addEventListener('click', hideExpenseModal);
    document.getElementById('expense-form').addEventListener('submit', addExpense);
    
    // AI Category Suggestion
    document.getElementById('suggest-category').addEventListener('click', suggestCategory);
    
    // Budget Management
    document.getElementById('add-budget-btn').addEventListener('click', showBudgetForm);
    document.getElementById('cancel-budget').addEventListener('click', hideBudgetForm);
    document.getElementById('save-budget').addEventListener('click', addBudget);
    
    // Data Management
    document.getElementById('export-btn').addEventListener('click', exportData);
    document.getElementById('import-file').addEventListener('change', importData);
    
    // AI Features
    document.getElementById('predict-btn').addEventListener('click', predictExpenses);
    document.getElementById('refresh-insights').addEventListener('click', refreshInsights);
    
    // Month Selector
    document.getElementById('month-selector').addEventListener('change', function() {
        updateExpenseList();
        updateChart();
        updateStats();
    });
    
    // Close modal on backdrop click
    document.getElementById('expense-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            hideExpenseModal();
        }
    });
}

// Set current date in form
function setCurrentDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('expense-date').value = today;
}

// Toast notifications
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Show/Hide Loading
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// Expense Modal Functions
function showExpenseModal() {
    document.getElementById('expense-modal').classList.add('active');
    document.getElementById('expense-modal').classList.remove('hidden');
}

function hideExpenseModal() {
    document.getElementById('expense-modal').classList.remove('active');
    setTimeout(() => {
        document.getElementById('expense-modal').classList.add('hidden');
    }, 300);
    document.getElementById('expense-form').reset();
    setCurrentDate();
}

// Add Expense
async function addExpense(e) {
    e.preventDefault();
    
    const name = document.getElementById('expense-name').value;
    const amount = parseFloat(document.getElementById('expense-amount').value);
    const date = document.getElementById('expense-date').value;
    const category = document.getElementById('expense-category').value;
    const description = document.getElementById('expense-description').value;
    
    if (!name || !amount || !date || !category) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    const expense = {
        id: Date.now().toString(),
        name,
        amount,
        date,
        category,
        description
    };
    
    expenses.unshift(expense);
    saveExpenses();
    hideExpenseModal();
    
    updateStats();
    updateExpenseList();
    updateChart();
    checkBudgetAlerts();
    
    showToast('Expense added successfully!');
}

// Delete Expense
function deleteExpense(id) {
    if (confirm('Are you sure you want to delete this expense?')) {
        expenses = expenses.filter(expense => expense.id !== id);
        saveExpenses();
        
        updateStats();
        updateExpenseList();
        updateChart();
        checkBudgetAlerts();
        
        showToast('Expense deleted successfully!');
    }
}

// AI Category Suggestion
async function suggestCategory() {
    const name = document.getElementById('expense-name').value;
    const amount = document.getElementById('expense-amount').value;
    
    if (!name || !amount) {
        showToast('Please enter expense name and amount first', 'error');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/expenses/categorize?expense_name=${encodeURIComponent(name)}&amount=${amount}`);
        const data = await response.json();
        
        if (data.suggested_category) {
            document.getElementById('expense-category').value = data.suggested_category;
            showToast(`Category suggested: ${data.suggested_category}`);
        }
    } catch (error) {
        console.error('Error suggesting category:', error);
        showToast('Failed to suggest category', 'error');
    } finally {
        hideLoading();
    }
}

// Budget Functions
function showBudgetForm() {
    document.getElementById('budget-form').classList.remove('hidden');
}

function hideBudgetForm() {
    document.getElementById('budget-form').classList.add('hidden');
    document.getElementById('budget-category').value = '';
    document.getElementById('budget-amount').value = '';
    document.getElementById('budget-period').value = 'monthly';
}

function addBudget() {
    const category = document.getElementById('budget-category').value;
    const amount = parseFloat(document.getElementById('budget-amount').value);
    const period = document.getElementById('budget-period').value;
    
    if (!category || !amount) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    const existingBudget = budgets.find(b => b.category === category);
    if (existingBudget) {
        showToast('Budget already exists for this category', 'error');
        return;
    }
    
    const budget = {
        id: Date.now().toString(),
        category,
        amount,
        period
    };
    
    budgets.push(budget);
    saveBudgets();
    hideBudgetForm();
    populateBudgetCategories();
    updateBudgetList();
    checkBudgetAlerts();
    
    showToast('Budget added successfully!');
}

function deleteBudget(id) {
    budgets = budgets.filter(b => b.id !== id);
    saveBudgets();
    populateBudgetCategories();
    updateBudgetList();
    checkBudgetAlerts();
    showToast('Budget removed successfully!');
}

// AI Predict Expenses
async function predictExpenses() {
    if (expenses.length === 0) {
        showToast('Add some expenses to get predictions', 'error');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/expenses/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ expenses })
        });
        
        const prediction = await response.json();
        
        // Display prediction
        const predictionResult = document.getElementById('prediction-result');
        predictionResult.innerHTML = `
            <div class="budget-item" style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3);">
                <div class="budget-header">
                    <div class="budget-info">
                        <h3><i class="fas fa-chart-line"></i> Next Month Prediction</h3>
                        <small>AI-powered forecast</small>
                    </div>
                    <div class="budget-stats">
                        <div class="budget-amount">${prediction.confidence ? (prediction.confidence * 100).toFixed(0) + '%' : 'N/A'}</div>
                        <small>Confidence</small>
                    </div>
                </div>
                <p style="color: var(--text-secondary); margin-bottom: 1rem;">${prediction.message}</p>
                ${prediction.data && prediction.data.category_breakdown ? 
                    `<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; font-size: 0.875rem;">
                        ${Object.entries(prediction.data.category_breakdown).map(([cat, amt]) => 
                            `<div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--text-muted);">${cat}</span>
                                <span style="color: var(--text-primary); font-weight: 500;">$${amt.toFixed(2)}</span>
                            </div>`
                        ).join('')}
                    </div>` : ''
                }
            </div>
        `;
        predictionResult.classList.remove('hidden');
        
        showToast('Prediction generated successfully!');
    } catch (error) {
        console.error('Error predicting expenses:', error);
        showToast('Failed to generate prediction', 'error');
    } finally {
        hideLoading();
    }
}

// AI Refresh Insights
async function refreshInsights() {
    if (expenses.length === 0) {
        showToast('Add some expenses to get insights', 'error');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/expenses/insights`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ expenses })
        });
        
        const insights = await response.json();
        
        // Display insights
        const insightsContainer = document.getElementById('ai-insights');
        if (insights.length > 0) {
            insightsContainer.innerHTML = insights.map(insight => `
                <div class="budget-item" style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3);">
                    <div class="budget-header">
                        <div class="budget-info">
                            <h3><i class="fas fa-lightbulb"></i> ${insight.type.charAt(0).toUpperCase() + insight.type.slice(1)}</h3>
                            <small>AI Confidence: ${(insight.confidence * 100).toFixed(0)}%</small>
                        </div>
                    </div>
                    <p style="color: var(--text-secondary);">${insight.message}</p>
                    ${Object.keys(insight.data).length > 0 ? 
                        `<div style="margin-top: 0.5rem; font-size: 0.875rem;">
                            ${Object.entries(insight.data).map(([key, value]) => 
                                `<div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                                    <span style="color: var(--text-muted); text-transform: capitalize;">${key.replace(/_/g, ' ')}:</span>
                                    <span style="color: var(--text-primary);">${typeof value === 'number' && (key.includes('amount') || key.includes('spending')) ? '$' + value.toFixed(2) : value}</span>
                                </div>`
                            ).join('')}
                        </div>` : ''
                    }
                </div>
            `).join('');
            
            // Update insights count
            document.getElementById('insights-count').textContent = insights.length;
        }
        
        showToast('Insights refreshed!');
    } catch (error) {
        console.error('Error getting insights:', error);
        showToast('Failed to get insights', 'error');
    } finally {
        hideLoading();
    }
}

// Data Management
function exportData() {
    const data = { expenses, budgets };
    const dataStr = JSON.stringify(data, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `expense-data-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    showToast('Data exported successfully!');
}

function importData(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = JSON.parse(e.target.result);
            if (data.expenses) {
                expenses = data.expenses;
                saveExpenses();
            }
            if (data.budgets) {
                budgets = data.budgets;
                saveBudgets();
            }
            
            updateStats();
            updateExpenseList();
            updateChart();
            updateBudgetList();
            populateBudgetCategories();
            checkBudgetAlerts();
            
            showToast('Data imported successfully!');
        } catch (error) {
            showToast('Invalid file format', 'error');
        }
    };
    reader.readAsText(file);
}

// Update Functions
function updateStats() {
    const totalExpenses = expenses.reduce((sum, expense) => sum + expense.amount, 0);
    const currentMonth = document.getElementById('month-selector').value || new Date().toISOString().substring(0, 7);
    const monthlyExpenses = expenses.filter(expense => expense.date.startsWith(currentMonth));
    const monthlyTotal = monthlyExpenses.reduce((sum, expense) => sum + expense.amount, 0);
    const categoriesCount = new Set(expenses.map(e => e.category)).size;
    
    document.getElementById('total-expenses').textContent = `$${totalExpenses.toFixed(2)}`;
    document.getElementById('month-expenses').textContent = `$${monthlyTotal.toFixed(2)}`;
    document.getElementById('categories-count').textContent = categoriesCount;
    
    // Update analytics
    updateAnalytics();
}

function updateAnalytics() {
    const totalExpenses = expenses.reduce((sum, expense) => sum + expense.amount, 0);
    document.getElementById('analytics-total').textContent = `$${totalExpenses.toFixed(2)}`;
    
    // Top category
    const categoryTotals = {};
    expenses.forEach(expense => {
        categoryTotals[expense.category] = (categoryTotals[expense.category] || 0) + expense.amount;
    });
    
    const sortedCategories = Object.entries(categoryTotals).sort(([,a], [,b]) => b - a);
    if (sortedCategories.length > 0) {
        const [topCategory, topAmount] = sortedCategories[0];
        document.getElementById('analytics-top-category').textContent = topCategory;
        document.getElementById('analytics-top-amount').textContent = `$${topAmount.toFixed(2)}`;
    }
    
    // Monthly breakdown
    const monthlyBreakdown = document.getElementById('monthly-breakdown');
    const monthlyData = {};
    
    expenses.forEach(expense => {
        const month = expense.date.substring(0, 7);
        if (!monthlyData[month]) {
            monthlyData[month] = { total: 0, count: 0 };
        }
        monthlyData[month].total += expense.amount;
        monthlyData[month].count++;
    });
    
    const sortedMonths = Object.entries(monthlyData).sort(([a], [b]) => b.localeCompare(a)).slice(0, 6);
    
    if (sortedMonths.length > 0) {
        monthlyBreakdown.innerHTML = `
            <h3 style="color: var(--text-primary); margin-bottom: 1rem;">Monthly Breakdown</h3>
            ${sortedMonths.map(([month, data]) => `
                <div class="budget-item">
                    <div class="budget-header">
                        <div class="budget-info">
                            <h3>${new Date(month + '-01').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</h3>
                        </div>
                        <div class="budget-stats">
                            <div class="budget-amount">$${data.total.toFixed(2)}</div>
                            <small>${data.count} expenses</small>
                        </div>
                    </div>
                </div>
            `).join('')}
        `;
    }
}

function populateMonthSelector() {
    const selector = document.getElementById('month-selector');
    const months = [...new Set(expenses.map(expense => expense.date.substring(0, 7)))];
    const currentMonth = new Date().toISOString().substring(0, 7);
    
    if (!months.includes(currentMonth)) {
        months.push(currentMonth);
    }
    
    months.sort((a, b) => b.localeCompare(a));
    
    selector.innerHTML = months.map(month => 
        `<option value="${month}">${new Date(month + '-01').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</option>`
    ).join('');
    
    selector.value = currentMonth;
}

function populateBudgetCategories() {
    const selector = document.getElementById('budget-category');
    const usedCategories = budgets.map(b => b.category);
    const availableCategories = Object.keys(categories).filter(cat => !usedCategories.includes(cat));
    
    selector.innerHTML = '<option value="">Select Category</option>' + 
        availableCategories.map(category => `<option value="${category}">${category}</option>`).join('');
}

function updateExpenseList() {
    const selectedMonth = document.getElementById('month-selector').value || new Date().toISOString().substring(0, 7);
    const filteredExpenses = expenses.filter(expense => expense.date.startsWith(selectedMonth));
    const sortedExpenses = filteredExpenses.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    const container = document.getElementById('expense-list-container');
    
    if (sortedExpenses.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-dollar-sign empty-icon"></i>
                <p>No expenses found for this month</p>
                <small>Start by adding your first expense</small>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        ${sortedExpenses.map(expense => `
            <div class="expense-item">
                <div class="expense-icon">${categories[expense.category] || '📦'}</div>
                <div class="expense-details">
                    <div class="expense-name">${expense.name}</div>
                    <div class="expense-meta">
                        <div class="expense-category category-${expense.category.toLowerCase().replace(' ', '-')}">
                            <i class="fas fa-tag"></i>
                            ${expense.category}
                        </div>
                        <div class="expense-date">
                            <i class="fas fa-calendar"></i>
                            ${new Date(expense.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </div>
                    </div>
                    ${expense.description ? `<div class="expense-description">${expense.description}</div>` : ''}
                </div>
                <div class="expense-amount">$${expense.amount.toFixed(2)}</div>
                <button class="delete-expense" onclick="deleteExpense('${expense.id}')">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `).join('')}
        <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--border);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: var(--text-muted);">Total for ${new Date(selectedMonth + '-01').toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>
                <span style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">$${sortedExpenses.reduce((sum, expense) => sum + expense.amount, 0).toFixed(2)}</span>
            </div>
        </div>
    `;
}

function updateChart() {
    const selectedMonth = document.getElementById('month-selector').value || new Date().toISOString().substring(0, 7);
    const filteredExpenses = expenses.filter(expense => expense.date.startsWith(selectedMonth));
    
    const categoryData = {};
    filteredExpenses.forEach(expense => {
        categoryData[expense.category] = (categoryData[expense.category] || 0) + expense.amount;
    });
    
    const chartCanvas = document.getElementById('expense-chart');
    const chartEmpty = document.getElementById('chart-empty');
    const categorySummary = document.getElementById('category-summary');
    
    if (Object.keys(categoryData).length === 0) {
        chartCanvas.style.display = 'none';
        chartEmpty.style.display = 'block';
        categorySummary.innerHTML = '';
        return;
    }
    
    chartCanvas.style.display = 'block';
    chartEmpty.style.display = 'none';
    
    const ctx = chartCanvas.getContext('2d');
    
    if (chart) {
        chart.destroy();
    }
    
    chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categoryData),
            datasets: [{
                data: Object.values(categoryData),
                backgroundColor: [
                    '#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', 
                    '#EF4444', '#EC4899', '#06B6D4', '#F97316',
                    '#84CC16', '#22C55E', '#6366F1', '#6B7280'
                ],
                borderColor: '#1F2937',
                borderWidth: 2,
                hoverBorderWidth: 3,
            }]
        },
        options: {
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
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: '#1F2937',
                    titleColor: '#F9FAFB',
                    bodyColor: '#F9FAFB',
                    borderColor: '#374151',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((sum, value) => sum + value, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: $${context.parsed.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // Update category summary
    const sortedCategories = Object.entries(categoryData).sort(([,a], [,b]) => b - a);
    const total = Object.values(categoryData).reduce((sum, value) => sum + value, 0);
    
    categorySummary.innerHTML = `
        <h3 style="color: var(--text-primary); margin-bottom: 1rem;">Category Summary</h3>
        ${sortedCategories.map(([category, amount]) => {
            const percentage = ((amount / total) * 100).toFixed(1);
            return `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: var(--bg-tertiary); border-radius: 8px; margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">${category}</span>
                    <div style="text-align: right;">
                        <div style="color: var(--text-primary); font-weight: 600;">$${amount.toFixed(2)}</div>
                        <div style="font-size: 0.875rem; color: var(--text-muted);">${percentage}%</div>
                    </div>
                </div>
            `;
        }).join('')}
    `;
}

function updateBudgetList() {
    const container = document.getElementById('budget-list');
    
    if (budgets.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-bullseye empty-icon"></i>
                <p>No budgets set</p>
                <small>Create budgets to track your spending</small>
            </div>
        `;
        return;
    }
    
    container.innerHTML = budgets.map(budget => {
        const spent = getCurrentMonthExpenses(budget.category);
        const remaining = budget.amount - spent;
        const percentage = (spent / budget.amount) * 100;
        
        let status = 'good';
        let statusText = 'Within budget';
        let statusColor = 'var(--accent-green)';
        
        if (percentage >= 100) {
            status = 'danger';
            statusText = 'Budget exceeded!';
            statusColor = 'var(--accent-red)';
        } else if (percentage >= 80) {
            status = 'warning';
            statusText = 'Close to budget limit';
            statusColor = 'var(--accent-yellow)';
        } else if (percentage >= 60) {
            status = 'warning';
            statusText = 'Approaching budget limit';
            statusColor = 'var(--accent-yellow)';
        }
        
        return `
            <div class="budget-item" style="background: rgba(${status === 'danger' ? '239, 68, 68' : status === 'warning' ? '245, 158, 11' : '16, 185, 129'}, 0.1);">
                <div class="budget-header">
                    <div class="budget-info">
                        <h3>${budget.category}</h3>
                        <small>${budget.period} budget</small>
                    </div>
                    <div class="budget-stats">
                        <div class="budget-amount">$${spent.toFixed(2)} / $${budget.amount.toFixed(2)}</div>
                        <div class="budget-remaining ${status}" style="color: ${statusColor};">
                            ${remaining >= 0 ? `$${remaining.toFixed(2)} remaining` : `$${Math.abs(remaining).toFixed(2)} over`}
                        </div>
                        <button class="delete-budget" onclick="deleteBudget('${budget.id}')">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
                <div class="budget-progress">
                    <div class="budget-progress-header">
                        <span style="color: var(--text-muted);">Progress</span>
                        <span style="color: ${statusColor};">${percentage.toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill ${status}" style="width: ${Math.min(percentage, 100)}%;"></div>
                    </div>
                </div>
                <div class="budget-status">
                    <i class="fas ${percentage >= 100 ? 'fa-exclamation-triangle' : 'fa-check-circle'}" style="color: ${statusColor};"></i>
                    <span style="color: ${statusColor};">${statusText}</span>
                </div>
            </div>
        `;
    }).join('');
}

function getCurrentMonthExpenses(category) {
    const currentMonth = new Date().toISOString().substring(0, 7);
    return expenses
        .filter(expense => expense.date.startsWith(currentMonth) && expense.category === category)
        .reduce((sum, expense) => sum + expense.amount, 0);
}

function checkBudgetAlerts() {
    const alerts = [];
    
    budgets.forEach(budget => {
        const spent = getCurrentMonthExpenses(budget.category);
        const percentage = (spent / budget.amount) * 100;
        
        if (percentage >= 75) {
            alerts.push({
                category: budget.category,
                percentage: percentage.toFixed(1),
                amount: spent.toFixed(2),
                budget: budget.amount.toFixed(2),
                type: percentage >= 90 ? 'danger' : 'warning'
            });
        }
    });
    
    const alertsContainer = document.getElementById('budget-alerts');
    const alertsContent = document.getElementById('alerts-container');
    
    if (alerts.length > 0) {
        alertsContent.innerHTML = alerts.map(alert => `
            <div style="background: rgba(${alert.type === 'danger' ? '239, 68, 68' : '245, 158, 11'}, 0.1); padding: 0.75rem; border-radius: 8px; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">${alert.category}</span>
                    <span style="color: var(--text-primary); font-weight: 600;">${alert.percentage}% used</span>
                </div>
                <div style="width: 100%; background: var(--bg-secondary); border-radius: 4px; height: 0.5rem;">
                    <div style="height: 0.5rem; border-radius: 4px; background: var(--accent-${alert.type === 'danger' ? 'red' : 'yellow'}); width: ${Math.min(alert.percentage, 100)}%;"></div>
                </div>
            </div>
        `).join('');
        alertsContainer.classList.remove('hidden');
    } else {
        alertsContainer.classList.add('hidden');
    }
}
