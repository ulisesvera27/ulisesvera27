"""
Simple User Management Web Application
This application demonstrates common bugs in web applications
"""

import sqlite3
import hashlib
from datetime import datetime
# FIXED: Added bcrypt for secure password hashing
try:
    import bcrypt
except ImportError:
    print("Warning: bcrypt not installed. Using hashlib for demonstration purposes.")

class UserManager:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with users table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                email TEXT,
                balance REAL DEFAULT 0.0,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_user(self, username, password, email):
        """Create a new user account"""
        # FIXED: Use parameterized queries to prevent SQL injection
        # FIXED: Hash password before storing
        hashed_password = self.hash_password(password)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Use parameterized query with ? placeholders
        cursor.execute(
            "INSERT INTO users (username, password, email, created_at) VALUES (?, ?, ?, ?)",
            (username, hashed_password, email, str(datetime.now()))
        )
        conn.commit()
        conn.close()
        return True
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        # FIXED: Use parameterized queries to prevent SQL injection
        # FIXED: Compare hashed passwords instead of plain text
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Use parameterized query with ? placeholder
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            return False
        
        stored_hash = result[0]
        # Verify password against stored hash
        return self.verify_password(password, stored_hash)
    
    def calculate_discount(self, price, discount_percent):
        """
        Calculate discounted price
        FIXED: Corrected logic error in discount calculation
        """
        # Calculate the discount amount and subtract it from the original price
        discount_amount = price * (discount_percent / 100)
        final_price = price - discount_amount  # FIXED: Changed from addition to subtraction
        return final_price
    
    def process_bulk_users(self, user_list):
        """
        Process a large list of users
        FIXED: Improved performance by using a single database connection
        """
        results = []
        # FIXED: Open connection once outside the loop for better performance
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for user_data in user_list:
                # Reuse the same connection for all queries
                cursor.execute(
                    "SELECT * FROM users WHERE username = ?",
                    (user_data['username'],)
                )
                user = cursor.fetchone()
                
                if user:
                    results.append({
                        'username': user[1],
                        'email': user[3],
                        'balance': user[4]
                    })
        finally:
            # Close connection once after all operations
            conn.close()
        
        return results
    
    def hash_password(self, password):
        """
        Hash a password using bcrypt (or SHA256 as fallback)
        FIXED: Replaced weak MD5 with strong hashing algorithm
        """
        try:
            # Use bcrypt for secure password hashing with salt
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode(), salt)
            return hashed.decode()
        except (NameError, AttributeError):
            # Fallback to SHA256 with salt if bcrypt not available
            # Note: In production, bcrypt, argon2, or scrypt should be used
            import os
            salt = hashlib.sha256(os.urandom(32)).hexdigest()
            return hashlib.sha256((password + salt).encode()).hexdigest() + ':' + salt
    
    def verify_password(self, password, stored_hash):
        """
        Verify a password against a stored hash
        FIXED: Added password verification method
        """
        try:
            # Verify with bcrypt
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
        except (NameError, AttributeError):
            # Fallback verification for SHA256
            if ':' in stored_hash:
                hash_part, salt = stored_hash.split(':')
                return hashlib.sha256((password + salt).encode()).hexdigest() == hash_part
            return False


def main():
    """Main function to demonstrate the bugs"""
    manager = UserManager()
    
    # Demonstrate Bug #1: Logic error in discount calculation
    print("Testing discount calculation...")
    original_price = 100.0
    discount = 20  # 20% discount
    final = manager.calculate_discount(original_price, discount)
    print(f"Original: ${original_price}, Discount: {discount}%, Final: ${final}")
    print(f"Expected: $80.00, Got: ${final}")
    
    # Demonstrate Bug #2: Performance issue
    print("\nTesting bulk user processing...")
    test_users = [{'username': f'user{i}'} for i in range(100)]
    start = datetime.now()
    manager.process_bulk_users(test_users)
    end = datetime.now()
    print(f"Processed {len(test_users)} users in {(end - start).total_seconds()} seconds")
    
    # Demonstrate Bug #3: SQL Injection vulnerability
    print("\nTesting authentication (SQL Injection vulnerability)...")
    # This malicious input would bypass authentication
    malicious_username = "admin' OR '1'='1"
    malicious_password = "anything"
    print(f"Attempting login with: {malicious_username}")


if __name__ == '__main__':
    main()
