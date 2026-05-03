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
