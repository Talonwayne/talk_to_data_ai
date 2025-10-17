#!/usr/bin/env python3
"""
Setup a comprehensive test SQLite database with lots of realistic data
This allows testing without requiring PostgreSQL
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random
import os

def create_comprehensive_test_database():
    """Create a comprehensive test database with realistic sample data"""
    
    # Remove existing database if it exists
    if os.path.exists('test_database.db'):
        os.remove('test_database.db')
    
    # Connect to SQLite database (creates if doesn't exist)
    conn = sqlite3.connect('test_database.db')
    cursor = conn.cursor()
    
    # Create tables with more comprehensive structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category_id INTEGER,
            price DECIMAL(10,2),
            cost DECIMAL(10,2),
            sku TEXT UNIQUE,
            description TEXT,
            in_stock BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            region TEXT,
            city TEXT,
            country TEXT,
            customer_type TEXT,
            registration_date DATE,
            total_spent DECIMAL(10,2) DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT,
            position TEXT,
            hire_date DATE,
            salary DECIMAL(10,2),
            manager_id INTEGER,
            FOREIGN KEY (manager_id) REFERENCES employees (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            customer_id INTEGER,
            employee_id INTEGER,
            amount DECIMAL(10,2),
            quantity INTEGER,
            discount_percent DECIMAL(5,2) DEFAULT 0,
            sale_date DATE,
            payment_method TEXT,
            region TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            quantity INTEGER,
            reorder_level INTEGER,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marketing_campaigns (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            campaign_type TEXT,
            start_date DATE,
            end_date DATE,
            budget DECIMAL(10,2),
            spent DECIMAL(10,2) DEFAULT 0,
            status TEXT
        )
    ''')
    
    # Insert comprehensive data
    
    # Categories
    categories_data = [
        (1, 'Electronics', 'Electronic devices and accessories', '2024-01-01 00:00:00'),
        (2, 'Clothing', 'Apparel and fashion items', '2024-01-01 00:00:00'),
        (3, 'Books', 'Books and educational materials', '2024-01-01 00:00:00'),
        (4, 'Home & Garden', 'Home improvement and garden supplies', '2024-01-01 00:00:00'),
        (5, 'Sports', 'Sports equipment and fitness gear', '2024-01-01 00:00:00'),
        (6, 'Beauty', 'Beauty and personal care products', '2024-01-01 00:00:00'),
        (7, 'Automotive', 'Car parts and automotive accessories', '2024-01-01 00:00:00'),
        (8, 'Toys', 'Toys and games for children', '2024-01-01 00:00:00'),
        (9, 'Food & Beverage', 'Food and drink products', '2024-01-01 00:00:00'),
        (10, 'Health', 'Health and wellness products', '2024-01-01 00:00:00')
    ]
    
    # Products (100 products)
    products_data = []
    for i in range(1, 101):
        category_id = random.randint(1, 10)
        base_price = random.uniform(10, 1000)
        cost = base_price * random.uniform(0.4, 0.7)
        
        product_names = {
            1: ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Camera', 'Monitor', 'Keyboard', 'Mouse', 'Speaker', 'Charger'],
            2: ['T-Shirt', 'Jeans', 'Dress', 'Jacket', 'Shoes', 'Hat', 'Socks', 'Belt', 'Scarf', 'Gloves'],
            3: ['Programming Book', 'Fiction Novel', 'Textbook', 'Biography', 'Cookbook', 'Travel Guide', 'Dictionary', 'Magazine', 'Comic', 'Manual'],
            4: ['Garden Tools', 'Furniture', 'Lighting', 'Paint', 'Hardware', 'Plants', 'Seeds', 'Soil', 'Pots', 'Decor'],
            5: ['Running Shoes', 'Basketball', 'Tennis Racket', 'Yoga Mat', 'Dumbbells', 'Bike', 'Helmet', 'Water Bottle', 'Gym Bag', 'Stopwatch'],
            6: ['Shampoo', 'Lotion', 'Makeup', 'Perfume', 'Soap', 'Cream', 'Serum', 'Mask', 'Brush', 'Mirror'],
            7: ['Tire', 'Oil Filter', 'Brake Pad', 'Battery', 'Headlight', 'Mirror', 'Floor Mat', 'Air Freshener', 'Tool Kit', 'Jump Starter'],
            8: ['Action Figure', 'Board Game', 'Puzzle', 'Doll', 'Building Blocks', 'Art Set', 'Remote Car', 'Robot', 'Stuffed Animal', 'Card Game'],
            9: ['Coffee', 'Tea', 'Snacks', 'Candy', 'Juice', 'Water', 'Cereal', 'Pasta', 'Sauce', 'Spices'],
            10: ['Vitamins', 'Supplements', 'Thermometer', 'Bandage', 'Medicine', 'Scale', 'Blood Pressure Monitor', 'First Aid Kit', 'Pill Organizer', 'Massage Oil']
        }
        
        name = random.choice(product_names[category_id]) + f" {i}"
        sku = f"SKU-{category_id:02d}-{i:03d}"
        description = f"High-quality {name.lower()} for everyday use"
        
        products_data.append((
            i, name, category_id, round(base_price, 2), round(cost, 2), 
            sku, description, random.choice([True, True, True, False]),  # Mostly in stock
            '2024-01-01 00:00:00'  # created_at
        ))
    
    # Customers (200 customers)
    customers_data = []
    regions = ['North', 'South', 'East', 'West', 'Central']
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
    countries = ['USA', 'Canada', 'Mexico']
    customer_types = ['Individual', 'Business', 'VIP']
    
    for i in range(1, 201):
        name = f"Customer {i}"
        email = f"customer{i}@email.com"
        phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        region = random.choice(regions)
        city = random.choice(cities)
        country = random.choice(countries)
        customer_type = random.choice(customer_types)
        
        # Registration date in the past 2 years
        reg_date = datetime.now() - timedelta(days=random.randint(1, 730))
        
        customers_data.append((
            i, name, email, phone, region, city, country, 
            customer_type, reg_date.strftime('%Y-%m-%d'), 0
        ))
    
    # Employees (50 employees)
    employees_data = []
    departments = ['Sales', 'Marketing', 'IT', 'HR', 'Finance', 'Operations', 'Customer Service']
    positions = ['Manager', 'Senior', 'Junior', 'Specialist', 'Analyst', 'Coordinator', 'Director']
    
    for i in range(1, 51):
        name = f"Employee {i}"
        email = f"employee{i}@company.com"
        department = random.choice(departments)
        position = random.choice(positions)
        
        # Hire date in the past 5 years
        hire_date = datetime.now() - timedelta(days=random.randint(1, 1825))
        
        salary = random.uniform(30000, 150000)
        manager_id = random.randint(1, 10) if i > 10 else None
        
        employees_data.append((
            i, name, email, department, position, 
            hire_date.strftime('%Y-%m-%d'), round(salary, 2), manager_id
        ))
    
    # Sales (2000 sales records)
    sales_data = []
    payment_methods = ['Credit Card', 'Debit Card', 'Cash', 'PayPal', 'Bank Transfer']
    
    for i in range(1, 2001):
        product_id = random.randint(1, 100)
        customer_id = random.randint(1, 200)
        employee_id = random.randint(1, 50)
        quantity = random.randint(1, 10)
        
        # Get product price (simplified)
        base_price = random.uniform(10, 1000)
        discount = random.uniform(0, 0.3)  # 0-30% discount
        amount = base_price * quantity * (1 - discount)
        
        # Sale date in the past 2 years
        sale_date = datetime.now() - timedelta(days=random.randint(1, 730))
        
        payment_method = random.choice(payment_methods)
        region = random.choice(regions)
        
        sales_data.append((
            i, product_id, customer_id, employee_id, round(amount, 2), 
            quantity, round(discount * 100, 2), sale_date.strftime('%Y-%m-%d'),
            payment_method, region
        ))
    
    # Inventory
    inventory_data = []
    for i in range(1, 101):
        quantity = random.randint(0, 500)
        reorder_level = random.randint(10, 100)
        inventory_data.append((i, i, quantity, reorder_level, '2024-01-01 00:00:00'))
    
    # Marketing Campaigns
    campaigns_data = [
        (1, 'Summer Sale 2024', 'Promotional', '2024-06-01', '2024-08-31', 50000, 45000, 'Completed'),
        (2, 'Black Friday 2024', 'Seasonal', '2024-11-24', '2024-11-30', 100000, 95000, 'Completed'),
        (3, 'New Year Campaign', 'Brand Awareness', '2024-12-15', '2025-01-15', 75000, 30000, 'Active'),
        (4, 'Spring Collection', 'Product Launch', '2024-03-01', '2024-05-31', 60000, 58000, 'Completed'),
        (5, 'Holiday Special', 'Seasonal', '2024-12-01', '2024-12-25', 80000, 75000, 'Completed'),
        (6, 'Back to School', 'Educational', '2024-08-15', '2024-09-15', 40000, 38000, 'Completed'),
        (7, 'Tech Innovation', 'Product Launch', '2024-09-01', '2024-11-30', 120000, 45000, 'Active'),
        (8, 'Fitness Challenge', 'Engagement', '2024-01-01', '2024-03-31', 30000, 28000, 'Completed'),
        (9, 'Beauty Week', 'Promotional', '2024-04-15', '2024-04-22', 25000, 24000, 'Completed'),
        (10, 'Automotive Expo', 'Trade Show', '2024-10-01', '2024-10-07', 150000, 145000, 'Completed')
    ]
    
    # Insert all data
    cursor.executemany('INSERT INTO categories VALUES (?, ?, ?, ?)', categories_data)
    cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', products_data)
    cursor.executemany('INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', customers_data)
    cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?)', employees_data)
    cursor.executemany('INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', sales_data)
    cursor.executemany('INSERT INTO inventory VALUES (?, ?, ?, ?, ?)', inventory_data)
    cursor.executemany('INSERT INTO marketing_campaigns VALUES (?, ?, ?, ?, ?, ?, ?, ?)', campaigns_data)
    
    # Update customer total spent
    cursor.execute('''
        UPDATE customers 
        SET total_spent = (
            SELECT COALESCE(SUM(amount), 0) 
            FROM sales 
            WHERE sales.customer_id = customers.id
        )
    ''')
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("✅ Comprehensive test database created successfully!")
    print("📊 Database contains:")
    print("   - 10 categories")
    print("   - 100 products")
    print("   - 200 customers")
    print("   - 50 employees")
    print("   - 2000 sales records (past 2 years)")
    print("   - 100 inventory records")
    print("   - 10 marketing campaigns")
    print("\n🔗 Connection string for testing:")
    print("   sqlite:///test_database.db")
    print("\n💡 Example queries to try:")
    print("   - 'Show me total sales by category'")
    print("   - 'What are the top 10 products by revenue?'")
    print("   - 'How many sales were made last month?'")
    print("   - 'Show me sales trends over time'")
    print("   - 'Which employees have the highest sales?'")
    print("   - 'What is our inventory status?'")
    print("   - 'Show me customer distribution by region'")
    print("   - 'Which marketing campaigns were most successful?'")

if __name__ == "__main__":
    create_comprehensive_test_database()
