#!/usr/bin/env python3
"""
Fixed Reviews Import Script
This script imports the olist_order_reviews_dataset.csv file into PostgreSQL database
while handling duplicate review_ids by keeping the first occurrence.
"""

import os
import sys
import psycopg2
import pandas as pd
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

def import_reviews_with_duplicate_handling():
    """Import olist_order_reviews_dataset.csv handling duplicates"""
    conn = None
    cursor = None
    data_dir = Path('data')
    csv_file_path = data_dir / 'olist_order_reviews_dataset.csv'
    table_name = 'olist_order_reviews_dataset'

    if not csv_file_path.exists():
        logger.error(f"CSV file not found: {csv_file_path}")
        return

    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # Load and process the CSV
        logger.info(f"Loading {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded {len(df)} rows from CSV")
        
        # Check for duplicates
        duplicate_count = df['review_id'].duplicated().sum()
        logger.info(f"Found {duplicate_count} duplicate review_ids in CSV")
        
        # Remove duplicates, keeping the first occurrence
        df_clean = df.drop_duplicates(subset=['review_id'], keep='first')
        logger.info(f"After removing duplicates: {len(df_clean)} rows")
        
        # Handle missing values
        df_clean = df_clean.where(pd.notnull(df_clean), None)
        
        # Clear existing data in the table
        logger.info(f"Clearing existing data in {table_name}")
        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
        conn.commit()
        
        # Prepare data for insertion
        columns = ['review_id', 'order_id', 'review_score', 'review_comment_title', 
                  'review_comment_message', 'review_creation_date', 'review_answer_timestamp']
        
        # Convert DataFrame to list of tuples
        data_tuples = [tuple(row) for row in df_clean[columns].values]
        
        # Insert data using execute_values for better performance
        from psycopg2.extras import execute_values
        
        insert_query = f"""
            INSERT INTO {table_name} 
            (review_id, order_id, review_score, review_comment_title, 
             review_comment_message, review_creation_date, review_answer_timestamp)
            VALUES %s
        """
        
        logger.info(f"Inserting {len(data_tuples)} rows into {table_name}")
        execute_values(cursor, insert_query, data_tuples, page_size=1000)
        conn.commit()
        
        # Verify row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
        logger.info(f"Successfully imported {row_count} rows to {table_name}")
        
        # Check for any remaining duplicates in database
        cursor.execute(f"""
            SELECT review_id, COUNT(*) as count 
            FROM {table_name} 
            GROUP BY review_id 
            HAVING COUNT(*) > 1 
            LIMIT 5;
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            logger.warning(f"Found {len(duplicates)} duplicate review_ids in database")
            for review_id, count in duplicates:
                logger.warning(f"  {review_id}: {count} occurrences")
        else:
            logger.info("No duplicate review_ids found in database")
        
        logger.info("Reviews table import completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during reviews import process: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    import_reviews_with_duplicate_handling()
