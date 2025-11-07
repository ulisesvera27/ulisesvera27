#!/usr/bin/env python3
"""
Simple web application with user authentication and data processing
"""

from flask import Flask, request, jsonify, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'hardcoded-secret-key-12345'

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Bug 1: Logic Error - Password comparison is case-sensitive but registration is not
def register_user(username, password):
    """Register a new user"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Store password as-is (no hashing - security issue, but separate bug)
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                   (username.lower(), password))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    """Authenticate a user"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Fix: Use lowercase to match how username is stored during registration
    cursor.execute('SELECT password FROM users WHERE username = ?', (username.lower(),))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == password:
        return True
    return False

# Fixed: Performance Issue - Using efficient join() method instead of concatenation
def process_data(data_list):
    """Process a list of data items"""
    # Fix: Use join() which is O(n) instead of O(n²) string concatenation
    return ", ".join(str(item) for item in data_list)

# Fixed: Security Vulnerability - Using parameterized queries and proper escaping
@app.route('/search', methods=['GET'])
def search_users():
    """Search for users by name"""
    query = request.args.get('q', '')
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Fix: Use parameterized query to prevent SQL injection
    cursor.execute('SELECT username FROM users WHERE username LIKE ?', (f'%{query}%',))
    results = cursor.fetchall()
    conn.close()
    
    # Fix: jsonify() automatically escapes JSON, but we ensure clean data
    usernames = [str(row[0]) for row in results]
    return jsonify({
        'query': query,  # jsonify() handles escaping for JSON output
        'results': usernames
    })

@app.route('/register', methods=['POST'])
def register():
    """Register endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    try:
        register_user(username, password)
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409

@app.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if authenticate_user(username, password):
        session['username'] = username
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/process', methods=['POST'])
def process():
    """Process data endpoint"""
    data = request.json
    items = data.get('items', [])
    
    processed = process_data(items)
    return jsonify({'result': processed}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
