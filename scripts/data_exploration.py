#!/usr/bin/env python3
"""
Data Exploration Script for Cordly AI - Olist E-commerce Dataset
This script performs comprehensive data analysis and generates reports
"""

import os
import sys
import pandas as pd
import psycopg2
import numpy as np
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

def get_table_info(conn):
    """Get basic information about all tables"""
    cursor = conn.cursor()
    
    # Get table names and row counts
    cursor.execute("""
        SELECT 
            schemaname,
            relname as tablename,
            n_tup_ins as row_count
        FROM pg_stat_user_tables 
        WHERE schemaname = 'public'
        ORDER BY relname;
    """)
    
    tables_info = cursor.fetchall()
    
    logger.info("Database Tables Overview:")
    logger.info("=" * 50)
    for table in tables_info:
        logger.info(f"{table[1]}: {table[2]} rows")
    
    cursor.close()
    return tables_info

def analyze_data_quality(conn):
    """Analyze data quality issues"""
    cursor = conn.cursor()
    
    # Check for missing values in key tables
    key_tables = [
        'olist_orders_dataset',
        'olist_customers_dataset', 
        'olist_order_items_dataset'
    ]
    
    logger.info("\nData Quality Analysis:")
    logger.info("=" * 50)
    
    for table in key_tables:
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = '{table}'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        logger.info(f"\n{table} schema:")
        for col in columns:
            logger.info(f"  {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
    
    cursor.close()

def generate_sample_queries(conn):
    """Generate sample analytical queries to test the dataset"""
    cursor = conn.cursor()
    
    sample_queries = [
        {
            'name': 'Total Orders by Status',
            'query': """
                SELECT order_status, COUNT(*) as order_count
                FROM olist_orders_dataset
                GROUP BY order_status
                ORDER BY order_count DESC;
            """
        },
        {
            'name': 'Top 10 States by Customer Count',
            'query': """
                SELECT 
                    customer_state,
                    COUNT(*) as customer_count
                FROM olist_customers_dataset
                GROUP BY customer_state
                ORDER BY customer_count DESC
                LIMIT 10;
            """
        },
        {
            'name': 'Average Order Value by State',
            'query': """
                SELECT 
                    c.customer_state,
                    COUNT(DISTINCT o.order_id) as order_count,
                    AVG(oi.price) as avg_order_value
                FROM olist_orders_dataset o
                JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
                JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
                GROUP BY c.customer_state
                ORDER BY avg_order_value DESC
                LIMIT 10;
            """
        },
        {
            'name': 'Payment Methods Distribution',
            'query': """
                SELECT 
                    payment_type,
                    COUNT(*) as payment_count,
                    AVG(payment_value) as avg_payment_value
                FROM olist_order_payments_dataset
                GROUP BY payment_type
                ORDER BY payment_count DESC;
            """
        },
        {
            'name': 'Monthly Order Trends',
            'query': """
                SELECT 
                    DATE_TRUNC('month', order_purchase_timestamp) as month,
                    COUNT(*) as order_count
                FROM olist_orders_dataset
                WHERE order_purchase_timestamp IS NOT NULL
                GROUP BY month
                ORDER BY month;
            """
        }
    ]
    
    logger.info("\nSample Analytical Queries:")
    logger.info("=" * 50)
    
    for query_info in sample_queries:
        logger.info(f"\n{query_info['name']}:")
        try:
            cursor.execute(query_info['query'])
            results = cursor.fetchall()
            
            # Get column names
            cursor.execute(query_info['query'])
            columns = [desc[0] for desc in cursor.description]
            
            # Display results
            df = pd.DataFrame(results, columns=columns)
            logger.info(df.to_string(index=False))
            
        except Exception as e:
            logger.error(f"Error executing query '{query_info['name']}': {e}")
    
    cursor.close()

def create_data_summary(conn):
    """Create a comprehensive data summary"""
    cursor = conn.cursor()
    
    logger.info("\nComprehensive Data Summary:")
    logger.info("=" * 50)
    
    # Overall statistics
    cursor.execute("SELECT COUNT(*) FROM olist_orders_dataset;")
    total_orders = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM olist_customers_dataset;")
    total_customers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM olist_order_items_dataset;")
    total_items = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM olist_sellers_dataset;")
    total_sellers = cursor.fetchone()[0]
    
    logger.info(f"Total Orders: {total_orders:,}")
    logger.info(f"Total Customers: {total_customers:,}")
    logger.info(f"Total Order Items: {total_items:,}")
    logger.info(f"Total Sellers: {total_sellers:,}")
    
    # Date range
    cursor.execute("""
        SELECT 
            MIN(order_purchase_timestamp) as earliest_order,
            MAX(order_purchase_timestamp) as latest_order
        FROM olist_orders_dataset
        WHERE order_purchase_timestamp IS NOT NULL;
    """)
    
    date_range = cursor.fetchone()
    if date_range[0] and date_range[1]:
        logger.info(f"Date Range: {date_range[0]} to {date_range[1]}")
    
    # Geographic distribution
    cursor.execute("""
        SELECT 
            customer_state,
            COUNT(*) as customer_count
        FROM olist_customers_dataset
        GROUP BY customer_state
        ORDER BY customer_count DESC
        LIMIT 5;
    """)
    
    top_states = cursor.fetchall()
    logger.info("\nTop 5 States by Customer Count:")
    for state, count in top_states:
        logger.info(f"  {state}: {count:,} customers")
    
    cursor.close()

def main():
    """Main function to run data exploration"""
    # Create output directory
    output_dir = Path('data')
    output_dir.mkdir(exist_ok=True)
    
    # Connect to database
    conn = connect_to_database()
    
    try:
        # Run analysis
        get_table_info(conn)
        analyze_data_quality(conn)
        generate_sample_queries(conn)
        create_data_summary(conn)
        
        logger.info("\nData exploration completed successfully!")
        logger.info("The dataset is ready for AI agent development.")
        
    except Exception as e:
        logger.error(f"Error during data exploration: {e}")
    finally:
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main()