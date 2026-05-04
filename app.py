from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly
import plotly.graph_objs as go
import json
import hashlib
import secrets
from cryptography.fernet import Fernet
import requests
import warnings
warnings.filterwarnings('ignore')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_buddy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# Encryption setup
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)
# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    monthly_income = db.Column(db.Float, default=0)
    tax_rate = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))
    
class FinancialGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    deadline = db.Column(db.DateTime, nullable=False)
    
class BudgetLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()
# Helper Functions
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode())

def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data).decode()

def calculate_net_worth(user_id):
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    return total_income - total_expenses

def predict_future_expenses(user_id, months=3):
    transactions = Transaction.query.filter_by(user_id=user_id, transaction_type='expense').all()
    if len(transactions) < 3:
        return None
    
    df = pd.DataFrame([(t.date, t.amount) for t in transactions], columns=['date', 'amount'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.groupby(df['date'].dt.month).sum().reset_index()
    
    if len(df) < 2:
        return None
    
    X = np.array(range(len(df))).reshape(-1, 1)
    y = df['amount'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_X = np.array(range(len(df), len(df) + months)).reshape(-1, 1)
    predictions = model.predict(future_X)
    return predictions

def check_budget_alert(user_id, category, amount):
    budget = BudgetLimit.query.filter_by(user_id=user_id, category=category).first()
    if budget:
        current_month = datetime.utcnow().month
        monthly_expenses = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.category == category,
            Transaction.transaction_type == 'expense',
            db.extract('month', Transaction.date) == current_month
        ).all()
        total = sum(e.amount for e in monthly_expenses)
        if total > budget.monthly_limit:
            return f"Alert: Budget exceeded for {category}!"
    return None
# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('dashboard.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
    user = User(username=data['username'], email=data['email'], password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registration successful'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
    user = User.query.filter_by(username=data['username'], password_hash=password_hash).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'message': 'Login successful', 'user_id': user.id, 'username': user.username})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})

@app.route('/api/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    transaction = Transaction(
        user_id=session['user_id'],
        amount=data['amount'],
        category=data['category'],
        transaction_type=data['type'],
        description=data.get('description', '')
    )
    db.session.add(transaction)
    db.session.commit()
    
    alert = None
    if data['type'] == 'expense':
        alert = check_budget_alert(session['user_id'], data['category'], data['amount'])
    
    return jsonify({'message': 'Transaction added', 'alert': alert})

@app.route('/api/get_transactions', methods=['GET'])
def get_transactions():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    transactions = Transaction.query.filter_by(user_id=session['user_id']).order_by(Transaction.date.desc()).all()
    return jsonify([{
        'id': t.id,
        'amount': t.amount,
        'category': t.category,
        'type': t.transaction_type,
        'date': t.date.strftime('%Y-%m-%d'),
        'description': t.description
    } for t in transactions])

@app.route('/api/get_summary', methods=['GET'])
def get_summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    transactions = Transaction.query.filter_by(user_id=session['user_id']).all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    net_worth = total_income - total_expense
    savings_rate = (net_worth / total_income * 100) if total_income > 0 else 0
    
    category_breakdown = {}
    for t in transactions:
        if t.transaction_type == 'expense':
            category_breakdown[t.category] = category_breakdown.get(t.category, 0) + t.amount
    
    monthly_data = {}
    for t in transactions:
        month = t.date.strftime('%Y-%m')
        if month not in monthly_data:
            monthly_data[month] = {'income': 0, 'expense': 0}
        if t.transaction_type == 'income':
            monthly_data[month]['income'] += t.amount
        else:
            monthly_data[month]['expense'] += t.amount
    
    return jsonify({
        'total_income': total_income,
        'total_expense': total_expense,
        'net_worth': net_worth,
        'savings_rate': savings_rate,
        'category_breakdown': category_breakdown,
        'monthly_data': monthly_data
    })

@app.route('/api/get_chart_data', methods=['GET'])
def get_chart_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    transactions = Transaction.query.filter_by(user_id=session['user_id']).all()
    
    expense_categories = {}
    for t in transactions:
        if t.transaction_type == 'expense':
            expense_categories[t.category] = expense_categories.get(t.category, 0) + t.amount
    
    monthly_data = {}
    for t in transactions:
        month = t.date.strftime('%Y-%m')
        if month not in monthly_data:
            monthly_data[month] = {'income': 0, 'expense': 0}
        if t.transaction_type == 'income':
            monthly_data[month]['income'] += t.amount
        else:
            monthly_data[month]['expense'] += t.amount
    
    return jsonify({
        'pie_chart': expense_categories,
        'monthly_trend': monthly_data
    })
    @app.route('/api/predict_expenses', methods=['GET'])
def predict_expenses():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    predictions = predict_future_expenses(session['user_id'])
    if predictions is not None:
        return jsonify({'predictions': predictions.tolist()})
    return jsonify({'error': 'Not enough data for prediction'}), 400

@app.route('/api/set_goal', methods=['POST'])
def set_goal():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    goal = FinancialGoal(
        user_id=session['user_id'],
        goal_name=data['name'],
        target_amount=data['target'],
        current_amount=data.get('current', 0),
        deadline=datetime.strptime(data['deadline'], '%Y-%m-%d')
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify({'message': 'Goal set successfully'})

@app.route('/api/get_goals', methods=['GET'])
def get_goals():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    goals = FinancialGoal.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'id': g.id,
        'name': g.goal_name,
        'target': g.target_amount,
        'current': g.current_amount,
        'progress': (g.current_amount / g.target_amount * 100) if g.target_amount > 0 else 0,
        'deadline': g.deadline.strftime('%Y-%m-%d')
    } for g in goals])

@app.route('/api/update_goal_progress', methods=['POST'])
def update_goal_progress():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    goal = FinancialGoal.query.get(data['goal_id'])
    if goal and goal.user_id == session['user_id']:
        goal.current_amount += data['amount']
        db.session.commit()
        return jsonify({'message': 'Progress updated', 'progress': (goal.current_amount / goal.target_amount * 100)})
    return jsonify({'error': 'Goal not found'}), 404

@app.route('/api/convert_currency', methods=['POST'])
def convert_currency():
    data = request.json
    amount = data['amount']
    from_currency = data['from_currency']
    to_currency = data['to_currency']
    
    # Fallback rates (no external API dependency)
    fallback_rates = {
        'USD': 1, 'EUR': 0.85, 'GBP': 0.73, 'INR': 83.5, 'JPY': 110.5, 'CAD': 1.35, 'AUD': 1.52,
        'CNY': 7.2, 'SGD': 1.35, 'CHF': 0.91, 'MYR': 4.7, 'AED': 3.67, 'SAR': 3.75
    }
    
    try:
        # Try external API first
        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{from_currency}', timeout=3)
        if response.status_code == 200:
            rates = response.json()['rates']
            if to_currency in rates:
                converted = amount * rates[to_currency]
                return jsonify({'converted_amount': converted, 'rate': rates[to_currency], 'source': 'api'})
    except:
        pass
    
    # Use fallback rates
    if from_currency in fallback_rates and to_currency in fallback_rates:
        rate = fallback_rates[to_currency] / fallback_rates[from_currency]
        converted = amount * rate
        return jsonify({'converted_amount': converted, 'rate': rate, 'source': 'fallback', 'using_fallback': True})
    
    return jsonify({'error': 'Currency conversion failed'}), 400

@app.route('/api/calculate_tax', methods=['POST'])
def calculate_tax():
    data = request.json
    annual_income = data.get('annual_income', 0)
    investments = data.get('investments', 0)
    
    if annual_income == 0:
        return jsonify({'error': 'Please provide annual income'}), 400
    
    taxable_income = max(0, annual_income - min(investments, 150000))
    
    if taxable_income <= 250000:
        tax = 0
    elif taxable_income <= 500000:
        tax = (taxable_income - 250000) * 0.05
    elif taxable_income <= 1000000:
        tax = 12500 + (taxable_income - 500000) * 0.20
    else:
        tax = 112500 + (taxable_income - 1000000) * 0.30
    
    cess = tax * 0.04
    total_tax = tax + cess
    
    return jsonify({
        'annual_income': annual_income,
        'taxable_income': taxable_income,
        'tax': total_tax,
        'effective_tax_rate': (total_tax / annual_income * 100) if annual_income > 0 else 0,
        'in_hand_monthly': (annual_income - total_tax) / 12,
        'in_hand_annual': annual_income - total_tax
    })

@app.route('/api/calculate_ctc_breakdown', methods=['POST'])
def calculate_ctc_breakdown():
    data = request.json
    ctc = data['ctc']
    bonus = data.get('bonus', 0)
    perks = data.get('perks', 0)
    
    basic = ctc * 0.4
    hra = basic * 0.5
    special_allowance = ctc - (basic + hra + bonus + perks)
    
    return jsonify({
        'basic_salary': basic,
        'hra': hra,
        'special_allowance': special_allowance,
        'bonus': bonus,
        'perks': perks,
        'monthly_in_hand': (basic + special_allowance) / 12,
        'annual_in_hand': basic + special_allowance
    })

@app.route('/api/loan_eligibility', methods=['POST'])
def loan_eligibility():
    data = request.json
    monthly_income = data['monthly_income']
    existing_emis = data.get('existing_emis', 0)
    loan_type = data['loan_type']
    
    max_emi = monthly_income * 0.5 - existing_emis
    
    if max_emi <= 0:
        return jsonify({'error': 'Not eligible based on existing obligations'}), 400
    
    if loan_type == 'home':
        interest_rate = 8.5
        max_tenure = 20
    elif loan_type == 'car':
        interest_rate = 9.5
        max_tenure = 7
    else:
        interest_rate = 12
        max_tenure = 5
    
    monthly_rate = interest_rate / 12 / 100
    loan_amount = max_emi * ((1 - (1 + monthly_rate) ** (-max_tenure * 12)) / monthly_rate)
    
    emi_options = {}
    for tenure in [3, 5, 7, 10, 15, 20]:
        if tenure <= max_tenure:
            months = tenure * 12
            emi = loan_amount * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
            emi_options[tenure] = emi
    
    return jsonify({
        'eligible_amount': loan_amount,
        'max_emi': max_emi,
        'interest_rate': interest_rate,
        'max_tenure': max_tenure,
        'emi_options': emi_options
    })

@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.json
    text = data['text']
    target_lang = data['target_lang']
    
    # Simple translation dictionary for common financial terms
    translations = {
        'hi': {  # Hindi
            'budget': 'बजट', 'savings': 'बचत', 'expense': 'खर्च', 'income': 'आय',
            'investment': 'निवेश', 'loan': 'ऋण', 'tax': 'कर', 'profit': 'लाभ',
            'loss': 'हानि', 'money': 'पैसा', 'save': 'बचाएं', 'spend': 'खर्च करें'
        },
        'es': {  # Spanish
            'budget': 'Presupuesto', 'savings': 'Ahorros', 'expense': 'Gasto',
            'income': 'Ingresos', 'investment': 'Inversión', 'loan': 'Préstamo',
            'tax': 'Impuesto', 'profit': 'Ganancia', 'loss': 'Pérdida'
        },
        'fr': {  # French
            'budget': 'Budget', 'savings': 'Épargne', 'expense': 'Dépense',
            'income': 'Revenu', 'investment': 'Investissement', 'loan': 'Prêt',
            'tax': 'Impôt', 'profit': 'Profit', 'loss': 'Perte'
        },
        'de': {  # German
            'budget': 'Budget', 'savings': 'Ersparnisse', 'expense': 'Ausgabe',
            'income': 'Einkommen', 'investment': 'Investition', 'loan': 'Darlehen',
            'tax': 'Steuer', 'profit': 'Gewinn', 'loss': 'Verlust'
        },
        'zh': {  # Chinese
            'budget': '预算', 'savings': '储蓄', 'expense': '花费',
            'income': '收入', 'investment': '投资', 'loan': '贷款',
            'tax': '税收', 'profit': '利润', 'loss': '损失'
        }
    }
    
    translated_words = []
    words = text.lower().split()
    lang_dict = translations.get(target_lang, {})
    
    for word in words:
        if word in lang_dict:
            translated_words.append(lang_dict[word])
        else:
            translated_words.append(word)
    
    translated_text = ' '.join(translated_words)
    
    return jsonify({
        'translated_text': translated_text if translated_text != text else f"[Translation to {target_lang} available for financial terms]",
        'original_text': text,
        'target_language': target_lang
    })

@app.route('/api/set_budget_limit', methods=['POST'])
def set_budget_limit():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    budget = BudgetLimit.query.filter_by(user_id=session['user_id'], category=data['category']).first()
    if budget:
        budget.monthly_limit = data['limit']
    else:
        budget = BudgetLimit(user_id=session['user_id'], category=data['category'], monthly_limit=data['limit'])
        db.session.add(budget)
    
    db.session.commit()
    return jsonify({'message': 'Budget limit set'})

@app.route('/api/get_budget_limits', methods=['GET'])
def get_budget_limits():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    budgets = BudgetLimit.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'category': b.category,
        'limit': b.monthly_limit
    } for b in budgets])

@app.route('/api/get_budget_alerts', methods=['GET'])
def get_budget_alerts():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    budgets = BudgetLimit.query.filter_by(user_id=session['user_id']).all()
    current_month = datetime.utcnow().month
    alerts = []
    
    for budget in budgets:
        monthly_expenses = Transaction.query.filter(
            Transaction.user_id == session['user_id'],
            Transaction.category == budget.category,
            Transaction.transaction_type == 'expense',
            db.extract('month', Transaction.date) == current_month
        ).all()
        total = sum(e.amount for e in monthly_expenses)
        
        if total > budget.monthly_limit:
            alerts.append({
                'category': budget.category,
                'type': 'exceeded',
                'spent': total,
                'limit': budget.monthly_limit,
                'percentage': (total / budget.monthly_limit * 100)
            })
        elif total > budget.monthly_limit * 0.8:
            alerts.append({
                'category': budget.category,
                'type': 'warning',
                'spent': total,
                'limit': budget.monthly_limit,
                'percentage': (total / budget.monthly_limit * 100)
            })
    
    return jsonify({'alerts': alerts})

@app.route('/api/financial_literacy_tips', methods=['GET'])
def financial_literacy_tips():
    tips = [
        "Save at least 20% of your income for emergencies",
        "Invest early to benefit from compound interest",
        "Track your expenses to identify spending patterns",
        "Create an emergency fund covering 6 months of expenses",
        "Pay off high-interest debt first",
        "Diversify your investment portfolio",
        "Review your insurance coverage annually",
        "Plan for retirement starting from your first job",
        "The 50/30/20 rule: 50% needs, 30% wants, 20% savings",
        "Automate your savings to ensure consistency",
        "Negotiate your salary every 1-2 years",
        "Avoid credit card debt - pay full balance monthly"
    ]
    return jsonify({'tips': tips})

@app.route('/api/get_financial_tips', methods=['GET'])
def get_financial_tips():
    tips = [
        "The 50/30/20 rule: 50% needs, 30% wants, 20% savings",
        "Start an emergency fund with at least 3-6 months of expenses",
        "Pay yourself first - automate your savings",
        "Invest early to benefit from compound interest",
        "Review your subscriptions monthly - cancel unused ones",
        "Use the 30-day rule for non-essential purchases over $100",
        "Your credit score affects loan interest rates - maintain it well",
        "Diversify investments to manage risk",
        "Tax-loss harvesting can reduce your tax bill",
        "Negotiate bills - many companies offer loyalty discounts",
        "Use cashback and rewards credit cards responsibly",
        "Set specific financial goals with deadlines"
    ]
    return jsonify({'tips': tips})

@app.route('/api/chatbot_response', methods=['POST'])
def chatbot_response():
    data = request.json
    message = data['message'].lower()
    
    responses = {
        'budget': "Great question! The 50/30/20 rule is a popular budgeting method: 50% for needs, 30% for wants, and 20% for savings and debt repayment.",
        'save': "To save effectively: 1) Track your expenses, 2) Set specific savings goals, 3) Automate your savings, 4) Cut unnecessary expenses, 5) Use the 30-day rule for impulse purchases.",
        'invest': "Start investing early! Consider diversified index funds, mutual funds, or ETFs. Always maintain an emergency fund first (6 months of expenses).",
        'debt': "For debt management: Use the avalanche method (pay highest interest first) or snowball method (pay smallest balance first). Always pay more than minimum due.",
        'emergency': "An emergency fund should cover 3-6 months of living expenses. Keep it in a high-yield savings account for easy access.",
        'credit': "Maintain credit utilization below 30%, pay bills on time, and check your credit report annually. Good credit saves money on loans and insurance.",
        'tax': "Maximize tax savings by: 1) Using retirement accounts, 2) Claiming all deductions, 3) Tax-loss harvesting, 4) Health savings accounts.",
        'retirement': "Start saving for retirement early. Aim to save 15% of your income. Take advantage of employer 401(k) matching.",
        'loan': "Before taking a loan: 1) Check your credit score, 2) Compare interest rates, 3) Calculate total cost, 4) Ensure EMI is below 40% of income."
    }
    
    response = "Thanks for your question! I can help with budgeting, saving, investing, debt management, taxes, retirement planning, and loans. Could you be more specific?"
    
    for key, value in responses.items():
        if key in message:
            response = value
            break
    
    return jsonify({'response': response})

@app.route('/api/set_income', methods=['POST'])
def set_income():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    user = User.query.get(session['user_id'])
    user.monthly_income = data['monthly_income']
    user.tax_rate = data.get('tax_rate', 0)
    db.session.commit()
    
    return jsonify({'message': 'Income updated successfully'})

@app.route('/api/get_user_profile', methods=['GET'])
def get_user_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    return jsonify({
        'username': user.username,
        'email': user.email,
        'monthly_income': user.monthly_income,
        'tax_rate': user.tax_rate,
        'member_since': user.created_at.strftime('%Y-%m-%d')
    })

@app.route('/api/export_data', methods=['GET'])
def export_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    transactions = Transaction.query.filter_by(user_id=session['user_id']).all()
    data = [{
        'date': t.date.strftime('%Y-%m-%d'),
        'amount': t.amount,
        'category': t.category,
        'type': t.transaction_type,
        'description': t.description
    } for t in transactions]
    
    return jsonify({'transactions': data, 'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
