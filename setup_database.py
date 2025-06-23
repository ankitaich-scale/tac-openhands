#!/usr/bin/env python3

import sqlite3
import csv
import os

def create_database():
    """Create SQLite database and tables from CSV files"""
    
    # Connect to database
    conn = sqlite3.connect('/data/coffee_shop.db')
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            shipping_address TEXT NOT NULL
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price REAL NOT NULL,
            unit_cost REAL NOT NULL,
            supplier TEXT NOT NULL
        )
    ''')
    
    # Create inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            product_id TEXT PRIMARY KEY,
            quantity_in_stock INTEGER NOT NULL,
            reorder_point INTEGER NOT NULL,
            last_restocked DATE NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date DATE NOT NULL,
            payment_status TEXT NOT NULL,
            total_amount REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    # Create order_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            order_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            PRIMARY KEY (order_id, product_id),
            FOREIGN KEY (order_id) REFERENCES orders (order_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')
    
    # Load data from CSV files
    load_csv_data(cursor)
    
    # Create views
    create_views(cursor)
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("Database created successfully!")

def load_csv_data(cursor):
    """Load data from CSV files into tables"""
    
    # Load customers
    with open('/workspace/customers.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO customers (customer_id, name, email, shipping_address)
                VALUES (?, ?, ?, ?)
            ''', (int(row['customer_id']), row['name'], row['email'], row['shipping_address']))
    
    # Load products
    with open('/workspace/products.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO products (product_id, name, category, unit_price, unit_cost, supplier)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['product_id'], row['name'], row['category'], 
                  round(float(row['unit_price']), 2), round(float(row['unit_cost']), 2), row['supplier']))
    
    # Load inventory
    with open('/workspace/inventory.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO inventory (product_id, quantity_in_stock, reorder_point, last_restocked)
                VALUES (?, ?, ?, ?)
            ''', (row['product_id'], int(row['quantity_in_stock']), 
                  int(row['reorder_point']), row['last_restocked']))
    
    # Load orders
    with open('/workspace/orders.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO orders (order_id, customer_id, order_date, payment_status, total_amount)
                VALUES (?, ?, ?, ?, ?)
            ''', (int(row['order_id']), int(row['customer_id']), row['order_date'], 
                  row['payment_status'], round(float(row['total_amount']), 2)))
    
    # Load order_items
    with open('/workspace/order_items.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            ''', (int(row['order_id']), row['product_id'], int(row['quantity']), 
                  round(float(row['unit_price']), 2)))

def create_views(cursor):
    """Create the required views"""
    
    # Create v_short_stock view - products that need to be reordered
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_short_stock AS
        SELECT 
            product_id,
            quantity_in_stock,
            reorder_point
        FROM inventory
        WHERE quantity_in_stock <= reorder_point
    ''')
    
    # Create v_sales view - sales details for each product
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_sales AS
        SELECT 
            oi.product_id,
            ROUND(AVG(oi.quantity), 2) as average_sales,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) as revenue_generated,
            ROUND(SUM(oi.quantity * (oi.unit_price - p.unit_cost)), 2) as profit_generated
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY oi.product_id
    ''')

if __name__ == "__main__":
    create_database()