#!/usr/bin/env python3

import sqlite3

def verify_database():
    conn = sqlite3.connect('/data/coffee_shop.db')
    cursor = conn.cursor()
    
    print("=== DATABASE VERIFICATION ===\n")
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables created:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check views
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    print("\nViews created:")
    for view in views:
        print(f"  - {view[0]}")
    
    # Check v_short_stock view
    print("\n=== v_short_stock VIEW ===")
    cursor.execute("SELECT * FROM v_short_stock")
    short_stock = cursor.fetchall()
    print("Products that need reordering:")
    for row in short_stock:
        print(f"  Product ID: {row[0]}, Stock: {row[1]}, Reorder Point: {row[2]}")
    
    # Check v_sales view
    print("\n=== v_sales VIEW ===")
    cursor.execute("SELECT * FROM v_sales ORDER BY profit_generated DESC")
    sales = cursor.fetchall()
    print("Sales data (ordered by profit):")
    for row in sales:
        print(f"  Product ID: {row[0]}, Avg Sales: {row[1]}, Revenue: ${row[2]}, Profit: ${row[3]}")
    
    # Check customers with pending payments
    print("\n=== PENDING PAYMENTS ===")
    cursor.execute("""
        SELECT c.name, o.order_id, o.total_amount 
        FROM customers c 
        JOIN orders o ON c.customer_id = o.customer_id 
        WHERE o.payment_status = 'PENDING'
    """)
    pending = cursor.fetchall()
    print("Customers with pending payments:")
    for row in pending:
        print(f"  Customer: {row[0]}, Order ID: {row[1]}, Amount: ${row[2]}")
    
    conn.close()
    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    verify_database()