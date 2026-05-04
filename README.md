# BudgetBuddy
A smart web app that helps students track expenses, analyze spending patterns, and predict future costs using data science.
## 📋 Overview

Budget Buddy is a comprehensive, full-stack financial management web application designed to help students and working professionals take control of their finances. With intelligent predictions, interactive visualizations, and smart budgeting tools, Budget Buddy makes personal finance management engaging and effective.
## ✨ Features

### Core Features
- 🔐 **User Authentication** - Secure registration and login system
- 📊 **Interactive Dashboard** - Real-time financial overview with beautiful visualizations
- 💸 **Transaction Management** - Add, track, and categorize income and expenses
- 🎯 **Goal Setting** - Set financial goals with progress tracking and deadlines
- 📈 **AI Predictions** - Machine learning-based expense forecasting
- 🚨 **Budget Alerts** - Smart notifications when approaching or exceeding limits
### Advanced Features
- 💹 **Tax Calculator** - Income tax calculation with investment deductions
- 🏠 **Loan Eligibility** - Calculate loan amounts based on income and existing EMIs
- 💱 **Currency Converter** - Convert between 10+ international currencies
- 🤖 **Financial Chatbot** - AI-powered assistant for financial advice
- 📊 **Visual Reports** - Interactive pie charts and bar graphs
- 📋 **Copy to Clipboard** - One-click copy of any financial value
- 🎨 **Animated UI** - Smooth animations and transitions
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
### Security Features
- 🔒 **Password Encryption** - SHA-256 hashing for passwords
- 🛡️ **Session Management** - Secure user sessions
- 💾 **Local Storage** - Automatic data persistence

## 🎨 Color Scheme

| Color | Usage | Hex Code |
|-------|-------|----------|
| 💙 Blue | Primary theme, buttons, highlights | `#667eea` |
| 💜 Purple | Gradients, accents | `#764ba2` |
| 🤍 White | Cards, backgrounds | `#ffffff` |
| 🟢 Green | Profits, income, success | `#28a745` |
| 🔴 Red | Losses, expenses, alerts | `#dc3545` |
| 🔵 Light Blue | Neutral information | `#17a2b8` |
## 🛠️ Technology Stack

### Backend
- **Python 3.8+** - Core programming language
- **Flask 2.3.3** - Web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight database
- **Scikit-learn** - Machine learning for predictions
- **Cryptography** - Data encryption
### Frontend
- **HTML5/CSS3** - Structure and styling
- **Bootstrap 5** - Responsive UI components
- **JavaScript (ES6)** - Interactive functionality
- **Plotly** - Interactive charts and graphs
- **Font Awesome** - Icons and visual elements

### APIs & Libraries
- **ExchangeRate-API** - Real-time currency conversion
- **Google Fonts** - Professional typography
- **Chart.js** - Additional visualizations
## 📁 Project Structure
BudgetBuddy/
│
├── app.py # Main Flask application
├── requirements.txt # Python dependencies
├── budget_buddy.db # SQLite database (auto-generated)
│
├── templates/
│ ├── index.html # Landing page
│ └── dashboard.html # Main dashboard
│
└── README.md # Project documentation

text

## 🚀 Installation Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)

### Step-by-Step Installation

#### 1. Clone or Download the Project
```bash
git clone https://github.com/Protistha/budget-buddy.git
cd budget-buddy
2. Create Virtual Environment (Recommended)
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
bash
pip install -r requirements.txt
If you encounter issues, install packages individually:

bash
pip install Flask Flask-SQLAlchemy pandas numpy scikit-learn plotly cryptography requests
4. Run the Application
bash
python app.py
5. Access the Application
Open your browser and navigate to:

text
http://localhost:5000
📱 How to Use
First Time Setup
Register an Account

Click "Register" on the homepage

Enter username, email, and password

Click "Register"

Login

Click "Login" button

Enter your credentials

You'll be redirected to the dashboard

Managing Transactions
Add Income

Go to "Transactions" section

Enter amount (e.g., 5000)

Select category (e.g., "Salary")

Choose type "Income"

Add description (optional)

Click "Add Transaction"

Add Expenses

Follow same steps but select "Expense"

Categories: Food, Transport, Entertainment, Shopping, Bills, etc.

Setting Financial Goals
Navigate to "Goals" section

Click "Set New Goal"

Enter:

Goal name (e.g., "Emergency Fund")

Target amount

Deadline date

Track progress with visual progress bar

Budget Management
Go to "Budget Limits"

Select category and monthly limit

Receive automatic alerts when:

Spending reaches 80% of limit (warning)

Spending exceeds limit (alert)

Tax Planning
Navigate to "Tax Calculator"

Enter annual income

Add investment deductions (up to $150,000)

Get instant tax calculation including:

Taxable income

Total tax liability

Effective tax rate

Monthly in-hand salary

Loan Eligibility
Go to "Loan Planning"

Enter:

Monthly income

Existing EMIs

Loan type (Home/Car/Personal)

View:

Maximum eligible loan amount

EMI capacity

Interest rates

Tenure options

Currency Conversion
Navigate to "Currency Converter"

Enter amount

Select source and target currencies

Get real-time conversion rates

Financial Assistant (Chatbot)
Ask questions like:

"How to save money?"

"Best investment strategies"

"How to reduce debt?"

"Tax saving tips"

"Budgeting methods"

📊 Sample Data for Testing
Use this sample data to test all features:

yaml
Monthly Income: $5,000
Monthly Expenses:
  - Rent: $1,500
  - Food: $600
  - Transport: $300
  - Entertainment: $400
  - Shopping: $500
  - Utilities: $200

Savings Goals:
  - Emergency Fund: $10,000 (6 months target)
  - Vacation: $3,000 (1 year target)
  - New Laptop: $1,500 (3 months target)

Budget Limits:
  - Food: $700/month
  - Entertainment: $500/month
  - Shopping: $400/month
🔧 Troubleshooting
Common Issues & Solutions
Login Fails
Ensure you registered first

Check username and password spelling

Clear browser cache and try again

Check if server is running

Charts Not Displaying
Check internet connection (Plotly CDN)

Add at least 3-5 transactions

Refresh the page

Check browser console for errors (F12)

Database Errors
bash
# Delete existing database and restart
rm budget_buddy.db  # Linux/Mac
del budget_buddy.db # Windows
python app.py
Port Already in Use
bash
# Change port in app.py last line to:
app.run(debug=True, port=5001)
Package Installation Fails
bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install without version restrictions
pip install Flask Flask-SQLAlchemy pandas numpy scikit-learn plotly cryptography
🎯 Key Features Explained
AI Predictions
Uses Linear Regression algorithm

Analyzes 3+ months of expense data

Predicts future spending patterns

Provides actionable insights

Budget Alerts System
Green: Spending within 80% of limit ✅

Yellow: Spending between 80-100% ⚠️

Red: Spending exceeded limit 🚨

Data Persistence
LocalStorage for offline demo mode

SQLite database for production

Automatic data backup

Export functionality

🎨 Customization
Changing Colors
Edit the CSS variables in dashboard.html:

css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --success-color: #28a745;
    --danger-color: #dc3545;
}
Adding Categories
Modify the select options in dashboard.html:

html
<option value="NewCategory">New Category</option>
Adjusting Tax Brackets
Edit the calculate_tax function in app.py:

python
if taxable_income <= 250000:
    tax = 0
# Add your country's tax brackets here
🔜 Future Enhancements
Mobile app (React Native)

Bank API integration

Multi-currency support

Bill payment reminders

Investment portfolio tracker

PDF report generation

Email notifications

Multi-language support

Dark mode

Voice commands

Expense scanning from receipts

Family/Group budgeting

Stock market integration

Cryptocurrency tracking

🤝 Contributing
Contributions are welcome! Please follow these steps:

Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add AmazingFeature')

Push to branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see below:

text
MIT License

Copyright (c) 2024 Budget Buddy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
🙏 Acknowledgments
Flask - For the amazing web framework

Plotly - For beautiful interactive charts

Bootstrap - For responsive design components

Font Awesome - For stunning icons

Scikit-learn - For ML capabilities

⭐ Star History
If you find this project useful, please give it a star on GitHub!

🎉 Final Notes
Budget Buddy is designed to make financial management accessible, intuitive, and even enjoyable. Whether you're a student learning to budget or a professional planning for retirement, Budget Buddy provides the tools you need to achieve financial freedom.

Remember: Financial freedom is a journey, not a destination. Start small, stay consistent, and watch your wealth grow!

<div align="center"> Made with ❤️ for financial wellness
Start your financial journey today with Budget Buddy!
y.txt
