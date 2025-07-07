// Global variables
let expenses = [];
let budgets = [];
let chart = null;
const API_BASE_URL = '/api';

// Chart.js reference (Ensure it's loaded globally)
// const Chart = window.Chart;

// Categories with icons and specific classes for coloring
const categories = {
    'Food': { icon: '🍽️', class: 'category-food' },
    'Transportation': { icon: '🚗', class: 'category-transportation' },
    'Bills': { icon: '📋', class: 'category-bills' },
    'Entertainment': { icon: '🎬', class: 'category-entertainment' },
    'Housing': { icon: '🏠', class: 'category-housing' },
    'Groceries': { icon: '🛒', class: 'category-groceries' },
    'Health': { icon: '💊', class: 'category-health' },
    'Education': { icon: '📚', class: 'category-education' },
    'Personal Care': { icon: '🧴', class: 'category-personal-care' },
    'Savings': { icon: '💰', class: 'category-savings' },
    'Travel': { icon: '✈️', class: 'category-travel' },
    'Other': { icon: '📦', class: 'category-other' }
};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadData();
    initializeEventListeners();
    populateMonthSelector();
    populateBudgetCategories();
    updateAll(); // Consolidated update calls
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
    document.getElementById('month-selector').addEventListener('change', updateAll);

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
    toast.className = `toast ${type}`; // Added specific animation class
    toast.textContent = message;
    toastContainer.appendChild(toast);

    // Animation trigger
    setTimeout(() => {
        toast.style.animation = 'none'; // Remove animation for a brief moment to allow re-triggering
        requestAnimationFrame(() => {
            toast.style.animation = '';
        });
    }, 50); // Small delay for re-application

    // Remove toast after some time
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

// --- Modal Functions ---
function showExpenseModal() {
    document.getElementById('expense-modal').classList.add('active');
    document.getElementById('expense-modal').classList.remove('hidden');
    document.getElementById('expense-form').reset(); // Clear form on showing
    setCurrentDate(); // Set date to today when opening
    document.getElementById('expense-category').value = ''; // Reset category dropdown
}

function hideExpenseModal() {
    document.getElementById('expense-modal').classList.remove('active');
    setTimeout(() => {
        document.getElementById('expense-modal').classList.add('hidden');
    }, 300);
    // Resetting form on hide is handled in showExpenseModal to ensure clean slate
}

// Add Expense
async function addExpense(e) {
    e.preventDefault();

    const nameInput = document.getElementById('expense-name');
    const amountInput = document.getElementById('expense-amount');
    const dateInput = document.getElementById('expense-date');
    const categoryInput = document.getElementById('expense-category');
    const descriptionInput = document.getElementById('expense-description');

    const name = nameInput.value.trim();
    const amount = parseFloat(amountInput.value);
    const date = dateInput.value;
    const category = categoryInput.value;
    const description = descriptionInput.value.trim();

    if (!name || isNaN(amount) || amount <= 0 || !date || !category) {
        showToast('Please fill in all required fields with valid data', 'error');
        return;
    }

    const expense = {
        id: Date.now().toString(), // Simple unique ID
        name,
        amount,
        date,
        category,
        description
    };

    expenses.unshift(expense); // Add to the beginning of the array
    saveExpenses();
    hideExpenseModal();

    updateAll(); // Update everything after adding

    showToast('Expense added successfully!');
}

// Delete Expense
function deleteExpense(id) {
    if (confirm('Are you sure you want to delete this expense?')) {
        expenses = expenses.filter(expense => expense.id !== id);
        saveExpenses();
        updateAll();
        showToast('Expense deleted successfully!');
    }
}

// AI Category Suggestion
async function suggestCategory() {
    const nameInput = document.getElementById('expense-name');
    const amountInput = document.getElementById('expense-amount');
    const categoryInput = document.getElementById('expense-category');

    const name = nameInput.value.trim();
    const amount = amountInput.value;

    if (!name) {
        showToast('Please enter expense name first', 'error');
        return;
    }
    if (!amount || isNaN(parseFloat(amount)) || parseFloat(amount) <= 0) {
        showToast('Please enter a valid amount', 'error');
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/expenses/categorize?expense_name=${encodeURIComponent(name)}&amount=${amount}`);
        const data = await response.json();

        if (data.suggested_category && categories[data.suggested_category]) {
            categoryInput.value = data.suggested_category;
            showToast(`AI suggested category: ${data.suggested_category}`);
        } else if (data.suggested_category) {
            // If suggestion isn't in our predefined list, prompt user
            if (confirm(`AI suggested "${data.suggested_category}". Add as 'Other'?`)) {
                categoryInput.value = 'Other';
            } else {
                categoryInput.value = ''; // Clear if user cancels
            }
            showToast(`AI suggestion processed.`);
        }
        else {
            showToast('Could not suggest a category.', 'error');
        }
    } catch (error) {
        console.error('Error suggesting category:', error);
        showToast('Failed to get category suggestion', 'error');
    } finally {
        hideLoading();
    }
}

// --- Budget Functions ---
function showBudgetForm() {
    document.getElementById('budget-form').classList.remove('hidden');
    // Reset form inputs when showing
    document.getElementById('budget-category').value = '';
    document.getElementById('budget-amount').value = '';
    document.getElementById('budget-period').value = 'monthly';
    populateBudgetCategories(); // Re-populate to show current available options
}

function hideBudgetForm() {
    document.getElementById('budget-form').classList.add('hidden');
}

function addBudget() {
    const category = document.getElementById('budget-category').value;
    const amountInput = document.getElementById('budget-amount');
    const amount = parseFloat(amountInput.value);
    const period = document.getElementById('budget-period').value;

    if (!category) {
        showToast('Please select a category', 'error');
        return;
    }
    if (isNaN(amount) || amount <= 0) {
        showToast('Please enter a valid budget amount', 'error');
        return;
    }

    const existingBudgetIndex = budgets.findIndex(b => b.category === category);
    if (existingBudgetIndex !== -1) {
        // Update existing budget if found
        budgets[existingBudgetIndex] = { id: budgets[existingBudgetIndex].id, category, amount, period };
        showToast(`Budget for ${category} updated successfully!`);
    } else {
        // Add new budget
        const budget = {
            id: Date.now().toString(),
            category,
            amount,
            period
        };
        budgets.push(budget);
        showToast(`Budget for ${category} added successfully!`);
    }

    saveBudgets();
    hideBudgetForm();
    populateBudgetCategories(); // Refresh available categories
    updateAll();
}

function deleteBudget(id) {
    if (confirm('Are you sure you want to remove this budget?')) {
        budgets = budgets.filter(b => b.id !== id);
        saveBudgets();
        populateBudgetCategories(); // Refresh available categories
        updateAll();
        showToast('Budget removed successfully!');
    }
}

// --- AI Functions ---
async function predictExpenses() {
    if (expenses.length === 0) {
        showToast('Add some expenses to get predictions', 'error');
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/expenses/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ expenses })
        });

        const prediction = await response.json();

        const predictionResultDiv = document.getElementById('prediction-result');
        let categoryBreakdownHtml = '';
        if (prediction.data && prediction.data.category_breakdown) {
            categoryBreakdownHtml = `<div class="ai-breakdown">`;
            Object.entries(prediction.data.category_breakdown)
                .sort(([,a], [,b]) => b - a) // Sort by amount descending
                .forEach(([cat, amt]) => {
                    const catInfo = categories[cat];
                    const icon = catInfo ? `<span class="category-icon">${catInfo.icon}</span>` : '';
                    const categoryClass = catInfo ? catInfo.class : 'category-other';
                    categoryBreakdownHtml += `
                        <div class="ai-category-item">
                            <span class="ai-category-name"><span class="${categoryClass}">${icon}</span>${cat}</span>
                            <span class="ai-category-amount">₹${amt.toFixed(2)}</span>
                        </div>
                    `;
                });
            categoryBreakdownHtml += `</div>`;
        }

        predictionResultDiv.innerHTML = `
            <div class="budget-item">
                <div class="budget-header">
                    <div class="budget-info"><h3><i class="fas fa-chart-line"></i> Next Month Forecast</h3></div>
                    <div class="budget-stats">
                        <div class="budget-amount">${prediction.confidence ? (prediction.confidence * 100).toFixed(0) + '%' : 'N/A'}</div>
                        <small>Confidence</small>
                    </div>
                </div>
                <p>${prediction.message}</p>
                ${categoryBreakdownHtml}
            </div>
        `;
        predictionResultDiv.classList.remove('hidden');

        showToast('Forecast generated successfully!');
    } catch (error) {
        console.error('Error predicting expenses:', error);
        showToast('Failed to generate forecast', 'error');
    } finally {
        hideLoading();
    }
}

async function refreshInsights() {
    if (expenses.length === 0) {
        showToast('Add some expenses to get insights', 'error');
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/expenses/insights`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ expenses })
        });

        const insights = await response.json();

        const insightsContainer = document.getElementById('ai-insights');
        let insightsHtml = '';

        if (insights.length > 0) {
            insightsHtml = insights.map(insight => {
                const insightType = insight.type.charAt(0).toUpperCase() + insight.type.slice(1);
                const catInfo = categories[insight.data.category] || categories['Other'];
                const icon = `<i class="${catInfo.class} fas fa-category-icon"></i>`; // Placeholder, need to map categories to icons if used here
                
                let dataDisplay = '';
                if (insight.data) {
                    dataDisplay = `<div class="insight-data">`;
                    // Specific handling for common data keys
                    if (insight.data.category) dataDisplay += `<span class="data-item">Category: ${insight.data.category}</span>`;
                    if (insight.data.date) dataDisplay += `<span class="data-item">Date: ${insight.data.date}</span>`;
                    if (insight.data.spending_change) dataDisplay += `<span class="data-item">Spending Change: ₹${insight.data.spending_change.toFixed(2)}</span>`;
                    if (insight.data.budget_status) dataDisplay += `<span class="data-item">Budget Status: ${insight.data.budget_status}</span>`;
                    if (insight.data.top_spending_category) dataDisplay += `<span class="data-item">Top Spending: ${insight.data.top_spending_category}</span>`;
                    
                    // Generic display for other keys
                    Object.entries(insight.data).forEach(([key, value]) => {
                        if (!['category', 'date', 'spending_change', 'budget_status', 'top_spending_category'].includes(key)) {
                            if (typeof value === 'number' && (key.includes('amount') || key.includes('spending'))) {
                                dataDisplay += `<span class="data-item">${key.replace(/_/g, ' ')}: ₹${value.toFixed(2)}</span>`;
                            } else {
                                dataDisplay += `<span class="data-item">${key.replace(/_/g, ' ')}: ${value}</span>`;
                            }
                        }
                    });
                    dataDisplay += `</div>`;
                }

                return `
                    <div class="budget-item">
                        <div class="budget-header">
                            <div class="budget-info">
                                <h3><i class="fas fa-lightbulb"></i> ${insightType}</h3>
                                <small>Confidence: ${(insight.confidence * 100).toFixed(0)}%</small>
                            </div>
                        </div>
                        <p>${insight.message}</p>
                        ${dataDisplay}
                    </div>
                `;
            }).join('');
            document.getElementById('insights-count').textContent = insights.length;
        } else {
            insightsHtml = `<div class="empty-state">
                <i class="fas fa-brain empty-icon"></i>
                <p>No new insights found</p>
                <small>Add more expenses for deeper analysis</small>
            </div>`;
            document.getElementById('insights-count').textContent = 0;
        }
        insightsContainer.innerHTML = insightsHtml;

        showToast('Insights refreshed!');
    } catch (error) {
        console.error('Error getting insights:', error);
        showToast('Failed to get insights', 'error');
    } finally {
        hideLoading();
    }
}

// --- Data Management ---
function exportData() {
    const data = { expenses, budgets };
    const dataStr = JSON.stringify(data, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

    const exportFileDefaultName = `expense_data_${new Date().toISOString().split('T')[0]}.json`;

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
            const importedData = JSON.parse(e.target.result);
            if (importedData.expenses && Array.isArray(importedData.expenses)) {
                // Filter out invalid expenses and merge carefully
                const newExpenses = importedData.expenses.filter(exp =>
                    exp.id && exp.name && typeof exp.amount === 'number' && exp.date && exp.category
                );
                // Merge and avoid duplicates by id
                const existingIds = new Set(expenses.map(exp => exp.id));
                newExpenses.forEach(exp => {
                    if (!existingIds.has(exp.id)) {
                        expenses.push(exp);
                    }
                });
                saveExpenses();
            }
            if (importedData.budgets && Array.isArray(importedData.budgets)) {
                 const newBudgets = importedData.budgets.filter(budget =>
                    budget.id && budget.category && typeof budget.amount === 'number' && budget.period
                );
                const existingBudgetIds = new Set(budgets.map(budget => budget.id));
                newBudgets.forEach(budget => {
                    if (!existingBudgetIds.has(budget.id)) {
                        budgets.push(budget);
                    }
                });
                saveBudgets();
            }

            updateAll();
            showToast('Data imported successfully!');
        } catch (error) {
            console.error('Error importing data:', error);
            showToast('Failed to import data. Invalid file format.', 'error');
        }
    };
    reader.onerror = function() {
        showToast('Error reading file.', 'error');
    };
    reader.readAsText(file);
}


// --- Update Functions ---
function updateAll() {
    updateStats();
    updateExpenseList();
    updateChart();
    updateBudgetList();
    checkBudgetAlerts();
    populateMonthSelector(); // Re-populate in case new months are added via import/data manipulation
}

function updateStats() {
    const totalExpenses = expenses.reduce((sum, expense) => sum + expense.amount, 0);
    const currentMonthValue = document.getElementById('month-selector').value;
    // If month selector is empty, default to current month. Otherwise use selected month.
    const currentMonthPrefix = currentMonthValue ? currentMonthValue.substring(0, 7) : new Date().toISOString().substring(0, 7);

    const monthlyExpenses = expenses.filter(expense => expense.date.startsWith(currentMonthPrefix));
    const monthlyTotal = monthlyExpenses.reduce((sum, expense) => sum + expense.amount, 0);
    
    const uniqueCategories = new Set(expenses.map(e => e.category)).size;

    document.getElementById('total-expenses').textContent = formatCurrency(totalExpenses);
    document.getElementById('month-expenses').textContent = formatCurrency(monthlyTotal);
    document.getElementById('categories-count').textContent = uniqueCategories;
    document.getElementById('insights-count').textContent = document.querySelectorAll('#ai-insights .budget-item').length; // Count displayed insights

    updateAnalytics();
}

function updateAnalytics() {
    const totalExpenses = expenses.reduce((sum, expense) => sum + expense.amount, 0);
    document.getElementById('analytics-total').textContent = formatCurrency(totalExpenses);

    const categoryTotals = {};
    expenses.forEach(expense => {
        categoryTotals[expense.category] = (categoryTotals[expense.category] || 0) + expense.amount;
    });

    const sortedCategories = Object.entries(categoryTotals).sort(([,a], [,b]) => b - a);

    if (sortedCategories.length > 0) {
        const [topCategory, topAmount] = sortedCategories[0];
        document.getElementById('analytics-top-category').textContent = topCategory;
        document.getElementById('analytics-top-amount').textContent = formatCurrency(topAmount);
    } else {
        document.getElementById('analytics-top-category').textContent = 'None';
        document.getElementById('analytics-top-amount').textContent = formatCurrency(0);
    }

    // Monthly breakdown for last 6 months
    const monthlyBreakdownDiv = document.getElementById('monthly-breakdown');
    const monthlyData = {};
    const endOfMonth = new Date();
    const startOfPeriod = new Date();
    startOfPeriod.setMonth(endOfMonth.getMonth() - 5); // Look back 6 months (current + 5 previous)
    startOfPeriod.setDate(1); // Start of the month

    const dateFormatter = new Intl.DateTimeFormat('en-US', { month: 'short', year: 'numeric' });

    expenses.forEach(expense => {
        const expenseDate = new Date(expense.date);
        // Only include expenses within the last 6 months (for breakdown visualization)
        if (expenseDate >= startOfPeriod && expenseDate <= endOfMonth) {
            const monthYear = expense.date.substring(0, 7); // YYYY-MM
            if (!monthlyData[monthYear]) {
                monthlyData[monthYear] = { total: 0, count: 0, displayDate: dateFormatter.format(expenseDate) };
            }
            monthlyData[monthYear].total += expense.amount;
            monthlyData[monthYear].count++;
        }
    });

    const sortedMonths = Object.keys(monthlyData).sort((a, b) => b.localeCompare(a)); // Sort by month descending

    if (sortedMonths.length > 0) {
        monthlyBreakdownDiv.innerHTML = `
            <h3 style="color: var(--text-secondary); margin-bottom: 1rem;">Monthly Spending Overview</h3>
            ${sortedMonths.map(monthYear => {
                const data = monthlyData[monthYear];
                const catInfo = categories[monthYear]; // Assuming 'monthYear' can be mapped to a category for icon
                const icon = ''; // No category icons for monthly breakdown itself

                return `
                    <div class="budget-item">
                        <div class="budget-header">
                            <div class="budget-info"><h3>${data.displayDate}</h3></div>
                            <div class="budget-stats">
                                <div class="budget-amount">${formatCurrency(data.total)}</div>
                                <small>${data.count} expenses</small>
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        `;
    } else {
        monthlyBreakdownDiv.innerHTML = ''; // Clear if no data
    }
}

function populateMonthSelector() {
    const selector = document.getElementById('month-selector');
    const usedMonths = [...new Set(expenses.map(expense => expense.date.substring(0, 7)))];
    const currentMonthYear = new Date().toISOString().substring(0, 7);

    if (!usedMonths.includes(currentMonthYear)) {
        usedMonths.push(currentMonthYear);
    }

    usedMonths.sort((a, b) => b.localeCompare(a)); // Sort descending

    const monthOptions = usedMonths.map(month => {
        // Helper to display full month name and year
        const dateForDisplay = new Date(month + '-02'); // Use a consistent day for parsing
        const monthName = dateForDisplay.toLocaleString('en-US', { month: 'long', year: 'numeric' });
        return `<option value="${month}">${monthName}</option>`;
    }).join('');

    selector.innerHTML = monthOptions;
    // Set the current month as default, if it exists in options, otherwise fallback to latest
    if (usedMonths.includes(currentMonthYear)) {
        selector.value = currentMonthYear;
    } else if (usedMonths.length > 0) {
        selector.value = usedMonths[0]; // Default to the most recent month available
    }
}

function populateBudgetCategories() {
    const selector = document.getElementById('budget-category');
    const usedCategoriesInBudgets = new Set(budgets.map(b => b.category)); // Use Set for efficient lookup

    const categoryOptions = Object.entries(categories).map(([category, { icon }]) => {
        const isDisabled = usedCategoriesInBudgets.has(category) ? 'disabled' : '';
        const className = `category-option ${categories[category].class}`; // Add category class
        return `<option value="${category}" ${isDisabled} class="${className}">${category}</option>`;
    }).join('');

    selector.innerHTML = `<option value="">Select Category</option>${categoryOptions}`;
}

function updateExpenseList() {
    const selectedMonth = document.getElementById('month-selector').value;
    const currentMonthPrefix = selectedMonth ? selectedMonth.substring(0, 7) : new Date().toISOString().substring(0, 7);

    const filteredExpenses = expenses.filter(expense => expense.date.startsWith(currentMonthPrefix));
    const sortedExpenses = filteredExpenses.sort((a, b) => new Date(b.date) - new Date(a.date));

    const container = document.getElementById('expense-list-container');

    if (sortedExpenses.length === 0) {
        container.innerHTML = `<div class="empty-state">
            <i class="fas fa-receipt empty-icon"></i>
            <p>No expenses for ${selectedMonth ? new Date(selectedMonth + '-02').toLocaleString('en-US', { month: 'long', year: 'numeric' }) : 'this month'}</p>
            <small>Click "Add Expense" to get started</small>
        </div>`;
        return;
    }

    container.innerHTML = sortedExpenses.map(expense => {
        const categoryInfo = categories[expense.category];
        const categoryIcon = categoryInfo ? categoryInfo.icon : '📦';
        const categoryClass = categoryInfo ? categoryInfo.class : 'category-other';
        
        return `
            <div class="expense-item">
                <div class="expense-icon ${categoryClass}">${categoryIcon}</div>
                <div class="expense-details">
                    <div class="expense-name">${expense.name}</div>
                    <div class="expense-meta">
                        <span class="${categoryClass}"><i class="fas fa-tag"></i> ${expense.category}</span>
                        <span><i class="fas fa-calendar-alt"></i> ${new Date(expense.date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}</span>
                    </div>
                </div>
                <div class="expense-amount">${formatCurrency(expense.amount)}</div>
                <button class="delete-expense" onclick="deleteExpense('${expense.id}')" aria-label="Delete expense">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
    }).join('');
}

function updateChart() {
    const selectedMonth = document.getElementById('month-selector').value;
    const currentMonthPrefix = selectedMonth ? selectedMonth.substring(0, 7) : new Date().toISOString().substring(0, 7);

    const filteredExpenses = expenses.filter(expense => expense.date.startsWith(currentMonthPrefix));

    const categoryData = {};
    filteredExpenses.forEach(expense => {
        categoryData[expense.category] = (categoryData[expense.category] || 0) + expense.amount;
    });

    const chartCanvas = document.getElementById('expense-chart');
    const chartEmpty = document.getElementById('chart-empty');
    const categorySummary = document.getElementById('category-summary');

    if (Object.keys(categoryData).length === 0) {
        chartCanvas.style.display = 'none';
        chartEmpty.style.display = 'flex'; // Make empty state visible
        categorySummary.innerHTML = '';
        if (chart) chart.destroy(); // Destroy previous chart instance
        return;
    }

    chartCanvas.style.display = 'block';
    chartEmpty.style.display = 'none';

    const ctx = chartCanvas.getContext('2d');
    if (chart) chart.destroy(); // Ensure only one chart instance exists

    // Assign consistent colors based on the 'categories' object
    const availableColors = [
        '#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444',
        '#EC4899', '#06B6D4', '#F97316', '#84CC16', '#22C55E',
        '#6366F1', '#6B7280'
    ];
    const chartColors = {};
    let colorIndex = 0;

    const labels = Object.keys(categoryData);
    const datasets = [{
        data: Object.values(categoryData),
        // Assign colors based on categories object or fallback
        backgroundColor: labels.map(label => {
            if (categories[label] && categories[label].class) {
                // Return a CSS variable if defined for specific categories for potentially brighter themes
                // For now, we map directly for a consistent chart palette
                return availableColors[colorIndex++ % availableColors.length];
            }
            return availableColors[colorIndex++ % availableColors.length];
        }),
        borderColor: 'var(--bg-secondary)', // Chart background separation
        borderWidth: 3, // Thicker border
        hoverBorderWidth: 3
    }];

    chart = new Chart(ctx, {
        type: 'doughnut',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }, // Hide default legend to use custom summary
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)', // Darker tooltip background
                    titleColor: 'var(--text-primary)',
                    bodyColor: 'var(--text-primary)',
                    borderColor: 'var(--border)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((sum, value) => sum + value, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${formatCurrency(context.parsed)} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '70%', // Creates the donut hole effect
            hoverOffset: 15 // Slightly enlarge segment on hover
        }
    });

    // Custom category summary for better readability
    const totalSpending = Object.values(categoryData).reduce((sum, value) => sum + value, 0);
    categorySummary.innerHTML = Object.entries(categoryData)
        .sort(([,a], [,b]) => b - a) // Sort by amount descending
        .map(([category, amount], index) => {
            const percentage = ((amount / totalSpending) * 100).toFixed(1);
            const categoryInfo = categories[category];
            const catIcon = categoryInfo ? categoryInfo.icon : '📦';
            const catClass = categoryInfo ? categoryInfo.class : 'category-other';
            
            return `
                <div class="budget-item">
                    <div class="budget-header">
                        <div class="budget-info">
                            <span class="${catClass}">${catIcon}</span> <h3>${category}</h3>
                        </div>
                        <div class="budget-stats">
                            <div class="budget-amount">${formatCurrency(amount)}</div>
                            <small>${percentage}%</small>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
}

function updateBudgetList() {
    const container = document.getElementById('budget-list');

    if (budgets.length === 0) {
        container.innerHTML = `<div class="empty-state">
            <i class="fas fa-chart-bar empty-icon"></i>
            <p>No budgets set</p>
            <small>Create budgets to track your spending</small>
        </div>`;
        return;
    }

    // Ensure the budget list is sorted by category name for consistency
    budgets.sort((a, b) => a.category.localeCompare(b.category));

    container.innerHTML = budgets.map(budget => {
        const spent = getCurrentMonthExpenses(budget.category);
        const remaining = budget.amount - spent;
        let percentage = 0;
        if (budget.amount > 0) { // Avoid division by zero
            percentage = Math.min((spent / budget.amount) * 100, 100); // Cap at 100%
        }

        let status = 'good';
        if (percentage >= 100) status = 'danger';
        else if (percentage >= 80) status = 'warning';
        
        const categoryInfo = categories[budget.category];
        const catIcon = categoryInfo ? categoryInfo.icon : '📦';
        const catClass = categoryInfo ? categoryInfo.class : 'category-other';

        return `
            <div class="budget-item">
                <button class="delete-budget" onclick="deleteBudget('${budget.id}')" aria-label="Delete budget">
                    <i class="fas fa-times"></i>
                </button>
                <div class="budget-header">
                    <div class="budget-info">
                        <span class="${catClass}">${catIcon}</span>
                        <h3>${budget.category}</h3>
                    </div>
                    <div class="budget-stats">
                        <div class="budget-amount">${formatCurrency(budget.amount)}</div>
                        <small>${budget.period.charAt(0).toUpperCase() + budget.period.slice(1)}</small>
                    </div>
                </div>
                <div class="budget-progress">
                    <div class="progress-bar">
                        <div class="progress-fill ${status}" style="width: ${percentage}%;"></div>
                    </div>
                </div>
                <div class="budget-progress-header">
                    <span>Spent: ${formatCurrency(spent)}</span>
                    <span>Remaining: ${formatCurrency(remaining)}</span>
                </div>
            </div>
        `;
    }).join('');
}

function getCurrentMonthExpenses(category) {
    const currentMonthPrefix = new Date().toISOString().substring(0, 7);
    return expenses
        .filter(expense => expense.date.startsWith(currentMonthPrefix) && expense.category === category)
        .reduce((sum, expense) => sum + expense.amount, 0);
}

function checkBudgetAlerts() {
    const alertsContainer = document.getElementById('budget-alerts');
    const alertsContent = document.getElementById('alerts-container');
    let alertsHtml = '';

    // Ensure budgets are checked against the current month for alerts
    budgets.forEach(budget => {
        const spent = getCurrentMonthExpenses(budget.category);
        let percentage = 0;
        if (budget.amount > 0) {
            percentage = (spent / budget.amount) * 100;
        }
        
        if (percentage >= 80) { // Threshold for alerts
            const alertType = percentage >= 100 ? 'danger' : 'warning';
            const catInfo = categories[budget.category] || categories['Other'];
            const icon = catInfo.icon;
            const catClass = catInfo.class;

            alertsHtml += `
                <div class="budget-item">
                    <div class="budget-header">
                        <div class="budget-info">
                             <span class="${catClass}">${icon}</span> <h3>${budget.category}</h3>
                        </div>
                        <div class="budget-stats">
                             <div class="budget-amount">${formatCurrency(spent)} / ${formatCurrency(budget.amount)}</div>
                        </div>
                    </div>
                    <div class="budget-progress">
                         <div class="progress-bar" style="height: 6px;">
                              <div class="progress-fill ${alertType}" style="width: ${Math.min(percentage, 100)}%;"></div>
                         </div>
                    </div>
                    <p class="budget-remaining ${alertType}" style="font-size: 0.85rem;">${alertType === 'danger' ? 'Over budget!' : `Nearing limit (${percentage.toFixed(0)}%)`}</p>
                </div>
            `;
        }
    });

    if (alertsHtml) {
        alertsContent.innerHTML = alertsHtml;
        alertsContainer.classList.remove('hidden');
    } else {
        alertsContainer.innerHTML = ''; // Clear content if no alerts
        alertsContainer.classList.add('hidden');
    }
}


// --- Helper Functions ---
function formatCurrency(amount) {
    return `₹${amount.toFixed(2)}`;
}

// Ensure Chart is accessible globally if needed elsewhere by JS
// (This is generally handled by the <script src="...chart.js"></script> tag)
// window.Chart = Chart; // Usually not needed if script tag is present and loaded before scripts.js
