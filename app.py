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
