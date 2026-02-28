import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import time
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Configure security parameters
PASSWORD_MIN_LENGTH = 8
RATE_LIMIT_SECONDS = 1

# In-memory store for demo; replace with actual database in production
wallets = {}

# Simple rate limiting decorator
def rate_limiter(func):
    last_called = [0]
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_time = time.time()
        if current_time - last_called[0] < RATE_LIMIT_SECONDS:
            return jsonify({'error': 'Too many requests'}), 429
        last_called[0] = current_time
        return func(*args, **kwargs)
    return wrapper

# Input validation function
def validate_input(data, required_fields):
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f'Missing or null field: {field}')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        validate_input(data, ['username', 'password'])
        username = data['username']
        password = data['password']
        
        if len(password) < PASSWORD_MIN_LENGTH:
            return jsonify({'error': 'Password is too short'}), 400
        
        # Hash password and store it securely (replace with database logic)
        hashed_password = generate_password_hash(password)
        logging.info(f'User {username} registered successfully.')  
        return jsonify({'message': 'User registered successfully'}), 201
    except ValueError as ve:
        logging.error(f'Input validation error: {ve}')
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging.error(f'Error during registration: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/wallet/<username>', methods=['POST'])
@rate_limiter
def create_wallet(username):
    try:
        if username in wallets:
            return jsonify({'error': 'Wallet already exists'}), 400

        wallets[username] = 0  # Initialize wallet
        logging.info(f'Wallet created for user {username}.')
        return jsonify({'message': 'Wallet created successfully'}), 201
    except Exception as e:
        logging.error(f'Error creating wallet: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# Environment variable for secret keys (example)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')

if __name__ == '__main__':
    app.run(debug=False)
