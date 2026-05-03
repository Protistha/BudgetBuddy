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
