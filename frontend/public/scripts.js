// Smart Expense Tracker - Modern JavaScript Application
class ExpenseTracker {
    constructor() {
        this.API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:8001/api' : '/api';
        this.expenses = [];
        this.budgets = [];
        this.currentView = 'dashboard';
        this.chart = null;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setCurrentDate();
        await this.loadData();
        this.updateDashboard();
        this.populateSampleData();
        this.initChart();
    }

    setupEventListeners() {
        // Expense form submission
        const expenseForm = document.getElementById('expense-form');
        if (expenseForm) {
            expenseForm.addEventListener('submit', this.handleAddExpense.bind(this));
        }

        // Modal close events
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

        // Validate required fields
        if (!expense.name || !expense.amount || !expense.date || !expense.category) {
            this.showToast('Please fill all required fields', 'error');
            return;
        }

        try {
            this.showLoading();
            const response = await fetch(`${this.API_BASE_URL}/expenses`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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
                const categorySelect = document.getElementById('expense-category');
                categorySelect.value = data.suggested_category;
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
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ expenses: this.expenses }),
            });

            if (response.ok) {
                const insights = await response.json();
                this.displayInsights(insights);
                this.showInsightsModal();
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
        this.updateBalances();
        this.updateTransactions();
        this.updateSidebarStats();
        this.updateCategoryBreakdown();
        this.updateChart();
    }

    updateBalances() {
        const totalAmount = this.expenses.reduce((sum, expense) => sum + expense.amount, 0);
        const currentMonth = new Date().toISOString().slice(0, 7);
        const monthlyAmount = this.expenses
            .filter(expense => expense.date.startsWith(currentMonth))
            .reduce((sum, expense) => sum + expense.amount, 0);

        // Update main balance card
        const mainBalance = document.getElementById('main-balance');
        if (mainBalance) {
            mainBalance.textContent = this.formatCurrency(totalAmount || 15780);
        }

        // Update secondary balance card
        const secondaryBalance = document.getElementById('secondary-balance');
        if (secondaryBalance) {
            secondaryBalance.textContent = this.formatCurrency(monthlyAmount || 123424);
        }

        // Update sidebar total
        const totalDisplay = document.getElementById('total-display');
        if (totalDisplay) {
            totalDisplay.textContent = this.formatCurrency(totalAmount || 14810);
        }
    }

    updateTransactions() {
        const transactionsList = document.getElementById('transactions-list');
        if (!transactionsList) return;

        // Get recent transactions (or create sample data)
        const recentTransactions = this.expenses.slice(0, 5);
        
        if (recentTransactions.length === 0) {
            // Show sample transactions
            transactionsList.innerHTML = this.getSampleTransactions();
            return;
        }

        transactionsList.innerHTML = recentTransactions.map(expense => `
            <div class="transaction-item">
                <img src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face" 
                     alt="User" class="transaction-avatar">
                <div class="transaction-name">${expense.name}</div>
                <div class="transaction-date">${this.formatDate(expense.date)}</div>
                <div class="transaction-status success">Success</div>
                <div class="transaction-amount negative">-${this.formatCurrency(expense.amount)}</div>
                <button class="transaction-delete" onclick="app.deleteExpense('${expense.id}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2"/>
                    </svg>
                </button>
            </div>
        `).join('');
    }

    getSampleTransactions() {
        const sampleTransactions = [
            { name: 'James Smith', date: 'Mar 18, 2023', status: 'Success', amount: 1080.0 },
            { name: 'George Holster', date: 'Mar 19, 2023', status: 'Process', amount: 880.0 },
            { name: 'Daniela Gordienko', date: 'Mar 21, 2023', status: 'Failed', amount: 1340.0 }
        ];

        return sampleTransactions.map(transaction => `
            <div class="transaction-item">
                <img src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face" 
                     alt="${transaction.name}" class="transaction-avatar">
                <div class="transaction-name">${transaction.name}</div>
                <div class="transaction-date">${transaction.date}</div>
                <div class="transaction-status ${transaction.status.toLowerCase()}">${transaction.status}</div>
                <div class="transaction-amount negative">-₹${transaction.amount.toFixed(2)}</div>
            </div>
        `).join('');
    }

    updateSidebarStats() {
        const chartCenterAmount = document.getElementById('chart-center-amount');
        if (chartCenterAmount) {
            const totalSpent = this.expenses.reduce((sum, exp) => sum + exp.amount, 0);
            chartCenterAmount.textContent = this.formatCurrency(totalSpent || 9560);
        }
    }

    updateCategoryBreakdown() {
        const categoryBreakdown = document.getElementById('category-breakdown');
        if (!categoryBreakdown) return;

        // Calculate category totals
        const categoryTotals = {};
        this.expenses.forEach(expense => {
            categoryTotals[expense.category] = (categoryTotals[expense.category] || 0) + expense.amount;
        });

        // Convert to array and sort by amount
        const categories = Object.entries(categoryTotals)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 6);

        if (categories.length === 0) {
            categoryBreakdown.innerHTML = this.getSampleCategoryBreakdown();
            return;
        }

        categoryBreakdown.innerHTML = categories.map(([category, amount]) => `
            <div class="category-item">
                <div class="category-icon" style="background: ${this.getCategoryColor(category)};">
                    ${this.getCategoryIcon(category)}
                </div>
                <div class="category-info">
                    <div class="category-name">${category}</div>
                    <div class="category-time">11 minutes ago</div>
                </div>
                <div class="category-amount negative">-${this.formatCurrency(amount)}</div>
            </div>
        `).join('');
    }

    getSampleCategoryBreakdown() {
        const sampleCategories = [
            { name: 'Spotify', icon: '🎵', color: '#1DB954', amount: 321.5 },
            { name: 'Bitcoin', icon: '₿', color: '#F7931A', amount: 123.5 },
            { name: 'Apple', icon: '🍎', color: '#007AFF', amount: 552.5 },
            { name: 'Apple', icon: '🍎', color: '#007AFF', amount: 242.5 },
            { name: 'Binance', icon: '🔸', color: '#F3BA2F', amount: 160.5 }
        ];

        return sampleCategories.map(item => `
            <div class="category-item">
                <div class="category-icon" style="background: ${item.color};">
                    ${item.icon}
                </div>
                <div class="category-info">
                    <div class="category-name">${item.name}</div>
                    <div class="category-time">11 minutes ago</div>
                </div>
                <div class="category-amount negative">-₹${item.amount}</div>
            </div>
        `).join('');
    }

    initChart() {
        const canvas = document.getElementById('expense-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
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
                        '#60A5FA', // Payment at the time
                        '#1F2937', // Money transaction
                        '#10B981',
                        '#F59E0B',
                        '#EF4444'
                    ],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.formattedValue + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    getChartData() {
        if (this.expenses.length === 0) {
            return {
                labels: ['Payment at the time', 'Money transaction'],
                values: [65, 35]
            };
        }

        // Calculate category percentages
        const categoryTotals = {};
        const total = this.expenses.reduce((sum, exp) => {
            categoryTotals[exp.category] = (categoryTotals[exp.category] || 0) + exp.amount;
            return sum + exp.amount;
        }, 0);

        const categories = Object.entries(categoryTotals)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5);

        return {
            labels: categories.map(([category]) => category),
            values: categories.map(([, amount]) => Math.round((amount / total) * 100))
        };
    }

    updateChart() {
        if (!this.chart) return;

        const data = this.getChartData();
        this.chart.data.labels = data.labels;
        this.chart.data.datasets[0].data = data.values;
        this.chart.update();
    }

    displayInsights(insights) {
        const insightsContent = document.getElementById('insights-content');
        if (!insightsContent) return;

        if (insights.length === 0) {
            insightsContent.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🤖</div>
                    <div class="empty-state-title">No insights available</div>
                    <div class="empty-state-description">Add more expenses to get AI insights</div>
                </div>
            `;
            return;
        }

        insightsContent.innerHTML = insights.map(insight => `
            <div class="insight-item">
                <div class="insight-message">${insight.message}</div>
                <div class="insight-confidence">Confidence: ${Math.round(insight.confidence * 100)}%</div>
            </div>
        `).join('');
    }

    populateSampleData() {
        // Only populate if no existing expenses
        if (this.expenses.length > 0) return;

        const sampleExpenses = [
            {
                id: '1',
                name: 'Morning Coffee',
                amount: 150,
                date: '2024-01-15',
                category: 'Food',
                description: 'Daily coffee from local cafe'
            },
            {
                id: '2',
                name: 'Uber Ride',
                amount: 280,
                date: '2024-01-14',
                category: 'Transportation',
                description: 'Ride to office'
            },
            {
                id: '3',
                name: 'Groceries',
                amount: 1200,
                date: '2024-01-13',
                category: 'Groceries',
                description: 'Weekly grocery shopping'
            }
        ];

        this.expenses = sampleExpenses;
        this.updateDashboard();
    }

    // UI Helper Methods
    showAddExpenseModal() {
        const modal = document.getElementById('add-expense-modal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    hideAddExpenseModal() {
        const modal = document.getElementById('add-expense-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    showInsightsModal() {
        const modal = document.getElementById('insights-modal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    hideInsightsModal() {
        const modal = document.getElementById('insights-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    hideAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
    }

    showLoading() {
        const loading = document.getElementById('loading-overlay');
        if (loading) {
            loading.classList.add('active');
        }
    }

    hideLoading() {
        const loading = document.getElementById('loading-overlay');
        if (loading) {
            loading.classList.remove('active');
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // Navigation Methods
    showDashboard() {
        this.updateNavigation('dashboard');
        this.currentView = 'dashboard';
    }

    showExpenses() {
        this.updateNavigation('expenses');
        this.currentView = 'expenses';
        this.showToast('Expenses view - showing recent expenses', 'info');
    }

    showBudgets() {
        this.updateNavigation('budgets');
        this.currentView = 'budgets';
        this.showToast('Budget management - coming soon!', 'info');
    }

    showAnalytics() {
        this.updateNavigation('analytics');
        this.currentView = 'analytics';
        this.getInsights();
    }

    showSettings() {
        this.updateNavigation('settings');
        this.currentView = 'settings';
        this.showToast('Settings - coming soon!', 'info');
    }

    showProfile() {
        this.showToast('Profile settings - coming soon!', 'info');
    }

    showTransfer() {
        this.setActiveAction('transfer');
        this.showToast('Transfer feature - coming soon!', 'info');
    }

    showUtility() {
        this.setActiveAction('utility');
        this.showToast('Utility payments - coming soon!', 'info');
    }

    showTaxes() {
        this.setActiveAction('taxes');
        this.showToast('Tax management - coming soon!', 'info');
    }

    showTransport() {
        this.setActiveAction('transport');
        this.showToast('Transport booking - coming soon!', 'info');
    }

    updateNavigation(activeView) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to current view (simplified mapping)
        const viewIndex = ['dashboard', 'expenses', 'budgets', 'analytics', 'settings'].indexOf(activeView);
        if (viewIndex !== -1) {
            const navItems = document.querySelectorAll('.nav-item');
            if (navItems[viewIndex]) {
                navItems[viewIndex].classList.add('active');
            }
        }
    }

    setActiveAction(action) {
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Simple mapping for now
        const actionBtns = document.querySelectorAll('.action-btn');
        const actionIndex = ['transfer', 'utility', 'taxes', 'transport'].indexOf(action);
        if (actionIndex !== -1 && actionBtns[actionIndex]) {
            actionBtns[actionIndex].classList.add('active');
        }
    }

    // Utility Methods
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount).replace('₹', '₹');
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
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

    getCategoryColor(category) {
        const colors = {
            'Food': '#FF6B35',
            'Transportation': '#007AFF',
            'Bills': '#5856D6',
            'Entertainment': '#FF453A',
            'Housing': '#30D158',
            'Groceries': '#FF9F0A',
            'Health': '#64D2FF',
            'Education': '#5856D6',
            'Personal Care': '#FF453A',
            'Savings': '#30D158',
            'Travel': '#007AFF',
            'Other': '#8E8E93'
        };
        return colors[category] || '#8E8E93';
    }
}

// Global functions for HTML onclick handlers
function showAddExpenseModal() {
    app.showAddExpenseModal();
}

function hideAddExpenseModal() {
    app.hideAddExpenseModal();
}

function hideInsightsModal() {
    app.hideInsightsModal();
}

function suggestCategory() {
    app.suggestCategory();
}

function showDashboard() {
    app.showDashboard();
}

function showExpenses() {
    app.showExpenses();
}

function showBudgets() {
    app.showBudgets();
}

function showAnalytics() {
    app.showAnalytics();
}

function showSettings() {
    app.showSettings();
}

function showProfile() {
    app.showProfile();
}

function showTransfer() {
    app.showTransfer();
}

function showUtility() {
    app.showUtility();
}

function showTaxes() {
    app.showTaxes();
}

function showTransport() {
    app.showTransport();
}

// Initialize the app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ExpenseTracker();
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExpenseTracker;
}
