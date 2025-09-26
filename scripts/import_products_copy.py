#!/usr/bin/env python3
"""
Import Products Table using PostgreSQL COPY command
This script uses COPY to import the products table directly
"""

import os
import sys
import pandas as pd
import psycopg2
import logging
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_to_database():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Successfully connected to PostgreSQL database")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def import_products_with_copy(conn, csv_file_path):
    """Import products using COPY command"""
    try:
        logger.info(f"Importing {csv_file_path} using COPY command")
        
        cursor = conn.cursor()
        
        # Clear the table first
        cursor.execute("TRUNCATE TABLE olist_products_dataset CASCADE;")
        logger.info("Cleared products table")
        
        # Use COPY command to import data
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            # Skip header row
            next(f)
            
            # Use COPY command
            cursor.copy_expert("""
                COPY olist_products_dataset (
                    product_id,
                    product_category_name,
                    product_name_lenght,
                    product_description_lenght,
                    product_photos_qty,
                    product_weight_g,
                    product_length_cm,
                    product_height_cm,
                    product_width_cm
                ) FROM STDIN WITH CSV NULL ''
            """, f)
        
        conn.commit()
        cursor.close()
        
        logger.info("Successfully imported products table using COPY command")
        
    except Exception as e:
        logger.error(f"Error importing with COPY: {e}")
        conn.rollback()
        raise

def main():
    """Main function to import products table"""
    data_dir = Path('data')
    csv_file = 'olist_products_dataset.csv'
    
    # Check if data directory exists
    if not data_dir.exists():
        logger.error("Data directory not found. Please create 'data' folder and place CSV files there.")
        return
    
    csv_path = data_dir / csv_file
    
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return
    
    # Connect to database
    conn = connect_to_database()
    
    try:
        # Import products table using COPY
        import_products_with_copy(conn, csv_path)
        
        logger.info("Products table import completed successfully!")
        
        # Display summary
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM olist_products_dataset;")
        row_count = cursor.fetchone()[0]
        logger.info(f"Products table now contains {row_count} rows")
        
        cursor.close()
        
    except Exception as e:
        logger.error(f"Error during products import process: {e}")
    finally:
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main()
