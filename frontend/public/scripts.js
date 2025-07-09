// Smart Expense Tracker - Modern Dark Theme Application
class ExpenseTracker {
    constructor() {
        this.API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:8001/api' : '/api';
        this.expenses = [];
        this.budgets = [];
        this.analytics = {};
        this.currentView = 'dashboard';
        this.chart = null;
        
        this.init();
    }

    async init() {
        console.log('🚀 Initializing Smart Expense Tracker...');
        this.setupEventListeners();
        this.setCurrentDate();
        await this.loadInitialData();
        this.updateGreeting();
        this.showView('dashboard');
        this.createChart();
        console.log('✅ Application initialized successfully');
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = e.currentTarget.dataset.view;
                this.showView(view);
            });
        });

        // Forms
        document.getElementById('expense-form')?.addEventListener('submit', this.handleAddExpense.bind(this));
        document.getElementById('budget-form')?.addEventListener('submit', this.handleAddBudget.bind(this));

        // Chart period selector
        document.getElementById('chart-period')?.addEventListener('change', (e) => {
            this.updateChart(e.target.value);
        });

        // Modal overlay clicks
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.hideAllModals();
            }
        });

        // Keyboard events
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAllModals();
            }
        });
    }

    setCurrentDate() {
        const today = new Date().toISOString().split('T')[0];
        const dateInput = document.getElementById('expense-date');
        if (dateInput) {
            dateInput.value = today;
        }
    }

    updateGreeting() {
        const hour = new Date().getHours();
        let greeting = 'Good evening! 🌙';
        
        if (hour < 12) {
            greeting = 'Good morning! ☀️';
        } else if (hour < 17) {
            greeting = 'Good afternoon! 🌤️';
        }
        
        const greetingElement = document.querySelector('.greeting-title');
        if (greetingElement) {
            greetingElement.textContent = greeting;
        }
    }

    async loadInitialData() {
        try {
            this.showLoading();
            await Promise.all([
                this.loadExpenses(),
                this.loadBudgets(),
                this.loadAnalytics()
            ]);
            this.updateDashboard();
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
            this.showToast('Failed to load data', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadExpenses() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/expenses`);
            const data = await response.json();
            
            if (data.success) {
                this.expenses = data.data || [];
                console.log(`📊 Loaded ${this.expenses.length} expenses`);
            } else {
                throw new Error(data.error || 'Failed to load expenses');
            }
        } catch (error) {
            console.error('❌ Error loading expenses:', error);
            this.expenses = [];
        }
    }

    async loadBudgets() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/budgets`);
            const data = await response.json();
            
            if (data.success) {
                this.budgets = data.data || [];
                console.log(`🎯 Loaded ${this.budgets.length} budgets`);
            } else {
                throw new Error(data.error || 'Failed to load budgets');
            }
        } catch (error) {
            console.error('❌ Error loading budgets:', error);
            this.budgets = [];
        }
    }

    async loadAnalytics() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/analytics`);
            const data = await response.json();
            
            if (data.success) {
                this.analytics = data.data || {};
                console.log('📈 Analytics loaded');
            } else {
                throw new Error(data.error || 'Failed to load analytics');
            }
        } catch (error) {
            console.error('❌ Error loading analytics:', error);
            this.analytics = {};
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
                body: JSON.stringify(expense)
            });

            const data = await response.json();
            
            if (data.success) {
                this.expenses.unshift(data.data);
                this.updateDashboard();
                this.hideAddExpenseModal();
                this.showToast('Expense added successfully! 💰', 'success');
                e.target.reset();
                this.setCurrentDate();
                console.log('✅ Expense added:', data.data);
            } else {
                throw new Error(data.error || 'Failed to add expense');
            }
        } catch (error) {
            console.error('❌ Error adding expense:', error);
            this.showToast(error.message || 'Failed to add expense', 'error');
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
                body: JSON.stringify(budget)
            });

            const data = await response.json();
            
            if (data.success) {
                this.budgets.push(data.data);
                this.updateDashboard();
                this.hideBudgetModal();
                this.showToast('Budget set successfully! 🎯', 'success');
                e.target.reset();
                console.log('✅ Budget added:', data.data);
            } else {
                throw new Error(data.error || 'Failed to set budget');
            }
        } catch (error) {
            console.error('❌ Error setting budget:', error);
            this.showToast(error.message || 'Failed to set budget', 'error');
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
                method: 'DELETE'
            });

            const data = await response.json();
            
            if (data.success) {
                this.expenses = this.expenses.filter(exp => exp.id !== expenseId);
                this.updateDashboard();
                this.showToast('Expense deleted successfully! 🗑️', 'success');
                console.log('✅ Expense deleted:', expenseId);
            } else {
                throw new Error(data.error || 'Failed to delete expense');
            }
        } catch (error) {
            console.error('❌ Error deleting expense:', error);
            this.showToast(error.message || 'Failed to delete expense', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async suggestCategory() {
        const expenseName = document.getElementById('expense-name').value.trim();
        const amount = parseFloat(document.getElementById('expense-amount').value);

        if (!expenseName || !amount) {
            this.showToast('Please enter expense name and amount first', 'warning');
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.API_BASE_URL}/expenses/categorize?expense_name=${encodeURIComponent(expenseName)}&amount=${amount}`);
            const data = await response.json();
            
            if (data.success) {
                const categorySelect = document.getElementById('expense-category');
                categorySelect.value = data.suggested_category;
                this.showToast(`🤖 AI suggested: ${data.suggested_category}`, 'info');
                console.log('✅ Category suggested:', data.suggested_category);
            } else {
                throw new Error(data.error || 'Failed to get category suggestion');
            }
        } catch (error) {
            console.error('❌ Error suggesting category:', error);
            this.showToast('Failed to get AI suggestion', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async getAIInsights() {
        if (this.expenses.length === 0) {
            this.showToast('Add some expenses to get AI insights', 'info');
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.API_BASE_URL}/expenses/insights`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expenses: this.expenses })
            });

            const data = await response.json();
            
            if (data.success) {
                this.displayInsights(data.data);
                this.showView('insights');
                this.showToast('🤖 AI insights generated!', 'success');
                console.log('✅ AI insights generated:', data.data);
            } else {
                throw new Error(data.error || 'Failed to get insights');
            }
        } catch (error) {
            console.error('❌ Error getting insights:', error);
            this.showToast('Failed to get AI insights', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async predictExpenses() {
        if (this.expenses.length === 0) {
            this.showToast('Add some expenses to get predictions', 'info');
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.API_BASE_URL}/expenses/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expenses: this.expenses })
            });

            const data = await response.json();
            
            if (data.success) {
                const prediction = data.data;
                this.showToast(`🔮 ${prediction.message}`, 'info');
                console.log('✅ Prediction generated:', prediction);
            } else {
                throw new Error(data.error || 'Failed to get prediction');
            }
        } catch (error) {
            console.error('❌ Error getting prediction:', error);
            this.showToast('Failed to get prediction', 'error');
        } finally {
            this.hideLoading();
        }
    }

    updateDashboard() {
        this.updateStatsCards();
        this.updateRecentExpenses();
        this.updateChart();
        this.loadAnalytics(); // Refresh analytics
    }

    updateStatsCards() {
        const totalExpenses = this.expenses.reduce((sum, exp) => sum + exp.amount, 0);
        const currentMonth = new Date().toISOString().slice(0, 7);
        const monthlyExpenses = this.expenses
            .filter(exp => exp.date.startsWith(currentMonth))
            .reduce((sum, exp) => sum + exp.amount, 0);

        const totalBudget = this.budgets.reduce((sum, budget) => sum + budget.amount, 0);
        const budgetLeft = totalBudget - monthlyExpenses;

        // Update stat cards
        this.updateElement('total-balance', this.formatCurrency(25000 - totalExpenses));
        this.updateElement('month-spent', this.formatCurrency(monthlyExpenses));
        this.updateElement('budget-left', this.formatCurrency(Math.max(0, budgetLeft)));
        this.updateElement('ai-score', this.calculateAIScore());
    }

    calculateAIScore() {
        // Simple AI score calculation based on spending habits
        const monthlyExpenses = this.expenses
            .filter(exp => exp.date.startsWith(new Date().toISOString().slice(0, 7)))
            .reduce((sum, exp) => sum + exp.amount, 0);
        
        const totalBudget = this.budgets.reduce((sum, budget) => sum + budget.amount, 0);
        
        if (totalBudget === 0) return 75;
        
        const utilization = monthlyExpenses / totalBudget;
        
        if (utilization < 0.7) return 90;
        if (utilization < 0.9) return 75;
        if (utilization < 1.1) return 60;
        return 40;
    }

    updateRecentExpenses() {
        const container = document.getElementById('recent-expenses');
        if (!container) return;

        const recentExpenses = this.expenses.slice(0, 5);
        
        if (recentExpenses.length === 0) {
            container.innerHTML = this.renderEmptyState('💳', 'No expenses yet', 'Add your first expense to get started');
            return;
        }

        container.innerHTML = recentExpenses.map(expense => `
            <div class="expense-item">
                <div class="expense-icon">${this.getCategoryIcon(expense.category)}</div>
                <div class="expense-details">
                    <div class="expense-name">${expense.name}</div>
                    <div class="expense-meta">${expense.category} • ${this.formatDate(expense.date)}</div>
                </div>
                <div class="expense-amount">-${this.formatCurrency(expense.amount)}</div>
                <button class="expense-delete" onclick="app.deleteExpense('${expense.id}')" title="Delete expense">
                    🗑️
                </button>
            </div>
        `).join('');
    }

    createChart() {
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
                        '#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', 
                        '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#8b5cf6'
                    ],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e1e22',
                        titleColor: '#ffffff',
                        bodyColor: '#b4b4b9',
                        borderColor: '#2a2a2e',
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                return `${context.label}: ${this.formatCurrency(context.raw)}`;
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });

        this.updateChartLegend(data);
    }

    getChartData(period = 'month') {
        let filteredExpenses = this.expenses;
        
        if (period === 'week') {
            const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
            filteredExpenses = this.expenses.filter(exp => new Date(exp.date) >= weekAgo);
        } else if (period === 'month') {
            const currentMonth = new Date().toISOString().slice(0, 7);
            filteredExpenses = this.expenses.filter(exp => exp.date.startsWith(currentMonth));
        } else if (period === 'year') {
            const currentYear = new Date().getFullYear().toString();
            filteredExpenses = this.expenses.filter(exp => exp.date.startsWith(currentYear));
        }

        const categoryTotals = {};
        filteredExpenses.forEach(expense => {
            categoryTotals[expense.category] = (categoryTotals[expense.category] || 0) + expense.amount;
        });

        const sortedCategories = Object.entries(categoryTotals)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8);

        return {
            labels: sortedCategories.map(([category]) => category),
            values: sortedCategories.map(([, amount]) => amount)
        };
    }

    updateChart(period = 'month') {
        if (!this.chart) return;

        const data = this.getChartData(period);
        this.chart.data.labels = data.labels;
        this.chart.data.datasets[0].data = data.values;
        this.chart.update('active');
        this.updateChartLegend(data);
    }

    updateChartLegend(data) {
        const container = document.getElementById('chart-legend');
        if (!container) return;

        if (data.labels.length === 0) {
            container.innerHTML = '<div class="empty-state">No data available</div>';
            return;
        }

        const total = data.values.reduce((sum, value) => sum + value, 0);
        const colors = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#84cc16', '#f97316'];

        container.innerHTML = data.labels.map((label, index) => {
            const amount = data.values[index];
            const percentage = ((amount / total) * 100).toFixed(1);
            
            return `
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${colors[index] || '#6366f1'}"></div>
                    <span class="legend-label">${label}</span>
                    <span class="legend-amount">${this.formatCurrency(amount)} (${percentage}%)</span>
                </div>
            `;
        }).join('');
    }

    displayInsights(insights) {
        const container = document.getElementById('insights-content');
        if (!container) return;

        if (!insights || insights.length === 0) {
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

    showView(viewName) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.view === viewName) {
                link.classList.add('active');
            }
        });

        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });

        // Show selected view
        const targetView = document.getElementById(`${viewName}-view`);
        if (targetView) {
            targetView.classList.add('active');
            this.currentView = viewName;
            
            // Load view-specific data
            this.loadViewData(viewName);
        }
    }

    async loadViewData(viewName) {
        switch (viewName) {
            case 'expenses':
                this.updateAllExpenses();
                break;
            case 'analytics':
                this.updateAnalyticsView();
                break;
            case 'budgets':
                this.updateBudgetsView();
                break;
            case 'insights':
                if (!document.getElementById('insights-content').hasChildNodes()) {
                    await this.getAIInsights();
                }
                break;
        }
    }

    updateAllExpenses() {
        const container = document.getElementById('all-expenses');
        if (!container) return;

        if (this.expenses.length === 0) {
            container.innerHTML = this.renderEmptyState('💳', 'No expenses yet', 'Add your first expense to get started');
            return;
        }

        container.innerHTML = this.expenses.map(expense => `
            <div class="card">
                <div class="expense-item">
                    <div class="expense-icon">${this.getCategoryIcon(expense.category)}</div>
                    <div class="expense-details">
                        <div class="expense-name">${expense.name}</div>
                        <div class="expense-meta">${expense.category} • ${this.formatDate(expense.date)}</div>
                        ${expense.description ? `<div class="expense-description">${expense.description}</div>` : ''}
                    </div>
                    <div class="expense-amount">-${this.formatCurrency(expense.amount)}</div>
                    <button class="expense-delete" onclick="app.deleteExpense('${expense.id}')" title="Delete expense">
                        🗑️
                    </button>
                </div>
            </div>
        `).join('');
    }

    updateAnalyticsView() {
        const container = document.getElementById('analytics-content');
        if (!container) return;

        const analytics = this.analytics;
        
        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Overview</h3>
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Total Expenses</div>
                        <div class="stat-value">${this.formatCurrency(analytics.total_expenses || 0)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Transactions</div>
                        <div class="stat-value">${analytics.expense_count || 0}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Average Daily</div>
                        <div class="stat-value">${this.formatCurrency(analytics.average_per_day || 0)}</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Category Breakdown</h3>
                </div>
                <div class="expenses-list">
                    ${Object.entries(analytics.category_breakdown || {})
                        .sort((a, b) => b[1] - a[1])
                        .map(([category, amount]) => `
                            <div class="expense-item">
                                <div class="expense-icon">${this.getCategoryIcon(category)}</div>
                                <div class="expense-details">
                                    <div class="expense-name">${category}</div>
                                    <div class="expense-meta">Total spent in this category</div>
                                </div>
                                <div class="expense-amount">${this.formatCurrency(amount)}</div>
                            </div>
                        `).join('')}
                </div>
            </div>
        `;
    }

    updateBudgetsView() {
        const container = document.getElementById('budgets-grid');
        if (!container) return;

        if (this.budgets.length === 0) {
            container.innerHTML = this.renderEmptyState('🎯', 'No budgets set', 'Set your first budget to track spending');
            return;
        }

        const currentMonth = new Date().toISOString().slice(0, 7);
        
        container.innerHTML = this.budgets.map(budget => {
            const spent = this.expenses
                .filter(exp => exp.category === budget.category && exp.date.startsWith(currentMonth))
                .reduce((sum, exp) => sum + exp.amount, 0);
            
            const percentage = (spent / budget.amount) * 100;
            const remaining = Math.max(0, budget.amount - spent);
            
            return `
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">${this.getCategoryIcon(budget.category)} ${budget.category}</h3>
                        <span class="stat-change ${percentage > 90 ? 'negative' : percentage > 75 ? 'warning' : 'positive'}">
                            ${percentage.toFixed(1)}%
                        </span>
                    </div>
                    <div class="budget-progress">
                        <div class="stat-value">${this.formatCurrency(remaining)}</div>
                        <div class="stat-label">Remaining</div>
                        <div class="progress-bar" style="margin-top: 1rem; background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
                            <div class="progress-fill" style="width: ${Math.min(percentage, 100)}%; height: 100%; background: ${percentage > 90 ? 'var(--accent-danger)' : percentage > 75 ? 'var(--accent-warning)' : 'var(--accent-success)'}; transition: width 0.3s ease;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.875rem; color: var(--text-tertiary);">
                            <span>Spent: ${this.formatCurrency(spent)}</span>
                            <span>Budget: ${this.formatCurrency(budget.amount)}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Modal methods
    showAddExpenseModal() {
        document.getElementById('add-expense-modal').classList.add('active');
        setTimeout(() => document.getElementById('expense-name')?.focus(), 100);
    }

    hideAddExpenseModal() {
        document.getElementById('add-expense-modal').classList.remove('active');
    }

    showBudgetModal() {
        document.getElementById('budget-modal').classList.add('active');
        setTimeout(() => document.getElementById('budget-category')?.focus(), 100);
    }

    hideBudgetModal() {
        document.getElementById('budget-modal').classList.remove('active');
    }

    hideAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    // Loading and Toast methods
    showLoading() {
        document.getElementById('loading-overlay').classList.add('active');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('active');
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 4000);
    }

    // Utility methods
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

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
            'Savings': '💰',
            'Travel': '✈️',
            'Other': '📦'
        };
        return icons[category] || '📦';
    }

    renderEmptyState(icon, title, description) {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">${icon}</div>
                <div class="empty-state-title">${title}</div>
                <div class="empty-state-description">${description}</div>
            </div>
        `;
    }

    // Global action methods
    async refreshData() {
        console.log('🔄 Refreshing data...');
        await this.loadInitialData();
        this.showToast('Data refreshed successfully! 🔄', 'success');
    }

    async refreshAnalytics() {
        await this.loadAnalytics();
        this.updateAnalyticsView();
        this.showToast('Analytics refreshed! 📊', 'success');
    }

    async refreshInsights() {
        await this.getAIInsights();
    }

    showSettings() {
        this.showToast('Settings coming soon! ⚙️', 'info');
    }

    showAllExpenses() {
        this.showView('expenses');
    }
}

// Global functions for HTML onclick handlers
function showAddExpenseModal() {
    app.showAddExpenseModal();
}

function hideAddExpenseModal() {
    app.hideAddExpenseModal();
}

function showBudgetModal() {
    app.showBudgetModal();
}

function hideBudgetModal() {
    app.hideBudgetModal();
}

function suggestCategory() {
    app.suggestCategory();
}

function getAIInsights() {
    app.getAIInsights();
}

function predictExpenses() {
    app.predictExpenses();
}

function refreshData() {
    app.refreshData();
}

function refreshAnalytics() {
    app.refreshAnalytics();
}

function refreshInsights() {
    app.refreshInsights();
}

function showSettings() {
    app.showSettings();
}

function showAllExpenses() {
    app.showAllExpenses();
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ExpenseTracker();
    console.log('🎉 Smart Expense Tracker loaded successfully!');
});

// Handle app errors gracefully
window.addEventListener('error', (event) => {
    console.error('💥 Application error:', event.error);
    if (app) {
        app.showToast('An unexpected error occurred', 'error');
    }
});

// Handle network errors
window.addEventListener('online', () => {
    if (app) {
        app.showToast('Back online! 🌐', 'success');
        app.refreshData();
    }
});

window.addEventListener('offline', () => {
    if (app) {
        app.showToast('You are offline 📵', 'warning');
    }
});
