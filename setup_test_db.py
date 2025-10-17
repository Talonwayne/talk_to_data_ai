#!/usr/bin/env python3
"""
Setup a test SQLite database for demonstration purposes
This allows testing without requiring PostgreSQL
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

def create_test_database():
    """Create a test database with sample data"""
    
    # Connect to SQLite database (creates if doesn't exist)
    conn = sqlite3.connect('test_database.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category_id INTEGER,
            price DECIMAL(10,2),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            region TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            customer_id INTEGER,
            amount DECIMAL(10,2),
            quantity INTEGER,
            sale_date DATE,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # Insert sample data
    categories_data = [
        (1, 'Electronics'),
        (2, 'Clothing'),
        (3, 'Books'),
        (4, 'Home & Garden'),
        (5, 'Sports')
    ]
    
    products_data = [
        (1, 'Laptop', 1, 999.99),
        (2, 'Smartphone', 1, 699.99),
        (3, 'T-Shirt', 2, 19.99),
        (4, 'Jeans', 2, 49.99),
        (5, 'Python Programming', 3, 39.99),
        (6, 'Garden Tools', 4, 29.99),
        (7, 'Running Shoes', 5, 89.99),
        (8, 'Tablet', 1, 399.99),
        (9, 'Dress', 2, 79.99),
        (10, 'Fiction Novel', 3, 14.99)
    ]
    
    customers_data = [
        (1, 'John Smith', 'john@email.com', 'North'),
        (2, 'Jane Doe', 'jane@email.com', 'South'),
        (3, 'Bob Johnson', 'bob@email.com', 'East'),
        (4, 'Alice Brown', 'alice@email.com', 'West'),
        (5, 'Charlie Wilson', 'charlie@email.com', 'North'),
        (6, 'Diana Lee', 'diana@email.com', 'South'),
        (7, 'Eve Davis', 'eve@email.com', 'East'),
        (8, 'Frank Miller', 'frank@email.com', 'West')
    ]
    
    # Generate sales data for the past 6 months
    sales_data = []
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(1, 201):  # 200 sales records
        product_id = random.randint(1, 10)
        customer_id = random.randint(1, 8)
        quantity = random.randint(1, 5)
        
        # Get product price
        product_price = next((p[3] for p in products_data if p[0] == product_id), 50.00)
        amount = product_price * quantity
        
        # Random date within the past 6 months
        random_days = random.randint(0, 180)
        sale_date = start_date + timedelta(days=random_days)
        
        sales_data.append((
            i, product_id, customer_id, amount, quantity, sale_date.strftime('%Y-%m-%d')
        ))
    
    # Insert data
    cursor.executemany('INSERT OR REPLACE INTO categories VALUES (?, ?)', categories_data)
    cursor.executemany('INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?)', products_data)
    cursor.executemany('INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?)', customers_data)
    cursor.executemany('INSERT OR REPLACE INTO sales VALUES (?, ?, ?, ?, ?, ?)', sales_data)
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("✅ Test database created successfully!")
    print("📊 Database contains:")
    print("   - 5 categories")
    print("   - 10 products")
    print("   - 8 customers")
    print("   - 200 sales records (past 6 months)")
    print("\n🔗 Connection string for testing:")
    print("   sqlite:///test_database.db")
    print("\n💡 Example queries to try:")
    print("   - 'Show me total sales by category'")
    print("   - 'What are the top 5 products by revenue?'")
    print("   - 'How many sales were made last month?'")
    print("   - 'Show me sales trends over time'")

if __name__ == "__main__":
    create_test_database()
