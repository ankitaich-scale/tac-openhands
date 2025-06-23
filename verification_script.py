#!/usr/bin/env python3

import sqlite3
import os

def verify_database():
    """Verify that the database meets all requirements"""
    
    print("=== DATABASE VERIFICATION ===")
    
    # Check if database exists
    db_path = '/data/coffee_shop.db'
    if os.path.exists(db_path):
        print("✓ Database exists at /data/coffee_shop.db")
    else:
        print("✗ Database not found at /data/coffee_shop.db")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables exist and match CSV file names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = ['customers', 'products', 'inventory', 'orders', 'order_items']
    for table in expected_tables:
        if table in tables:
            print(f"✓ Table '{table}' exists")
        else:
            print(f"✗ Table '{table}' missing")
    
    # Check views exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = [row[0] for row in cursor.fetchall()]
    
    expected_views = ['v_short_stock', 'v_sales']
    for view in expected_views:
        if view in views:
            print(f"✓ View '{view}' exists")
        else:
            print(f"✗ View '{view}' missing")
    
    # Check v_short_stock structure
    cursor.execute("PRAGMA table_info(v_short_stock)")
    v_short_stock_columns = [row[1] for row in cursor.fetchall()]
    expected_short_stock_cols = ['product_id', 'quantity_in_stock', 'reorder_point']
    
    print(f"\nv_short_stock columns: {v_short_stock_columns}")
    if set(v_short_stock_columns) == set(expected_short_stock_cols):
        print("✓ v_short_stock has correct columns")
    else:
        print("✗ v_short_stock has incorrect columns")
    
    # Check v_sales structure
    cursor.execute("PRAGMA table_info(v_sales)")
    v_sales_columns = [row[1] for row in cursor.fetchall()]
    expected_sales_cols = ['product_id', 'average_sales', 'revenue_generated', 'profit_generated']
    
    print(f"v_sales columns: {v_sales_columns}")
    if set(v_sales_columns) == set(expected_sales_cols):
        print("✓ v_sales has correct columns")
    else:
        print("✗ v_sales has incorrect columns")
    
    # Check data in views
    cursor.execute("SELECT COUNT(*) FROM v_short_stock")
    short_stock_count = cursor.fetchone()[0]
    print(f"✓ v_short_stock contains {short_stock_count} products that need reordering")
    
    cursor.execute("SELECT COUNT(*) FROM v_sales")
    sales_count = cursor.fetchone()[0]
    print(f"✓ v_sales contains {sales_count} products with sales data")
    
    # Check floating point rounding
    cursor.execute("SELECT average_sales, revenue_generated, profit_generated FROM v_sales LIMIT 1")
    row = cursor.fetchone()
    if row:
        avg_sales, revenue, profit = row
        # Check if values are rounded to 2 decimal places
        avg_decimals = len(str(avg_sales).split('.')[-1]) if '.' in str(avg_sales) else 0
        revenue_decimals = len(str(revenue).split('.')[-1]) if '.' in str(revenue) else 0
        profit_decimals = len(str(profit).split('.')[-1]) if '.' in str(profit) else 0
        
        if avg_decimals <= 2 and revenue_decimals <= 2 and profit_decimals <= 2:
            print("✓ Floating point numbers are rounded to 2 decimal places")
        else:
            print(f"✗ Floating point rounding issue: {avg_decimals}, {revenue_decimals}, {profit_decimals} decimals")
    
    conn.close()
    
    # Check analysis.txt file
    analysis_path = '/workspace/analysis.txt'
    if os.path.exists(analysis_path):
        print("✓ analysis.txt file exists in workspace")
        with open(analysis_path, 'r') as f:
            content = f.read()
            if '<ANSWER HERE>' not in content:
                print("✓ All answers have been filled in analysis.txt")
            else:
                print("✗ Some answers are still missing in analysis.txt")
    else:
        print("✗ analysis.txt file not found in workspace")
    
    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    verify_database()