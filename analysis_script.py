#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timedelta

def analyze_reorder_needs():
    """Analyze which products need to be reordered within 7 days"""
    
    conn = sqlite3.connect('/data/coffee_shop.db')
    cursor = conn.cursor()
    
    # Get order date range to calculate daily sales rate
    cursor.execute("SELECT MIN(order_date), MAX(order_date) FROM orders")
    min_date, max_date = cursor.fetchone()
    
    # Calculate number of days in the data
    start_date = datetime.strptime(min_date, '%Y-%m-%d')
    end_date = datetime.strptime(max_date, '%Y-%m-%d')
    days_in_data = (end_date - start_date).days + 1
    
    print(f"Sales data spans {days_in_data} days (from {min_date} to {max_date})")
    
    # Get total sales per product and calculate daily rate
    cursor.execute('''
        SELECT 
            oi.product_id,
            SUM(oi.quantity) as total_sold,
            i.quantity_in_stock,
            i.reorder_point
        FROM order_items oi
        JOIN inventory i ON oi.product_id = i.product_id
        GROUP BY oi.product_id
    ''')
    
    products_to_reorder = []
    
    for row in cursor.fetchall():
        product_id, total_sold, current_stock, reorder_point = row
        daily_sales_rate = total_sold / days_in_data
        days_until_reorder = (current_stock - reorder_point) / daily_sales_rate if daily_sales_rate > 0 else float('inf')
        
        print(f"Product {product_id}:")
        print(f"  Current stock: {current_stock}")
        print(f"  Reorder point: {reorder_point}")
        print(f"  Total sold: {total_sold}")
        print(f"  Daily sales rate: {daily_sales_rate:.2f}")
        print(f"  Days until reorder point: {days_until_reorder:.1f}")
        
        # If already below reorder point or will be within 7 days
        if current_stock <= reorder_point or days_until_reorder <= 7:
            products_to_reorder.append(product_id)
        print()
    
    conn.close()
    return products_to_reorder

def get_top_profit_products():
    """Get top 3 products by profit"""
    
    conn = sqlite3.connect('/data/coffee_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT product_id, profit_generated 
        FROM v_sales 
        ORDER BY profit_generated DESC 
        LIMIT 3
    ''')
    
    top_products = [row[0] for row in cursor.fetchall()]
    conn.close()
    return top_products

def get_pending_customers():
    """Get customers with pending payments"""
    
    conn = sqlite3.connect('/data/coffee_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT c.name 
        FROM customers c 
        JOIN orders o ON c.customer_id = o.customer_id 
        WHERE o.payment_status = 'PENDING'
    ''')
    
    customers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return customers

if __name__ == "__main__":
    print("=== REORDER ANALYSIS ===")
    reorder_products = analyze_reorder_needs()
    print(f"Products to reorder within 7 days: {reorder_products}")
    
    print("\n=== TOP PROFIT PRODUCTS ===")
    top_profit = get_top_profit_products()
    print(f"Top 3 products by profit: {top_profit}")
    
    print("\n=== PENDING PAYMENTS ===")
    pending_customers = get_pending_customers()
    print(f"Customers with pending payments: {pending_customers}")