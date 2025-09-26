#!/usr/bin/env python3
"""
Verify products table import
"""

import os
import sys
import psycopg2
import logging

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_products_import():
    """Verify products table import"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check row count
        cursor.execute("SELECT COUNT(*) FROM olist_products_dataset;")
        row_count = cursor.fetchone()[0]
        print(f"Products table row count: {row_count}")
        
        # Check sample data
        cursor.execute("SELECT product_id, product_category_name, product_weight_g FROM olist_products_dataset LIMIT 5;")
        print("Sample data:")
        for row in cursor.fetchall():
            print(f"  {row}")
        
        # Check data types
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'olist_products_dataset'
            ORDER BY ordinal_position;
        """)
        print("\nColumn data types:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Check for null values
        cursor.execute("""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(product_category_name) as category_count,
                COUNT(product_weight_g) as weight_count
            FROM olist_products_dataset;
        """)
        null_info = cursor.fetchone()
        print(f"\nNull value analysis:")
        print(f"  Total rows: {null_info[0]}")
        print(f"  Rows with category: {null_info[1]}")
        print(f"  Rows with weight: {null_info[2]}")
        
        cursor.close()
        conn.close()
        
        print("\nProducts table verification completed successfully!")
        
    except Exception as e:
        print(f"Error verifying products table: {e}")

if __name__ == "__main__":
    verify_products_import()
