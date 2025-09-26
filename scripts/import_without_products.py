#!/usr/bin/env python3
"""
Import Script for Cordly AI - Olist E-commerce Dataset (without products table)
This script imports CSV files into PostgreSQL database, skipping the problematic products table
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import logging
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CSV file mappings - Import in order to respect foreign key constraints (skip products for now)
CSV_FILES = [
    ('olist_customers_dataset.csv', 'olist_customers_dataset'),
    ('olist_geolocation_dataset.csv', 'olist_geolocation_dataset'),
    ('olist_sellers_dataset.csv', 'olist_sellers_dataset'),
    # ('olist_products_dataset.csv', 'olist_products_dataset'),  # Skip for now
    ('product_category_name_translation.csv', 'product_category_name_translation'),
    ('olist_orders_dataset.csv', 'olist_orders_dataset'),
    ('olist_order_items_dataset.csv', 'olist_order_items_dataset'),
    ('olist_order_payments_dataset.csv', 'olist_order_payments_dataset'),
    ('olist_order_reviews_dataset.csv', 'olist_order_reviews_dataset')
]

def connect_to_database():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Successfully connected to PostgreSQL database")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def clean_dataframe(df, table_name):
    """Clean dataframe to handle data type issues"""
    logger.info(f"Cleaning data for {table_name}")
    
    # Handle NaN values - convert to None for PostgreSQL
    df = df.replace('', None)
    df = df.where(pd.notnull(df), None)
    
    return df

def import_csv_to_table(conn, csv_file_path, table_name):
    """Import CSV file to PostgreSQL table"""
    try:
        logger.info(f"Importing {csv_file_path} to {table_name}")
        
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded {len(df)} rows from {csv_file_path}")
        
        # Clean the dataframe
        df = clean_dataframe(df, table_name)
        
        # Convert DataFrame to list of tuples
        data = [tuple(row) for row in df.values]
        
        # Get column names
        columns = list(df.columns)
        
        # Create INSERT query for execute_values
        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES %s"
        
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

def clear_tables(conn):
    """Clear all data from tables"""
    cursor = conn.cursor()
    
    # Disable foreign key constraints
    cursor.execute("SET session_replication_role = replica;")
    
    # Clear tables in reverse order to respect foreign keys
    tables_to_clear = [
        'olist_order_reviews_dataset',
        'olist_order_payments_dataset', 
        'olist_order_items_dataset',
        'olist_orders_dataset',
        'product_category_name_translation',
        'olist_products_dataset',
        'olist_sellers_dataset',
        'olist_geolocation_dataset',
        'olist_customers_dataset'
    ]
    
    for table in tables_to_clear:
        try:
            cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
            logger.info(f"Cleared table: {table}")
        except Exception as e:
            logger.warning(f"Could not clear table {table}: {e}")
    
    conn.commit()
    cursor.close()
    logger.info("All tables cleared successfully")

def main():
    """Main function to reset and import all CSV files"""
    data_dir = Path('data')
    
    # Check if data directory exists
    if not data_dir.exists():
        logger.error("Data directory not found. Please create 'data' folder and place CSV files there.")
        return
    
    # Connect to database
    conn = connect_to_database()
    
    try:
        # Clear existing data
        clear_tables(conn)
        
        # Import each CSV file in order
        for csv_file, table_name in CSV_FILES:
            csv_path = data_dir / csv_file
            
            if csv_path.exists():
                import_csv_to_table(conn, csv_path, table_name)
            else:
                logger.warning(f"CSV file not found: {csv_path}")
        
        # Re-enable foreign key constraints
        cursor = conn.cursor()
        cursor.execute("SET session_replication_role = DEFAULT;")
        conn.commit()
        cursor.close()
        logger.info("Re-enabled foreign key constraints")
        
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
