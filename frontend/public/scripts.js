// Minimal Dark Theme Expense Tracker
class ExpenseTracker {
    constructor() {
        this.API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:8001/api' : '/api';
        this.expenses = [];
        this.budgets = [];
        this.chart = null;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setCurrentDate();
        await this.loadData();
        this.updateDashboard();
        this.initChart();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Form submissions
        document.getElementById('expense-form').addEventListener('submit', this.handleAddExpense.bind(this));
        document.getElementById('budget-form').addEventListener('submit', this.handleAddBudget.bind(this));

        // Modal close events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.hideAllModals();
            }
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        // Load tab-specific data
        if (tabName === 'expenses') {
            this.updateExpenseList();
        } else if (tabName === 'analytics') {
            this.updateChart();
        } else if (tabName === 'budgets') {
            this.updateBudgetList();
        }
    }

    setCurrentDate() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('expense-date').value = today;
    }

    async loadData() {
        try {
            await Promise.all([
                this.loadExpenses(),
                this.loadBudgets()
            ]);
        } catch (error) {
            console.error('Error loading data:', error);
        }
    }

    async loadExpenses() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/expenses`);
            if (response.ok) {
                this.expenses = await response.json();
            }
        } catch (error) {
            console.error('Error loading expenses:', error);
            this.expenses = [];
        }
    }

    async loadBudgets() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/budgets`);
            if (response.ok) {
                this.budgets = await response.json();
            }
        } catch (error) {
            console.error('Error loading budgets:', error);
            this.budgets = [];
        }
    }

    async handleAddExpense(e) {
        e.preventDefault();
        
        const expense = {
            name: document.getElementById('expense-name').value.trim(),
            amount: parseFloat(document.getElementById('expense-amount').value),
            date: document.getElementById('expense-date').value,
            category: document.getElementById('expense-category').value,
            description: document.getElementById('expense-description').value.trim()
        };

        if (!expense.name || !expense.amount || !expense.date || !expense.category) {
            this.showToast('Please fill all required fields', 'error');
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.API_BASE_URL}/expenses`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(expense),
            });

            if (response.ok) {
                const newExpense = await response.json();
                this.expenses.unshift(newExpense);
                this.updateDashboard();
                this.hideAddExpenseModal();
                this.showToast('Expense added successfully!', 'success');
                e.target.reset();
                this.setCurrentDate();
            } else {
                throw new Error('Failed to add expense');
            }
        } catch (error) {
            console.error('Error adding expense:', error);
            this.showToast('Failed to add expense', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async handleAddBudget(e) {
        e.preventDefault();
        
        const budget = {
            category: document.getElementById('budget-category').value,
            amount: parseFloat(document.getElementById('budget-amount').value),
            period: document.getElementById('budget-period').value
        };

        if (!budget.category || !budget.amount) {
            this.showToast('Please fill all required fields', 'error');
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.API_BASE_URL}/budgets`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(budget),
            });

            if (response.ok) {
                const newBudget = await response.json();
                this.budgets.push(newBudget);
                this.updateBudgetList();
                this.hideAddBudgetModal();
                this.showToast('Budget added successfully!', 'success');
                e.target.reset();
            } else {
                throw new Error('Failed to add budget');
            }
        } catch (error) {
            console.error('Error adding budget:', error);
            this.showToast('Failed to add budget', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async deleteExpense(expenseId) {
        if (!confirm('Are you sure you want to delete this expense?')) {
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.API_BASE_URL}/expenses/${expenseId}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                this.expenses = this.expenses.filter(expense => expense.id !== expenseId);
                this.updateDashboard();
                this.showToast('Expense deleted successfully!', 'success');
            } else {
                throw new Error('Failed to delete expense');
            }
        } catch (error) {
            console.error('Error deleting expense:', error);
            this.showToast('Failed to delete expense', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async suggestCategory() {
        const expenseName = document.getElementById('expense-name').value.trim();
        const amount = parseFloat(document.getElementById('expense-amount').value);

        if (!expenseName || !amount) {
            this.showToast('Please enter expense name and amount first', 'error');
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.API_BASE_URL}/expenses/categorize?expense_name=${encodeURIComponent(expenseName)}&amount=${amount}`);
            
            if (response.ok) {
                const data = await response.json();
                document.getElementById('expense-category').value = data.suggested_category;
                this.showToast(`AI suggested: ${data.suggested_category}`, 'info');
            } else {
                throw new Error('Failed to get category suggestion');
            }
        } catch (error) {
            console.error('Error suggesting category:', error);
            this.showToast('Failed to get AI suggestion', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async getInsights() {
        if (this.expenses.length === 0) {
            this.showToast('Add some expenses to get insights', 'info');
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.API_BASE_URL}/expenses/insights`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expenses: this.expenses }),
            });

            if (response.ok) {
                const insights = await response.json();
                this.displayInsights(insights);
            } else {
                throw new Error('Failed to get insights');
            }
        } catch (error) {
            console.error('Error getting insights:', error);
            this.showToast('Failed to get insights', 'error');
        } finally {
            this.hideLoading();
        }
    }

    updateDashboard() {
        this.updateStats();
        this.updateRecentExpenses();
    }

    updateStats() {
        const totalAmount = this.expenses.reduce((sum, expense) => sum + expense.amount, 0);
        const currentMonth = new Date().toISOString().slice(0, 7);
        const monthlyAmount = this.expenses
            .filter(expense => expense.date.startsWith(currentMonth))
            .reduce((sum, expense) => sum + expense.amount, 0);
        const uniqueCategories = new Set(this.expenses.map(e => e.category)).size;

        document.getElementById('total-expenses').textContent = this.formatCurrency(totalAmount);
        document.getElementById('month-expenses').textContent = this.formatCurrency(monthlyAmount);
        document.getElementById('categories-count').textContent = uniqueCategories;
    }

    updateRecentExpenses() {
        const recentExpenses = this.expenses.slice(0, 5);
        const container = document.getElementById('recent-expense-list');

        if (recentExpenses.length === 0) {
            container.innerHTML = this.renderEmptyState('📋', 'No expenses yet', 'Add your first expense to get started');
            return;
        }

        container.innerHTML = recentExpenses.map(expense => `
            <div class="expense-item">
                <div class="expense-icon">${this.getCategoryIcon(expense.category)}</div>
                <div class="expense-details">
                    <div class="expense-name">${expense.name}</div>
                    <div class="expense-meta">${expense.category} • ${this.formatDate(expense.date)}</div>
                </div>
                <div class="expense-amount">${this.formatCurrency(expense.amount)}</div>
                <button class="expense-delete" onclick="app.deleteExpense('${expense.id}')">×</button>
            </div>
        `).join('');
    }

    updateExpenseList() {
        const container = document.getElementById('all-expense-list');

        if (this.expenses.length === 0) {
            container.innerHTML = this.renderEmptyState('💸', 'No expenses found', 'Start tracking your expenses');
            return;
        }

        container.innerHTML = this.expenses.map(expense => `
            <div class="expense-item">
                <div class="expense-icon">${this.getCategoryIcon(expense.category)}</div>
                <div class="expense-details">
                    <div class="expense-name">${expense.name}</div>
                    <div class="expense-meta">${expense.category} • ${this.formatDate(expense.date)}</div>
                    ${expense.description ? `<div class="expense-description">${expense.description}</div>` : ''}
                </div>
                <div class="expense-amount">${this.formatCurrency(expense.amount)}</div>
                <button class="expense-delete" onclick="app.deleteExpense('${expense.id}')">×</button>
            </div>
        `).join('');
    }

    updateBudgetList() {
        const container = document.getElementById('budget-list');

        if (this.budgets.length === 0) {
            container.innerHTML = this.renderEmptyState('💰', 'No budgets set', 'Create budgets to track spending');
            return;
        }

        const currentMonth = new Date().toISOString().slice(0, 7);
        
        container.innerHTML = this.budgets.map(budget => {
            const spent = this.expenses
                .filter(exp => exp.category === budget.category && exp.date.startsWith(currentMonth))
                .reduce((sum, exp) => sum + exp.amount, 0);
            
            const percentage = budget.amount > 0 ? (spent / budget.amount) * 100 : 0;
            let status = 'good';
            if (percentage >= 90) status = 'danger';
            else if (percentage >= 75) status = 'warning';

            return `
                <div class="budget-item">
                    <div class="budget-header">
                        <div class="budget-category">${this.getCategoryIcon(budget.category)} ${budget.category}</div>
                        <div class="budget-amount">${this.formatCurrency(budget.amount)}</div>
                    </div>
                    <div class="budget-progress">
                        <div class="budget-progress-fill ${status}" style="width: ${Math.min(percentage, 100)}%"></div>
                    </div>
                    <div class="budget-status">
                        Spent: ${this.formatCurrency(spent)} / ${this.formatCurrency(budget.amount)} 
                        (${percentage.toFixed(0)}%)
                    </div>
                </div>
            `;
        }).join('');
    }

    initChart() {
        const canvas = document.getElementById('expense-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        if (this.chart) {
            this.chart.destroy();
        }

        const data = this.getChartData();

        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        '#007AFF', '#32D74B', '#FF9F0A', '#FF453A', '#5856D6',
                        '#64D2FF', '#30B0C7', '#AC8E68', '#988F86', '#8C7853'
                    ],
                    borderWidth: 0,
                    cutout: '60%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    updateChart() {
        if (!this.chart) {
            this.initChart();
            return;
        }

        const data = this.getChartData();
        this.chart.data.labels = data.labels;
        this.chart.data.datasets[0].data = data.values;
        this.chart.update();
    }

    getChartData() {
        if (this.expenses.length === 0) {
            return { labels: ['No Data'], values: [1] };
        }

        const categoryTotals = {};
        this.expenses.forEach(expense => {
            categoryTotals[expense.category] = (categoryTotals[expense.category] || 0) + expense.amount;
        });

        const categories = Object.entries(categoryTotals)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8);

        return {
            labels: categories.map(([category]) => category),
            values: categories.map(([, amount]) => amount)
        };
    }

    displayInsights(insights) {
        const container = document.getElementById('insights-container');

        if (insights.length === 0) {
            container.innerHTML = this.renderEmptyState('🤖', 'No insights available', 'Add more expenses to get AI insights');
            return;
        }

        container.innerHTML = insights.map(insight => `
            <div class="insight-item">
                <div class="insight-message">${insight.message}</div>
                <div class="insight-confidence">Confidence: ${Math.round(insight.confidence * 100)}%</div>
            </div>
        `).join('');
    }

    // UI Helper Methods
    showAddExpenseModal() {
        document.getElementById('add-expense-modal').classList.add('active');
    }

    hideAddExpenseModal() {
        document.getElementById('add-expense-modal').classList.remove('active');
    }

    showAddBudgetModal() {
        document.getElementById('add-budget-modal').classList.add('active');
    }

    hideAddBudgetModal() {
        document.getElementById('add-budget-modal').classList.remove('active');
    }

    hideAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    showLoading() {
        document.getElementById('loading').classList.add('active');
    }

    hideLoading() {
        document.getElementById('loading').classList.remove('active');
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // Utility Methods
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric'
        });
    }

    getCategoryIcon(category) {
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
            'Travel': '✈️',
            'Other': '📦'
        };
        return icons[category] || '📦';
    }

    renderEmptyState(icon, title, description) {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">${icon}</div>
                <div>${title}</div>
                <small>${description}</small>
            </div>
        `;
    }
}

// Global functions for HTML onclick handlers
function showAddExpenseModal() {
    app.showAddExpenseModal();
}

function hideAddExpenseModal() {
    app.hideAddExpenseModal();
}

function showAddBudgetModal() {
    app.showAddBudgetModal();
}

function hideAddBudgetModal() {
    app.hideAddBudgetModal();
}

function suggestCategory() {
    app.suggestCategory();
}

function getInsights() {
    app.getInsights();
}

// Initialize the app
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ExpenseTracker();
});
