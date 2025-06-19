#!/usr/bin/env python3

import sqlite3
import csv
import os

def create_database():
    # Connect to SQLite database
    conn = sqlite3.connect('/data/coffee_shop.db')
    cursor = conn.cursor()
    
    # CSV files and their corresponding table structures
    csv_files = {
        'customers.csv': {
            'table_name': 'customers',
            'columns': [
                'customer_id INTEGER PRIMARY KEY',
                'name TEXT',
                'email TEXT',
                'shipping_address TEXT'
            ]
        },
        'inventory.csv': {
            'table_name': 'inventory',
            'columns': [
                'product_id TEXT PRIMARY KEY',
                'quantity_in_stock INTEGER',
                'reorder_point INTEGER',
                'last_restocked DATE'
            ]
        },
        'order_items.csv': {
            'table_name': 'order_items',
            'columns': [
                'order_id INTEGER',
                'product_id TEXT',
                'quantity INTEGER',
                'unit_price REAL'
            ]
        },
        'orders.csv': {
            'table_name': 'orders',
            'columns': [
                'order_id INTEGER PRIMARY KEY',
                'customer_id INTEGER',
                'order_date DATE',
                'payment_status TEXT',
                'total_amount REAL'
            ]
        },
        'products.csv': {
            'table_name': 'products',
            'columns': [
                'product_id TEXT PRIMARY KEY',
                'name TEXT',
                'category TEXT',
                'unit_price REAL',
                'unit_cost REAL',
                'supplier TEXT'
            ]
        }
    }
    
    # Create tables and import data
    for csv_file, table_info in csv_files.items():
        table_name = table_info['table_name']
        columns = table_info['columns']
        
        # Drop table if exists
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        
        # Create table
        create_table_sql = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        cursor.execute(create_table_sql)
        print(f"Created table: {table_name}")
        
        # Import data from CSV
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Skip header row
            
            # Prepare insert statement
            placeholders = ', '.join(['?' for _ in headers])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
            
            # Insert data
            for row in csv_reader:
                cursor.execute(insert_sql, row)
        
        print(f"Imported data into table: {table_name}")
    
    # Create view v_short_stock
    cursor.execute('DROP VIEW IF EXISTS v_short_stock')
    cursor.execute('''
        CREATE VIEW v_short_stock AS
        SELECT 
            product_id,
            ROUND(quantity_in_stock, 2) as quantity_in_stock,
            ROUND(reorder_point, 2) as reorder_point
        FROM inventory
        WHERE quantity_in_stock < reorder_point
    ''')
    print("Created view: v_short_stock")
    
    # Create view v_sales
    cursor.execute('DROP VIEW IF EXISTS v_sales')
    cursor.execute('''
        CREATE VIEW v_sales AS
        SELECT 
            oi.product_id,
            ROUND(AVG(oi.quantity), 2) as average_sales,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) as revenue_generated,
            ROUND(SUM(oi.quantity * (oi.unit_price - p.unit_cost)), 2) as profit_generated
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY oi.product_id
    ''')
    print("Created view: v_sales")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database created successfully at /data/coffee_shop.db")

if __name__ == "__main__":
    create_database()