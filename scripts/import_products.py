#!/usr/bin/env python3
"""
Import Products Table Script for Cordly AI - Olist E-commerce Dataset
This script specifically handles the products table import with proper NaN handling
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

def connect_to_database():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Successfully connected to PostgreSQL database")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def clean_products_dataframe(df):
    """Clean products dataframe to handle data type issues"""
    logger.info("Cleaning products data")
    
    # Handle NaN values - convert to None for PostgreSQL
    df = df.replace('', None)
    df = df.where(pd.notnull(df), None)
    
    # Convert numeric columns to proper types
    numeric_columns = [
        'product_name_lenght', 'product_description_lenght', 
        'product_photos_qty', 'product_weight_g', 
        'product_length_cm', 'product_height_cm', 'product_width_cm'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            # Convert to object type first to handle NaN properly
            df[col] = df[col].astype('object')
            # Replace NaN with None
            df[col] = df[col].where(pd.notnull(df[col]), None)
            # Convert valid numeric values to int
            df[col] = df[col].apply(lambda x: int(float(x)) if x is not None and str(x) != 'nan' else None)
    
    return df

def import_products_table(conn, csv_file_path, table_name):
    """Import products CSV file to PostgreSQL table"""
    try:
        logger.info(f"Importing {csv_file_path} to {table_name}")
        
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded {len(df)} rows from {csv_file_path}")
        
        # Clean the dataframe
        df = clean_products_dataframe(df)
        
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

def clear_products_table(conn):
    """Clear products table"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("TRUNCATE TABLE olist_products_dataset CASCADE;")
        conn.commit()
        logger.info("Cleared products table")
    except Exception as e:
        logger.warning(f"Could not clear products table: {e}")
    
    cursor.close()

def main():
    """Main function to import products table"""
    data_dir = Path('data')
    csv_file = 'olist_products_dataset.csv'
    table_name = 'olist_products_dataset'
    
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
        # Clear existing data
        clear_products_table(conn)
        
        # Import products table
        import_products_table(conn, csv_path, table_name)
        
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
