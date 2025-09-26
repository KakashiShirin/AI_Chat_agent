#!/usr/bin/env python3
"""
Data Import Script for Cordly AI - Olist E-commerce Dataset
This script imports CSV files into PostgreSQL database
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'cordly_ai',
    'user': 'postgres',
    'password': input('Enter PostgreSQL password: ')  # You can also set this as an environment variable
}

# CSV file mappings
CSV_FILES = {
    'olist_customers_dataset.csv': 'olist_customers_dataset',
    'olist_geolocation_dataset.csv': 'olist_geolocation_dataset',
    'olist_order_items_dataset.csv': 'olist_order_items_dataset',
    'olist_order_payments_dataset.csv': 'olist_order_payments_dataset',
    'olist_order_reviews_dataset.csv': 'olist_order_reviews_dataset',
    'olist_orders_dataset.csv': 'olist_orders_dataset',
    'olist_products_dataset.csv': 'olist_products_dataset',
    'olist_sellers_dataset.csv': 'olist_sellers_dataset',
    'product_category_name_translation.csv': 'product_category_name_translation'
}

def connect_to_database():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Successfully connected to PostgreSQL database")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def import_csv_to_table(conn, csv_file_path, table_name):
    """Import CSV file to PostgreSQL table"""
    try:
        logger.info(f"Importing {csv_file_path} to {table_name}")
        
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded {len(df)} rows from {csv_file_path}")
        
        # Handle NaN values
        df = df.fillna('')
        
        # Convert DataFrame to list of tuples
        data = [tuple(row) for row in df.values]
        
        # Get column names
        columns = list(df.columns)
        
        # Create INSERT query
        placeholders = ','.join(['%s'] * len(columns))
        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        
        # Execute batch insert
        cursor = conn.cursor()
        execute_values(cursor, query, data, page_size=1000)
        conn.commit()
        cursor.close()
        
        logger.info(f"Successfully imported {len(data)} rows to {table_name}")
        
    except Exception as e:
        logger.error(f"Error importing {csv_file_path}: {e}")
        conn.rollback()
        raise

def main():
    """Main function to import all CSV files"""
    data_dir = Path('data')
    
    # Check if data directory exists
    if not data_dir.exists():
        logger.error("Data directory not found. Please create 'data' folder and place CSV files there.")
        return
    
    # Connect to database
    conn = connect_to_database()
    
    try:
        # Import each CSV file
        for csv_file, table_name in CSV_FILES.items():
            csv_path = data_dir / csv_file
            
            if csv_path.exists():
                import_csv_to_table(conn, csv_path, table_name)
            else:
                logger.warning(f"CSV file not found: {csv_path}")
        
        logger.info("Data import completed successfully!")
        
        # Display summary
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                n_tup_ins as row_count
            FROM pg_stat_user_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        results = cursor.fetchall()
        logger.info("\nTable row counts:")
        for row in results:
            logger.info(f"  {row[1]}: {row[2]} rows")
        
        cursor.close()
        
    except Exception as e:
        logger.error(f"Error during import process: {e}")
    finally:
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main()
