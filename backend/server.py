<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Expense Tracker</title>
    <meta name="description" content="AI-powered expense tracking with smart insights">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💰</text></svg>">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-primary: #0a0a0b;
            --bg-secondary: #1a1a1b;
            --bg-tertiary: #2a2a2b;
            --bg-glass: rgba(26, 26, 27, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #b3b3b3; /* Slightly lighter than original */
            --text-muted: #8a8a8a;
            --accent-blue: #4a9eff;
            --accent-purple: #8b5cf6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-orange: #f59e0b;
            --border: rgba(255, 255, 255, 0.1);
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            --shadow-hover: 0 12px 40px rgba(0, 0, 0, 0.4);
            --gradient-primary: linear-gradient(135deg, #4a9eff 0%, #8b5cf6 100%);
            --gradient-card: linear-gradient(135deg, rgba(74, 158, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .app-container {
            max-width: 400px;
            min-height: 100vh;
            margin: 0 auto;
            background: var(--bg-primary);
            position: relative;
            border-left: 1px solid var(--border);
            border-right: 1px solid var(--border);
        }

        .main-content {
            padding: 20px;
            padding-bottom: 120px;
        }

        .greeting-section {
            margin-bottom: 35px; /* Increased margin */
            padding: 20px;
            background: var(--gradient-card);
            border-radius: 20px;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
        }

        .greeting-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .greeting-text {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .greeting-emoji {
            font-size: 24px;
        }

        .greeting-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .greeting-subtitle {
            font-size: 14px;
            color: var(--text-secondary);
        }

        .settings-btn {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .settings-btn:hover {
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }

        .balance-card {
            background: var(--bg-secondary);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 30px; /* Increased margin */
            border: 1px solid var(--border);
            position: relative;
            overflow: hidden;
        }

        .balance-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-primary);
        }

        .balance-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .balance-icon {
            color: var(--accent-blue);
            font-size: 20px;
        }

        .balance-label {
            font-size: 14px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .balance-amount {
            font-size: 32px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 10px;
        }

        .balance-subtitle {
            font-size: 12px;
            color: var(--text-muted);
        }

        .quick-actions {
            display: flex;
            gap: 15px;
            margin-bottom: 35px; /* Increased margin */
        }

        .action-btn {
            flex: 1;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            color: var(--text-primary);
        }

        .action-btn:hover {
            background: var(--bg-tertiary);
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }

        .action-btn i {
            font-size: 20px;
            color: var(--accent-blue);
        }

        .action-btn span {
            font-size: 12px;
            font-weight: 500;
            color: var(--text-secondary);
        }

        .action-btn.primary {
            background: var(--gradient-primary);
            color: white;
        }

        .action-btn.primary i,
        .action-btn.primary span {
            color: white;
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section-title i {
            color: var(--accent-blue);
        }

        .expense-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .expense-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: all 0.3s ease;
        }

        .expense-item:hover {
            background: var(--bg-tertiary);
            transform: translateY(-1px);
        }

        .expense-icon {
            width: 45px;
            height: 45px;
            border-radius: 12px;
            background: var(--bg-tertiary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: var(--accent-blue);
            border: 1px solid var(--border);
        }

        .expense-details {
            flex: 1;
        }

        .expense-name {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 5px;
        }

        .expense-meta {
            font-size: 12px;
            color: var(--text-muted);
            display: flex;
            gap: 15px;
        }

        .expense-amount {
            font-size: 16px;
            font-weight: 700;
            color: var(--text-primary);
        }

        .expense-amount.negative {
            color: var(--accent-red);
        }

        .expense-amount.positive {
            color: var(--accent-green);
        }

        .delete-btn {
            background: var(--accent-red);
            border: none;
            color: white;
            padding: 8px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .delete-btn:hover {
            background: #c53030;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 35px; /* Increased margin */
        }

        .stat-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        }

        .stat-icon {
            font-size: 24px;
            margin-bottom: 10px;
        }

        .stat-icon.income { color: var(--accent-green); }
        .stat-icon.expense { color: var(--accent-red); }
        .stat-icon.savings { color: var(--accent-blue); }
        .stat-icon.budget { color: var(--accent-purple); }

        .stat-value {
            font-size: 20px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 12px;
            color: var(--text-secondary);
        }

        .bottom-nav {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 380px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 25px;
            padding: 12px;
            display: flex;
            justify-content: space-around;
            backdrop-filter: blur(10px);
            box-shadow: var(--shadow);
        }

        .nav-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            padding: 12px;
            border-radius: 15px;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
            min-width: 60px;
        }

        .nav-btn.active {
            background: var(--gradient-primary);
            color: white;
        }

        .nav-btn i {
            font-size: 18px;
        }

        .nav-btn span {
            font-size: 10px;
            font-weight: 500;
        }

        .tab-page {
            display: none;
        }

        .tab-page.active {
            display: block;
        }

        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }

        .modal.active {
            opacity: 1;
            visibility: visible;
        }

        .modal-content {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 20px;
            width: 90%;
            max-width: 400px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: var(--shadow-hover);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid var(--border);
        }

        .modal-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .close-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 20px;
            cursor: pointer;
            padding: 5px;
            border-radius: 50%;
            transition: all 0.3s ease;
        }

        .close-btn:hover {
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }

        .modal-body {
            padding: 20px;
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            font-weight: 500;
            color: var(--text-secondary);
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.2);
        }

        .form-group input::placeholder,
        .form-group textarea::placeholder {
            color: var(--text-muted);
        }

        .form-group input[type="date"] {
            color: var(--text-primary);
        }

        .form-buttons {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }

        .btn {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn-primary {
            background: var(--gradient-primary);
            color: white;
        }

        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }

        .btn-danger {
            background: var(--accent-red);
            color: white;
        }

        .btn:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow);
        }

        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
        }

        .empty-icon {
            font-size: 48px;
            margin-bottom: 15px;
            opacity: 0.5;
        }

        .empty-text {
            font-size: 16px;
            margin-bottom: 10px;
        }

        .empty-subtext {
            font-size: 14px;
            color: var(--text-muted);
        }

        .budget-section {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 25px;
        }

        .budget-progress {
            margin-bottom: 16px;
        }

        .budget-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .budget-info h4 {
            color: var(--text-primary);
            font-size: 16px;
            font-weight: 600;
        }

        .budget-info p {
            color: var(--text-secondary);
            font-size: 12px;
        }

        .budget-amount {
            text-align: right;
        }

        .budget-spent {
            font-size: 16px;
            font-weight: 700;
            color: var(--text-primary);
        }

        .budget-total {
            font-size: 12px;
            color: var(--text-secondary);
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 8px;
        }

        .progress-fill {
            height: 100%;
            background: var(--gradient-primary);
            border-radius: 4px;
            transition: width 0.5s ease;
        }

        .progress-fill.warning {
            background: linear-gradient(90deg, var(--accent-orange), #ff8c42);
        }

        .progress-fill.danger {
            background: linear-gradient(90deg, #ff4757, #ff6b7a);
        }

        .chart-container {
            margin-top: 20px;
            padding: 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 15px;
            margin-bottom: 25px;
        }

        /* Insights Tab Styles */
        .insights-section {
            background: var(--bg-secondary);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px; /* Reduced margin */
            border: 1px solid var(--border);
        }

        .insights-section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .insights-section-header h4 {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .insights-section-header i {
            color: var(--accent-blue); /* Or a relevant color */
        }

        .refresh-btn {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 12px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .refresh-btn:hover {
            background: var(--accent-blue);
            color: var(--text-primary);
        }

        /* Health Score Card */
        .health-score-card {
            background: var(--gradient-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border);
        }

        .score-display {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }

        .score-circle {
            width: 60px; /* Slightly smaller */
            height: 60px; /* Slightly smaller */
            border-radius: 50%;
            background: var(--gradient-primary); /* Default gradient */
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px; /* Adjusted font size */
            font-weight: 700;
            color: var(--text-primary);
            box-shadow: var(--shadow); /* Added shadow for better visual */
        }

        /* Color mapping for score */
        .score-circle.excellent { background: linear-gradient(135deg, #10b981 0%, #059669 100%); } /* Green */
        .score-circle.good { background: linear-gradient(135deg, #4a9eff 0%, #047857 100%); }      /* Blue */
        .score-circle.fair { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }    /* Orange */
        .score-circle.poor { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }     /* Red */


        .score-info h5 {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .score-info p {
            font-size: 14px;
            color: var(--text-secondary);
        }

        .health-factors {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .health-factor {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 12px;
            color: var(--text-secondary);
        }

        /* Insights Container */
        .insights-container {
            max-height: 300px; /* Fixed height */
            overflow-y: auto;
            scroll-behavior: smooth; /* Smooth scrolling */
            padding-right: 10px; /* Space for scrollbar */
        }

        .insight-card {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }

        .insight-card h5 {
            font-size: 14px;
            font-weight: 600;
            color: var(--accent-blue);
            margin-bottom: 8px;
        }

        .insight-card p {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.4;
        }

        .empty-insights {
            text-align: center;
            padding: 30px 20px;
            color: var(--text-muted);
        }

        .empty-insights i {
            font-size: 24px;
            margin-bottom: 10px;
        }

        /* Predictive Analytics Card */
        .prediction-card {
            background: var(--gradient-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border);
        }

        .prediction-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .prediction-header i {
            color: var(--accent-purple);
            font-size: 18px;
        }

        .prediction-header h5 {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .prediction-content {
            font-size: 14px; /* Adjusted font size */
            color: var(--text-secondary);
            line-height: 1.5;
        }

        /* Savings Advice Card */
        .savings-advice-container {
            max-height: 400px; /* Fixed height */
            overflow-y: auto;
            scroll-behavior: smooth;
            padding-right: 10px; /* Space for scrollbar */
        }

        .advice-card {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }

        .advice-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }

        .advice-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--accent-green);
        }

        .advice-priority {
            background: var(--accent-orange);
            color: var(--text-primary);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .advice-priority.high { background: var(--accent-red); }
        .advice-priority.medium { background: var(--accent-orange); }
        .advice-priority.low { background: var(--accent-green); }

        .advice-message {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.4;
            margin-bottom: 8px;
        }

        .advice-savings {
            font-size: 12px;
            color: var(--accent-green);
            font-weight: 600;
        }

        .empty-advice {
            text-align: center;
            padding: 30px 20px;
            color: var(--text-muted);
        }

        .empty-advice i {
            font-size: 24px;
            margin-bottom: 10px;
        }

        /* Smart Categorization Demo */
        .categorization-demo {
            background: var(--bg-tertiary);
            border-radius: 10px;
            padding: 15px;
        }

        .demo-input {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap; /* Allow wrapping on smaller screens */
        }

        .demo-input input {
            flex: 1;
            min-width: 120px; /* Ensure inputs don't get too small */
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px;
            color: var(--text-primary);
            font-size: 14px;
        }

        .demo-input input::placeholder {
            color: var(--text-muted);
        }

        .categorization-result {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            min-height: 70px; /* Ensure consistent height */
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .categorization-result.success {
            border-color: var(--accent-green);
            background: rgba(16, 185, 129, 0.1); /* Light green background */
        }

        .categorization-result p {
            font-size: 14px;
            color: var(--text-secondary);
            margin: 0;
        }

        .categorization-result .suggested-category {
            font-size: 16px;
            font-weight: 600;
            color: var(--accent-green);
            margin-top: 5px;
        }

        /* Calendar Adjustments */
        .calendar-date {
            text-align: center;
            padding: 8px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            min-height: 45px; /* Ensure consistent height */
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            width: 100%;
            box-sizing: border-box;
            overflow: hidden; /* Prevent text overflow */
        }

        .calendar-expenses {
          font-size: 10px;
          margin-top: 3px; /* Reduced margin to fit within height */
          line-height: 1.2;
          font-weight: 600;
          max-width: 100%; /* Prevent text from exceeding cell */
          overflow: hidden;
          text-overflow: ellipsis;
        }


        @media (max-width: 480px) {
            .app-container {
                max-width: 100%;
                border-left: none;
                border-right: none;
            }

            .main-content {
                padding: 15px;
                padding-bottom: 100px;
            }

            .balance-amount {
                font-size: 28px;
            }

            .bottom-nav {
                width: 95%;
                bottom: 15px;
            }

            .calendar-date {
                padding: 8px;
                min-height: 45px;
            }

            .calendar-expenses {
                font-size: 9px;
            }
        }
    </style>
</head>
<body>
    <div class="app-container">
        <main class="main-content">
            <!-- Home Tab -->
            <div id="tab-home" class="tab-page active">
                <div class="greeting-section">
                    <div class="greeting-header">
                        <div class="greeting-text">
                            <span class="greeting-emoji">👋</span>
                            <div>
                                <div class="greeting-title" id="greeting-title">Good morning!</div>
                                <div class="greeting-subtitle">Here's your spending</div>
                            </div>
                        </div>
                        <button class="settings-btn" onclick="openModal('settings-modal')">
                            <i class="fas fa-cog"></i>
                        </button>
                    </div>
                </div>

                <div class="balance-card">
                    <div class="balance-header">
                        <i class="fas fa-wallet balance-icon"></i>
                        <span class="balance-label">Current Balance</span>
                    </div>
                    <div class="balance-amount" id="balance-amount">₹0.00</div>
                    <div class="balance-subtitle">**** 1910</div>
                </div>

                <div class="quick-actions">
                    <button class="action-btn" onclick="openModal('income-modal')">
                        <i class="fas fa-plus"></i>
                        <span>Add Income</span>
                    </button>
                    <button class="action-btn primary" onclick="openModal('expense-modal')">
                        <i class="fas fa-minus"></i>
                        <span>Add Expense</span>
                    </button>
                    <button class="action-btn" onclick="switchTab('history')">
                        <i class="fas fa-exchange-alt"></i>
                        <span>Transfer</span>
                    </button>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon income">
                            <i class="fas fa-arrow-up"></i>
                        </div>
                        <div class="stat-value" id="total-income">₹0.00</div>
                        <div class="stat-label">Income</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon expense">
                            <i class="fas fa-arrow-down"></i>
                        </div>
                        <div class="stat-value" id="total-expense">₹0.00</div>
                        <div class="stat-label">Expenses</div>
                    </div>
                </div>

                <div class="section-header">
                    <h3 class="section-title">
                        <i class="fas fa-history"></i>
                        Recent Transactions
                    </h3>
                </div>
                <div class="expense-list" id="recent-expenses">
                    <!-- Transactions will be populated by JS -->
                </div>

                <div class="chart-container">
                    <canvas id="expense-chart"></canvas>
                </div>
            </div>

            <!-- Insights Tab (Replaced AI Tab) -->
            <div id="tab-insights" class="tab-page">
                <div class="section-header">
                    <h3 class="section-title">
                        <i class="fas fa-chart-line"></i>
                        Financial Insights
                    </h3>
                </div>
                
                <!-- Loading Indicator -->
                <div id="insights-loading" class="ai-loading" style="display: none;">
                    <div class="loading-spinner">
                        <i class="fas fa-cog fa-spin"></i>
                    </div>
                    <p>Analyzing your financial data...</p>
                </div>

                <!-- Insights Content -->
                <div id="insights-content" style="display: none;">
                    <!-- Financial Health Score -->
                    <div class="insights-section">
                        <div class="insights-section-header">
                            <h4><i class="fas fa-heartbeat"></i> Financial Health Score</h4>
                            <button class="refresh-btn" onclick="refreshInsights()">
                                <i class="fas fa-sync-alt"></i>
                            </button>
                        </div>
                        <div id="health-score-card" class="health-score-card">
                            <div class="score-display">
                                <div class="score-circle" id="health-score-circle">
                                    <span id="health-score">--</span>
                                </div>
                                <div class="score-info">
                                    <h5 id="health-grade">--</h5>
                                    <p id="health-message">Click refresh to analyze</p>
                                </div>
                            </div>
                            <div id="health-factors" class="health-factors"></div>
                        </div>
                    </div>

                    <!-- Smart Insights -->
                    <div class="insights-section">
                        <div class="insights-section-header">
                            <h4><i class="fas fa-lightbulb"></i> Smart Insights</h4>
                        </div>
                        <div id="insights-container" class="insights-container">
                            <div class="empty-insights">
                                <i class="fas fa-chart-line"></i>
                                <p>No insights available yet</p>
                            </div>
                        </div>
                    </div>

                    <!-- Predictive Analytics -->
                    <div class="insights-section">
                        <div class="insights-section-header">
                            <h4><i class="fas fa-chart-line"></i> Predictive Analytics</h4>
                        </div>
                        <div id="prediction-card" class="prediction-card">
                            <div class="prediction-header">
                                <i class="fas fa-crystal-ball"></i>
                                <h5>Month-End Prediction</h5>
                            </div>
                            <div id="prediction-content" class="prediction-content">
                                <p>Click refresh to get predictions</p>
                            </div>
                        </div>
                    </div>

                    <!-- Savings Advice -->
                    <div class="insights-section">
                        <div class="insights-section-header">
                            <h4><i class="fas fa-piggy-bank"></i> Savings Advice</h4>
                        </div>
                        <div id="savings-advice-container" class="savings-advice-container">
                            <div class="empty-advice">
                                <i class="fas fa-coins"></i>
                                <p>No advice available yet</p>
                            </div>
                        </div>
                    </div>

                    <!-- Smart Categorization Demo -->
                    <div class="insights-section">
                        <div class="insights-section-header">
                            <h4><i class="fas fa-tags"></i> Smart Categorization</h4>
                        </div>
                        <div class="categorization-demo">
                            <div class="demo-input">
                                <input type="text" id="expense-name-input" placeholder="Enter expense name (e.g., Coffee at Starbucks)">
                                <input type="number" id="expense-amount-input" placeholder="Amount" step="0.01">
                                <button onclick="testCategorization()" class="btn btn-primary">
                                    <i class="fas fa-magic"></i> Categorize
                                </button>
                            </div>
                            <div id="categorization-result" class="categorization-result">
                                <p>Try entering an expense to see AI categorization</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>


            <!-- Budget Tab -->
            <div id="tab-budget" class="tab-page">
                <div class="section-header">
                    <h3 class="section-title">
                        <i class="fas fa-chart-pie"></i>
                        Budget Overview
                    </h3>
                </div>
                <div class="budget-section">
                    <div id="budget-list">
                        <!-- Budgets will be populated by JS -->
                    </div>
                    <button class="btn btn-primary" onclick="openModal('budget-modal')">
                        <i class="fas fa-plus"></i>
                        Add Budget
                    </button>
                </div>
            </div>

            <!-- History Tab -->
            <div id="tab-history" class="tab-page">
                <div class="section-header">
                    <h3 class="section-title">
                        <i class="fas fa-history"></i>
                        Transaction History
                    </h3>
                </div>
                <div class="calendar-container">
                    <div class="calendar-header">
                        <button class="calendar-nav" onclick="changeMonth(-1)"><i class="fas fa-chevron-left"></i></button>
                        <span id="calendar-month-year"></span>
                        <button class="calendar-nav" onclick="changeMonth(1)"><i class="fas fa-chevron-right"></i></button>
                    </div>
                    <div class="calendar-grid" id="calendar-days">
                        <!-- Calendar days will be populated by JS -->
                    </div>
                </div>
                <div class="section-header">
                    <h3 class="section-title">
                        <i class="fas fa-list"></i>
                        Transactions
                    </h3>
                </div>
                <div class="expense-list" id="all-expenses">
                    <!-- Transactions will be populated by JS -->
                </div>
            </div>
        </main>

        <!-- Bottom Navigation -->
        <nav class="bottom-nav">
            <button class="nav-btn active" onclick="switchTab('home')">
                <i class="fas fa-home"></i>
                <span>Home</span>
            </button>
            <!-- Updated link to Insights Tab -->
            <button class="nav-btn" onclick="switchTab('insights')">
                <i class="fas fa-chart-line"></i>
                <span>Insights</span>
            </button>
            <button class="nav-btn" onclick="switchTab('budget')">
                <i class="fas fa-chart-pie"></i>
                <span>Budget</span>
            </button>
            <button class="nav-btn" onclick="switchTab('history')">
                <i class="fas fa-history"></i>
                <span>History</span>
            </button>
        </nav>
    </div>

    <!-- Add Expense Modal -->
    <div id="expense-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">Add Expense</h2>
                <button class="close-btn" onclick="closeModal('expense-modal')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <form id="expense-form">
                    <div class="form-group">
                        <label for="expense-name">Expense Name</label>
                        <input type="text" id="expense-name" placeholder="e.g., Lunch at Cafe" required>
                    </div>
                    <div class="form-group">
                        <label for="expense-amount">Amount (₹)</label>
                        <input type="number" id="expense-amount" placeholder="0.00" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label for="expense-category">Category</label>
                        <select id="expense-category" required>
                            <option value="">Select Category</option>
                            <option value="food">Food & Dining</option>
                            <option value="transportation">Transportation</option>
                            <option value="entertainment">Entertainment</option>
                            <option value="bills">Bills & Utilities</option>
                            <option value="shopping">Shopping</option>
                            <option value="health">Health & Fitness</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="expense-date">Date</label>
                        <input type="date" id="expense-date" required>
                    </div>
                    <div class="form-group">
                        <label for="expense-description">Description (Optional)</label>
                        <textarea id="expense-description" rows="3" placeholder="Add a note..."></textarea>
                    </div>
                    <div class="form-buttons">
                        <button type="button" class="btn btn-secondary" onclick="closeModal('expense-modal')">Cancel</button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-plus"></i>
                            Add Expense
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Add Income Modal -->
    <div id="income-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">Add Income</h2>
                <button class="close-btn" onclick="closeModal('income-modal')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <form id="income-form">
                    <div class="form-group">
                        <label for="income-name">Income Source</label>
                        <input type="text" id="income-name" placeholder="e.g., Salary, Freelance" required>
                    </div>
                    <div class="form-group">
                        <label for="income-amount">Amount (₹)</label>
                        <input type="number" id="income-amount" placeholder="0.00" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label for="income-category">Category</label>
                        <select id="income-category" required>
                            <option value="">Select Category</option>
                            <option value="salary">Salary</option>
                            <option value="freelance">Freelance</option>
                            <option value="investment">Investment</option>
                            <option value="gift">Gift</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="income-date">Date</label>
                        <input type="date" id="income-date" required>
                    </div>
                    <div class="form-buttons">
                        <button type="button" class="btn btn-secondary" onclick="closeModal('income-modal')">Cancel</button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-plus"></i>
                            Add Income
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Settings Modal -->
    <div id="settings-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">Settings</h2>
                <button class="close-btn" onclick="closeModal('settings-modal')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label for="user-name">Your Name</label>
                    <input type="text" id="user-name" placeholder="Enter your name">
                    <button class="btn btn-primary" style="margin-top: 12px;" onclick="saveUserName()">Save Name</button>
                </div>
                <div class="form-group">
                    <label>Data Management</label>
                    <div class="form-buttons">
                        <button class="btn btn-primary" onclick="exportData()">Export Data</button>
                        <input type="file" id="import-data" accept=".json" style="display: none;" onchange="importData(event)">
                        <button class="btn btn-secondary" onclick="document.getElementById('import-data').click()">Import Data</button>
                    </div>
                </div>
                <div class="form-group">
                    <button class="btn btn-danger" onclick="resetData()">Reset All Data</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Budget Modal -->
    <div id="budget-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">Add Budget</h2>
                <button class="close-btn" onclick="closeModal('budget-modal')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <form id="budget-form">
                    <div class="form-group">
                        <label for="budget-category">Category</label>
                        <select id="budget-category" required>
                            <option value="">Select Category</option>
                            <option value="food">Food & Dining</option>
                            <option value="transportation">Transportation</option>
                            <option value="entertainment">Entertainment</option>
                            <option value="bills">Bills & Utilities</option>
                            <option value="shopping">Shopping</option>
                            <option value="health">Health & Fitness</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="budget-amount">Budget Amount (₹)</label>
                        <input type="number" id="budget-amount" placeholder="0.00" step="0.01" required>
                    </div>
                    <div class="form-buttons">
                        <button type="button" class="btn btn-secondary" onclick="closeModal('budget-modal')">Cancel</button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-plus"></i>
                            Add Budget
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script>
    // Initial data
    let balance = 0;
    let totalIncome = 0;
    let totalExpenses = 0;
    let transactions = [];
    let budgets = {};
    let userName = '';
    let expenseChart = null;
    let currentMonth = new Date().getMonth();
    let currentYear = new Date().getFullYear();
    let selectedDate = null;
    let previousMonthData = null;

    // Category icons mapping
    const categoryIcons = {
        food: 'fas fa-utensils',
        transportation: 'fas fa-car',
        entertainment: 'fas fa-gamepad',
        bills: 'fas fa-file-invoice',
        shopping: 'fas fa-shopping-cart',
        health: 'fas fa-heartbeat',
        other: 'fas fa-question',
        salary: 'fas fa-wallet',
        freelance: 'fas fa-laptop',
        investment: 'fas fa-chart-line',
        gift: 'fas fa-gift'
    };

    // --- Local Storage Functions ---
    function saveToLocalStorage() {
        const data = {
            balance,
            totalIncome,
            totalExpenses,
            transactions,
            budgets,
            userName,
            previousMonthData,
            currentMonth,
            currentYear
        };
        localStorage.setItem('expenseTrackerData', JSON.stringify(data));
    }

    function loadFromLocalStorage() {
        const data = localStorage.getItem('expenseTrackerData');
        if (data) {
            const parsed = JSON.parse(data);
            balance = parsed.balance || 0;
            totalIncome = parsed.totalIncome || 0;
            totalExpenses = parsed.totalExpenses || 0;
            transactions = parsed.transactions || [];
            budgets = parsed.budgets || {};
            userName = parsed.userName || '';
            previousMonthData = parsed.previousMonthData || null;
            currentMonth = parsed.currentMonth ?? new Date().getMonth();
            currentYear = parsed.currentYear ?? new Date().getFullYear();
        }
    }

    // --- Utility Functions ---
    function getIconForCategory(category) {
        return categoryIcons[category] || 'fas fa-question';
    }

    function getISTDate() {
        // Returns a Date object representing current time in IST
        return new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
    }

    function formatDate(date) {
        // Formats a Date object into a readable string, showing 'Today' if applicable
        const today = getISTDate();
        if (date.toDateString() === today.toDateString()) {
            return 'Today';
        }
        return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
    }

    function getGreeting() {
        // Provides a time-based greeting
        const hour = getISTDate().getHours();
        let greeting;
        if (hour < 12) greeting = 'Good morning';
        else if (hour < 18) greeting = 'Good afternoon';
        else greeting = 'Good evening';
        return userName ? `${greeting}, ${userName}!` : `${greeting}!`;
    }

    function checkAndResetData() {
        // Checks if the month/year has changed and resets data if necessary
        const today = getISTDate();
        const currentDay = today.getDate();
        const newMonth = today.getMonth();
        const newYear = today.getFullYear();

        if (newMonth !== currentMonth || newYear !== currentYear) {
            // Store previous month's data before resetting
            previousMonthData = {
                balance,
                totalIncome,
                totalExpenses,
                transactions,
                budgets,
                userName,
                month: currentMonth,
                year: currentYear
            };
            // Reset current month's data
            balance = 0;
            totalIncome = 0;
            totalExpenses = 0;
            transactions = [];
            budgets = {};
            currentMonth = newMonth;
            currentYear = newYear;
            saveToLocalStorage();
            updateUI();
        }

        // Special condition to clear June 2025 data after July 10, 2025
        if (newMonth === 6 && newYear === 2025 && currentDay > 10 && previousMonthData && previousMonthData.month === 5 && previousMonthData.year === 2025) {
            previousMonthData = null;
            saveToLocalStorage();
        }
    }

    // --- Data Management Functions ---
    function exportData() {
        // Exports the current or previous month's data as a JSON file
        const today = getISTDate();
        const currentDay = today.getDate();
        const currentMonth = today.getMonth();
        const currentYear = today.getFullYear();

        // Specific condition for exporting June 2025 data
        if (previousMonthData && previousMonthData.month === 5 && previousMonthData.year === 2025 && currentMonth === 6 && currentYear === 2025 && currentDay <= 10) {
            const data = previousMonthData;
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `expense_tracker_june_2025_${getISTDate().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            alert('June 2025 data exported successfully.');
        } else if (currentMonth === previousMonthData?.month && currentYear === previousMonthData?.year) {
            // Export current month's data if it matches the last saved period
            const data = {
                balance,
                totalIncome,
                totalExpenses,
                transactions,
                budgets,
                userName,
                month: currentMonth,
                year: currentYear
            };
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `expense_tracker_${getISTDate().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            alert('Current month data exported successfully.');
        } else {
            alert('No data available to export for the requested period.');
        }
    }

    function importData(event) {
        // Imports data from a JSON file
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                balance = data.balance || 0;
                totalIncome = data.totalIncome || 0;
                totalExpenses = data.totalExpenses || 0;
                transactions = data.transactions || [];
                budgets = data.budgets || {};
                userName = data.userName || '';
                // Set current month/year from imported data, or default to current if missing
                currentMonth = data.month ?? getISTDate().getMonth();
                currentYear = data.year ?? getISTDate().getFullYear();
                saveToLocalStorage();
                updateUI();
                alert('Data imported successfully.');
            } catch (err) {
                alert('Invalid file format. Please upload a valid JSON file.');
            }
        };
        reader.readAsText(file);
    }

    // --- UI Rendering Functions ---
    function renderTransactionList(containerId, transactionsToRender, showDeleteButton = false) {
        // Renders a list of transactions into a specified container
        const container = document.getElementById(containerId);
        container.innerHTML = ''; // Clear existing content
        if (transactionsToRender.length === 0) {
            // Show empty state if no transactions
            const emptyState = document.createElement('div');
            emptyState.className = 'empty-state';
            emptyState.innerHTML = `
                <div class="empty-icon"><i class="fas fa-list"></i></div>
                <div class="empty-text">No Transactions</div>
                <div class="empty-subtext">Add a transaction to get started</div>
            `;
            container.appendChild(emptyState);
            return;
        }
        // Create and append each transaction item
        transactionsToRender.forEach(transaction => {
            const expenseItem = document.createElement('div');
            expenseItem.className = 'expense-item';
            const amountClass = transaction.amount < 0 ? 'negative' : 'positive';
            expenseItem.innerHTML = `
                <div class="expense-icon">
                    <i class="${transaction.icon}"></i>
                </div>
                <div class="expense-details">
                    <div class="expense-name">${transaction.name}</div>
                    <div class="expense-meta">
                        <span>${transaction.category}</span>
                        <span>${transaction.date}</span>
                    </div>
                </div>
                <div class="expense-amount ${amountClass}">${transaction.amount < 0 ? '-' : '+'}₹${Math.abs(transaction.amount).toFixed(2)}</div>
                ${showDeleteButton ? `<button class="delete-btn" onclick="deleteTransaction(${transaction.id})"><i class="fas fa-trash"></i></button>` : ''}
            `;
            container.appendChild(expenseItem);
        });
    }

    function deleteTransaction(id) {
        // Deletes a transaction after user confirmation
        if (confirm('Are you sure you want to delete this transaction?')) {
            const transaction = transactions.find(t => t.id === id);
            if (transaction) {
                // Update balance and totals
                balance -= transaction.amount;
                if (transaction.amount > 0) {
                    totalIncome -= transaction.amount;
                } else {
                    totalExpenses -= Math.abs(transaction.amount);
                }
                // Remove from array
                transactions = transactions.filter(t => t.id !== id);
                saveToLocalStorage();
                updateUI();
            }
        }
    }

    function updateBalanceUI() {
        // Updates the balance display on the home screen
        document.getElementById('balance-amount').textContent = `₹${balance.toFixed(2)}`;
    }

    function updateStatsUI() {
        // Updates the total income and expense displays
        document.getElementById('total-income').textContent = `₹${totalIncome.toFixed(2)}`;
        document.getElementById('total-expense').textContent = `₹${totalExpenses.toFixed(2)}`;
    }

    function calculateCategoryExpenses(category) {
        // Calculates total expenses for a given category in the current month
        return transactions
            .filter(t => {
                const transactionDate = new Date(t.date === 'Today' ? getISTDate() : t.date);
                return transactionDate.getMonth() === currentMonth &&
                       transactionDate.getFullYear() === currentYear &&
                       t.amount < 0 &&
                       t.category === category;
            })
            .reduce((total, t) => total + Math.abs(t.amount), 0);
    }

    function renderBudgetList() {
        // Renders the list of budget progress cards
        const budgetList = document.getElementById('budget-list');
        budgetList.innerHTML = ''; // Clear existing
        if (Object.keys(budgets).length === 0) {
            // Show empty state if no budgets are set
            const emptyState = document.createElement('div');
            emptyState.className = 'empty-state';
            emptyState.innerHTML = `
                <div class="empty-icon"><i class="fas fa-chart-pie"></i></div>
                <div class="empty-text">No Budgets</div>
                <div class="empty-subtext">Add a budget to start tracking</div>
            `;
            budgetList.appendChild(emptyState);
            return;
        }
        // Create and append budget progress cards
        Object.keys(budgets).forEach(category => {
            const spent = calculateCategoryExpenses(category);
            const total = budgets[category];
            const percentage = total > 0 ? (spent / total) * 100 : 0;
            const progressClass = percentage > 90 ? 'danger' : percentage > 75 ? 'warning' : '';
            const budgetCard = document.createElement('div');
            budgetCard.className = 'budget-progress';
            budgetCard.innerHTML = `
                <div class="budget-header">
                    <div class="budget-info">
                        <h4>${category.charAt(0).toUpperCase() + category.slice(1)}</h4>
                        <p>Monthly budget</p>
                    </div>
                    <div class="budget-amount">
                        <div class="budget-spent">₹${spent.toFixed(2)}</div>
                        <div class="budget-total">of ₹${total.toFixed(2)}</div>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${progressClass}" style="width: ${Math.min(percentage, 100)}%"></div>
                </div>
            `;
            budgetList.appendChild(budgetCard);
        });
    }

    function addBudget(category, amount) {
        // Adds a new budget
        budgets[category] = amount;
        saveToLocalStorage();
        renderBudgetList();
    }

    function renderExpenseChart() {
        // Renders the pie chart for monthly expense breakdown
        const monthlyTransactions = transactions.filter(t => {
            const transactionDate = new Date(t.date === 'Today' ? getISTDate() : t.date);
            return transactionDate.getMonth() === currentMonth &&
                   transactionDate.getFullYear() === currentYear &&
                   t.amount < 0;
        });

        const categoryTotals = monthlyTransactions.reduce((acc, t) => {
            acc[t.category] = (acc[t.category] || 0) + Math.abs(t.amount);
            return acc;
        }, {});

        const labels = Object.keys(categoryTotals);
        const data = Object.values(categoryTotals);

        const ctx = document.getElementById('expense-chart').getContext('2d');

        if (expenseChart) {
            expenseChart.destroy(); // Destroy previous chart if it exists
        }

        if (labels.length === 0) {
            // Display a message if there's no data
            ctx.canvas.parentElement.innerHTML = `
                <div class="empty-insights">
                    <i class="fas fa-chart-pie"></i>
                    <p>No spending data for this month.</p>
                </div>
            `;
            return;
        }

        expenseChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'var(--text-secondary)', // Chart.js uses CSS vars indirectly
                            font: { size: 12, family: 'Inter' }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'var(--bg-glass)',
                        titleColor: 'var(--text-primary)',
                        bodyColor: 'var(--text-secondary)',
                        borderColor: 'var(--border)',
                        borderWidth: 1,
                        cornerRadius: 10,
                        padding: 10
                    }
                }
            }
        });
    }

    function renderCalendar() {
        // Renders the monthly calendar view
        const calendarDays = document.getElementById('calendar-days');
        const monthYear = document.getElementById('calendar-month-year');
        calendarDays.innerHTML = ''; // Clear previous month's content

        // Set month and year header
        const date = new Date(currentYear, currentMonth, 1);
        date.setTime(date.getTime() + (5.5 * 60 * 60 * 1000)); // Adjust to IST
        const monthName = date.toLocaleString('en-US', { month: 'long', timeZone: 'Asia/Kolkata' });
        monthYear.textContent = `${monthName} ${currentYear}`;

        // Add weekday headers (Sun, Mon, ...)
        const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        weekdays.forEach(day => {
            const dayEl = document.createElement('div');
            dayEl.className = 'calendar-day';
            dayEl.textContent = day;
            calendarDays.appendChild(dayEl);
        });

        // Add empty cells for days before the first of the month
        const firstDay = date.getDay(); // 0 for Sunday, 1 for Monday, etc.
        for (let i = 0; i < firstDay; i++) {
            const emptyCell = document.createElement('div');
            emptyCell.className = 'calendar-date';
            calendarDays.appendChild(emptyCell);
        }

        // Add days of the month
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        // Group transactions by date for quick lookup
        const transactionDates = transactions.reduce((acc, t) => {
            const tDate = new Date(t.date === 'Today' ? getISTDate() : t.date);
            // Ensure consistency in date format for grouping (YYYY-M-D)
            const dateStr = `${tDate.getFullYear()}-${tDate.getMonth()}-${tDate.getDate()}`;
            if (!acc[dateStr]) acc[dateStr] = [];
            acc[dateStr].push(t);
            return acc;
        }, {});

        for (let i = 1; i <= daysInMonth; i++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'calendar-date';
            // Create a Date object for the current day in the calendar
            const checkDate = new Date(currentYear, currentMonth, i);
            checkDate.setTime(checkDate.getTime() + (5.5 * 60 * 60 * 1000)); // Adjust to IST
            const dateStr = `${checkDate.getFullYear()}-${checkDate.getMonth()}-${checkDate.getDate()}`;
            
            let expenseSummary = '';
            let amountClass = '';
            
            if (transactionDates[dateStr]) {
                // If there are transactions for this date
                const dayTransactions = transactionDates[dateStr];
                // Calculate net amount for the day
                const netAmount = dayTransactions.reduce((sum, t) => sum + t.amount, 0).toFixed(0);
                expenseSummary = `${Math.abs(netAmount)}`; // Display absolute amount
                amountClass = netAmount >= 0 ? 'income' : 'expense'; // Class for color coding
                dayCell.classList.add('has-transactions'); // Add class for visual indicator
            }
            
            // Populate day cell content
            dayCell.innerHTML = `
                <span>${i}</span>
                <div class="calendar-expenses ${amountClass}">${expenseSummary}</div>
            `;
            
            // Highlight the selected date
            if (selectedDate && selectedDate.getDate() === i && selectedDate.getMonth() === currentMonth && selectedDate.getFullYear() === currentYear) {
                dayCell.classList.add('active');
            }
            
            // Add click listener to select the date
            dayCell.addEventListener('click', () => {
                selectedDate = new Date(currentYear, currentMonth, i);
                selectedDate.setTime(selectedDate.getTime() + (5.5 * 60 * 60 * 1000)); // Adjust to IST
                updateTransactionListForDate(); // Update transaction list below calendar
                renderCalendar(); // Re-render calendar to update active class
            });
            calendarDays.appendChild(dayCell);
        }
    }

    function changeMonth(delta) {
        // Changes the current month and re-renders the calendar and transaction list
        currentMonth += delta;
        if (currentMonth < 0) { // If moved to previous year
            currentMonth = 11;
            currentYear--;
        } else if (currentMonth > 11) { // If moved to next year
            currentMonth = 0;
            currentYear++;
        }
        selectedDate = null; // Deselect any previously selected date
        saveToLocalStorage();
        updateTransactionListForDate();
        renderCalendar();
    }

    function updateTransactionListForDate() {
        // Filters and displays transactions for the selected date
        let filteredTransactions = transactions;
        if (selectedDate) {
            const dateStr = `${selectedDate.getFullYear()}-${selectedDate.getMonth()}-${selectedDate.getDate()}`;
            filteredTransactions = transactions.filter(t => {
                const tDate = new Date(t.date === 'Today' ? getISTDate() : t.date);
                return `${tDate.getFullYear()}-${tDate.getMonth()}-${tDate.getDate()}` === dateStr;
            });
        }
        renderTransactionList('all-expenses', filteredTransactions, true); // Show delete buttons in history
    }

    function addTransaction(name, amount, category, date) {
        // Adds a new transaction (expense or income) to the list
        // Generates a unique ID (simple counter based, not robust for concurrent use)
        const id = transactions.length ? Math.max(...transactions.map(t => t.id)) + 1 : 1;
        const icon = getIconForCategory(category);
        const formattedDate = formatDate(new Date(date)); // Format the date for display
        const newTransaction = { id, name, amount, category, date: formattedDate, icon };
        
        transactions.push(newTransaction); // Add to the transactions array
        
        // Update global balance and totals
        balance += amount;
        if (amount > 0) {
            totalIncome += amount;
        } else {
            totalExpenses += Math.abs(amount);
        }
        
        saveToLocalStorage(); // Save updated data
        updateUI(); // Refresh the UI
    }

    function saveUserName() {
        // Saves the user's name from the settings modal
        const nameInput = document.getElementById('user-name').value.trim();
        if (nameInput) {
            userName = nameInput;
            saveToLocalStorage();
            updateGreeting();
            closeModal('settings-modal');
        } else {
            alert('Please enter a valid name.');
        }
    }

    function resetData() {
        // Resets all application data after confirmation
        if (confirm('Are you sure you want to reset all data? This action cannot be undone.')) {
            balance = 0;
            totalIncome = 0;
            totalExpenses = 0;
            transactions = [];
            budgets = {};
            userName = '';
            previousMonthData = null;
            localStorage.removeItem('expenseTrackerData'); // Clear data from localStorage
            updateUI();
            closeModal('settings-modal');
        }
    }

    function updateGreeting() {
        // Updates the greeting message in the header
        document.getElementById('greeting-title').textContent = getGreeting();
    }

    function updateUI() {
        // Main function to update all parts of the UI
        checkAndResetData(); // Ensure data is current for the month
        updateBalanceUI();
        updateStatsUI();
        renderTransactionList('recent-expenses', transactions.slice(-5).reverse(), false); // Show last 5 transactions
        updateTransactionListForDate(); // Show transactions for selected date (or all if none selected)
        renderBudgetList();
        renderExpenseChart();
        renderCalendar();
        updateGreeting();

        // Set default date for date input fields in modals
        const todayStr = getISTDate().toISOString().split('T')[0];
        document.getElementById('expense-date').value = todayStr;
        document.getElementById('income-date').value = todayStr;
    }

    function switchTab(tabName) {
        // Handles switching between different tabs (Home, Insights, Budget, History)
        document.querySelectorAll('.tab-page').forEach(tab => {
            tab.classList.remove('active'); // Hide all tabs
        });
        document.getElementById('tab-' + tabName).classList.add('active'); // Show the selected tab

        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active'); // Remove active class from all nav buttons
        });
        // Add active class to the clicked nav button
        const navBtn = document.querySelector(`.nav-btn[onclick="switchTab('${tabName}')"]`);
        if (navBtn) {
            navBtn.classList.add('active');
        }
        
        // Trigger specific rendering functions when a tab is activated
        if (tabName === 'home') {
            renderTransactionList('recent-expenses', transactions.slice(-5).reverse(), false);
            renderExpenseChart();
        } else if (tabName === 'history') {
            selectedDate = null; // Clear date selection when entering history tab
            updateTransactionListForDate();
            renderCalendar();
        } else if (tabName === 'budget') {
            renderBudgetList();
        } else if (tabName === 'insights') {
            // Automatically refresh insights when the tab is shown
            refreshInsights();
        }
    }

    function openModal(modalId) {
        // Makes a modal visible
        document.getElementById(modalId).classList.add('active');
    }

    function closeModal(modalId) {
        // Hides a modal and resets its form
        document.getElementById(modalId).classList.remove('active');
        // Reset forms to prevent residual data
        if (modalId === 'expense-modal') document.getElementById('expense-form').reset();
        if (modalId === 'income-modal') document.getElementById('income-form').reset();
        if (modalId === 'budget-modal') document.getElementById('budget-form').reset();
        // Reset date inputs to current date after closing
        document.getElementById('expense-date').value = getISTDate().toISOString().split('T')[0];
        document.getElementById('income-date').value = getISTDate().toISOString().split('T')[0];
    }

    // --- Event Listeners ---
    // Close modals when clicking outside of them
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('active');
        }
    });

    // Handle Expense Form Submission
    document.getElementById('expense-form').addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent default form submission
        const name = document.getElementById('expense-name').value.trim();
        const amount = parseFloat(document.getElementById('expense-amount').value);
        const category = document.getElementById('expense-category').value;
        const date = document.getElementById('expense-date').value;
        
        // Basic validation
        if (name && !isNaN(amount) && amount > 0 && category && date) {
            addTransaction(name, -amount, category, date); // Add as expense (negative amount)
            closeModal('expense-modal'); // Close modal after successful add
        } else {
            alert('Please fill in all required fields with valid values.');
        }
    });

    // Handle Income Form Submission
    document.getElementById('income-form').addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent default form submission
        const name = document.getElementById('income-name').value.trim();
        const amount = parseFloat(document.getElementById('income-amount').value);
        const category = document.getElementById('income-category').value;
        const date = document.getElementById('income-date').value;
        
        // Basic validation
        if (name && !isNaN(amount) && amount > 0 && category && date) {
            addTransaction(name, amount, category, date); // Add as income (positive amount)
            closeModal('income-modal'); // Close modal after successful add
        } else {
            alert('Please fill in all required fields with valid values.');
        }
    });

    // Handle Budget Form Submission
    document.getElementById('budget-form').addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent default form submission
        const category = document.getElementById('budget-category').value;
        const amount = parseFloat(document.getElementById('budget-amount').value);
        
        // Basic validation
        if (category && !isNaN(amount) && amount > 0) {
            addBudget(category, amount);
            closeModal('budget-modal');
        } else {
            alert('Please select a category and enter a valid budget amount.');
        }
    });

    // --- Insights Tab Specific Functions ---
    // NOTE: These functions assume the backend has endpoints for AI analysis.
    // The provided backend (server.py) does *not* have these endpoints.
    // If you need these AI features, you'll need to implement them in the backend.
    // For now, these are placeholders demonstrating the frontend structure.
    
    const API_BASE_URL = '/api'; // Using relative path for backend API

    async function refreshInsights() {
        // Shows loading spinner and fetches insights data
        const loadingEl = document.getElementById('insights-loading');
        const contentEl = document.getElementById('insights-content');
        
        loadingEl.style.display = 'block';
        contentEl.style.display = 'none';
        
        try {
            // This endpoint is assumed to exist in the backend
            // It should return comprehensive analysis data
            const response = await fetch(`${API_BASE_URL}/analytics/comprehensive`, {
                method: 'GET' // Assuming GET for analysis data
            });
            
            const result = await response.json();
            
            if (result.success) {
                updateHealthScore(result.data.health_score);
                updateInsights(result.data.insights);
                updatePrediction(result.data.prediction);
                updateSavingsAdvice(result.data.savings_advice);
            } else {
                console.error('AI analysis failed:', result.error);
                showInsightsError(); // Show error message if fetch fails
            }
        } catch (error) {
            console.error('AI analysis error:', error);
            showInsightsError(); // Show error message on network/parse error
        } finally {
            loadingEl.style.display = 'none'; // Hide loading spinner
            contentEl.style.display = 'block'; // Show content
        }
    }

    function updateHealthScore(healthData) {
        // Updates the UI elements for the financial health score
        const scoreEl = document.getElementById('health-score');
        const gradeEl = document.getElementById('health-grade');
        const messageEl = document.getElementById('health-message');
        const factorsEl = document.getElementById('health-factors');
        const scoreCircle = document.getElementById('health-score-circle'); // Element for the circle visualization
        
        if (!healthData) { // Handle cases where data might be missing
            scoreEl.textContent = '--';
            gradeEl.textContent = '--';
            messageEl.textContent = 'Could not fetch health data.';
            factorsEl.innerHTML = '';
            scoreCircle.className = 'score-circle'; // Reset class
            return;
        }

        scoreEl.textContent = healthData.score;
        gradeEl.textContent = healthData.grade;
        messageEl.textContent = healthData.message;
        
        // Update score circle color based on grade
        scoreCircle.className = 'score-circle'; // Reset classes
        if (healthData.grade === 'Excellent') scoreCircle.classList.add('excellent');
        else if (healthData.grade === 'Good') scoreCircle.classList.add('good');
        else if (healthData.grade === 'Fair') scoreCircle.classList.add('fair');
        else if (healthData.grade === 'Poor') scoreCircle.classList.add('poor');
        
        // Update health factors list
        factorsEl.innerHTML = '';
        if (healthData.factors && healthData.factors.length > 0) {
            healthData.factors.forEach(factor => {
                const factorEl = document.createElement('span');
                factorEl.className = 'health-factor';
                factorEl.textContent = factor;
                factorsEl.appendChild(factorEl);
            });
        }
    }

    function updateInsights(insights) {
        // Updates the "Smart Insights" section
        const container = document.getElementById('insights-container');
        
        if (!insights || insights.length === 0) {
            container.innerHTML = `
                <div class="empty-insights">
                    <i class="fas fa-chart-line"></i>
                    <p>No insights available yet</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = ''; // Clear previous insights
        insights.forEach(insight => {
            const insightEl = document.createElement('div');
            insightEl.className = 'insight-card';
            insightEl.innerHTML = `
                <h5><i class="fas fa-lightbulb"></i> Smart Insight</h5>
                <p>${insight.message}</p>
            `;
            container.appendChild(insightEl);
        });
    }

    function updatePrediction(prediction) {
        // Updates the "Predictive Analytics" section
        const contentEl = document.getElementById('prediction-content');
        
        if (prediction && prediction.message) {
            contentEl.innerHTML = `
                <p>${prediction.message}</p>
                ${prediction.data && prediction.data.insights ? 
                    `<div style="margin-top: 10px;">
                        <strong>Key Insights:</strong>
                        <ul style="margin-top: 5px; padding-left: 20px;">
                            ${prediction.data.insights.map(insight => `<li>${insight}</li>`).join('')}
                        </ul>
                    </div>` : ''
                }
            `;
        } else {
            contentEl.innerHTML = '<p>Unable to generate prediction</p>';
        }
    }

    function updateSavingsAdvice(advice) {
        // Updates the "Savings Advice" section
        const container = document.getElementById('savings-advice-container');
        
        if (!advice || advice.length === 0) {
            container.innerHTML = `
                <div class="empty-advice">
                    <i class="fas fa-coins"></i>
                    <p>No advice available yet</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = ''; // Clear previous advice
        advice.forEach(item => {
            const adviceEl = document.createElement('div');
            adviceEl.className = 'advice-card';
            adviceEl.innerHTML = `
                <div class="advice-header">
                    <div class="advice-title">${item.title}</div>
                    <span class="advice-priority ${item.priority}">${item.priority}</span>
                </div>
                <div class="advice-message">${item.message}</div>
                ${item.potential_savings > 0 ? 
                    `<div class="advice-savings">Potential savings: ₹${item.potential_savings.toFixed(0)}</div>` : ''
                }
            `;
            container.appendChild(adviceEl);
        });
    }

    async function testCategorization() {
        // Tests the AI's ability to categorize an expense name
        const nameInput = document.getElementById('expense-name-input');
        const amountInput = document.getElementById('expense-amount-input');
        const resultEl = document.getElementById('categorization-result');
        
        const name = nameInput.value.trim();
        const amount = parseFloat(amountInput.value);
        
        if (!name || isNaN(amount) || amount <= 0) {
            resultEl.innerHTML = '<p>Please enter a valid expense name and amount</p>';
            resultEl.className = 'categorization-result'; // Reset class
            return;
        }
        
        try {
            // Assumes a backend endpoint for categorization exists
            const response = await fetch(`${API_BASE_URL}/expenses/categorize?expense_name=${encodeURIComponent(name)}&amount=${amount}`, {
                method: 'GET'
            });
            
            const result = await response.json();
            
            if (result.success) {
                resultEl.innerHTML = `
                    <p>AI suggests category:</p>
                    <div class="suggested-category">${result.suggested_category}</div>
                `;
                resultEl.className = 'categorization-result success'; // Apply success styling
            } else {
                resultEl.innerHTML = '<p>Unable to categorize expense</p>';
                resultEl.className = 'categorization-result'; // Reset class
            }
        } catch (error) {
            console.error('Categorization error:', error);
            resultEl.innerHTML = '<p>Error categorizing expense</p>';
            resultEl.className = 'categorization-result'; // Reset class
        }
    }

    function showInsightsError() {
        // Displays an error message if insights data cannot be fetched
        const contentEl = document.getElementById('insights-content');
        contentEl.innerHTML = `
            <div class="insights-section">
                <div class="insights-section-header">
                    <h4><i class="fas fa-exclamation-triangle"></i> Insights Unavailable</h4>
                </div>
                <div style="text-align: center; padding: 20px; color: var(--text-muted);">
                    <i class="fas fa-robot" style="font-size: 32px; margin-bottom: 15px;"></i>
                    <p>Insights service is currently unavailable. Please try again later.</p>
                    <button onclick="refreshInsights()" class="btn btn-primary" style="margin-top: 15px;">
                        <i class="fas fa-sync-alt"></i> Retry
                    </button>
                </div>
            </div>
        `;
    }

    // --- Initialization ---
    // Load data from local storage when the page loads
    loadFromLocalStorage();
    updateUI(); // Initial rendering of all UI elements
    </script>
</body>
</html>
