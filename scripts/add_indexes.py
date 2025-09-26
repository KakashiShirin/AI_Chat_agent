#!/usr/bin/env python3
"""
Add Database Indexes for Performance Optimization
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

def connect_to_database():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Successfully connected to PostgreSQL database")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def add_database_indexes():
    """Add performance indexes to the database"""
    conn = None
    cursor = None
    
    # Index definitions
    indexes = [
        # Customer-related indexes
        "CREATE INDEX IF NOT EXISTS idx_customers_state ON olist_customers_dataset(customer_state)",
        "CREATE INDEX IF NOT EXISTS idx_customers_city ON olist_customers_dataset(customer_city)",
        "CREATE INDEX IF NOT EXISTS idx_customers_zip_prefix ON olist_customers_dataset(customer_zip_code_prefix)",
        
        # Order-related indexes
        "CREATE INDEX IF NOT EXISTS idx_orders_status ON olist_orders_dataset(order_status)",
        "CREATE INDEX IF NOT EXISTS idx_orders_purchase_date ON olist_orders_dataset(order_purchase_timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_orders_delivered_date ON olist_orders_dataset(order_delivered_customer_date)",
        "CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON olist_orders_dataset(customer_id)",
        
        # Order items indexes
        "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON olist_order_items_dataset(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON olist_order_items_dataset(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_seller_id ON olist_order_items_dataset(seller_id)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_price ON olist_order_items_dataset(price)",
        
        # Payment indexes
        "CREATE INDEX IF NOT EXISTS idx_payments_order_id ON olist_order_payments_dataset(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_payments_type ON olist_order_payments_dataset(payment_type)",
        "CREATE INDEX IF NOT EXISTS idx_payments_value ON olist_order_payments_dataset(payment_value)",
        
        # Review indexes
        "CREATE INDEX IF NOT EXISTS idx_reviews_order_id ON olist_order_reviews_dataset(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_score ON olist_order_reviews_dataset(review_score)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_creation_date ON olist_order_reviews_dataset(review_creation_date)",
        
        # Product indexes
        "CREATE INDEX IF NOT EXISTS idx_products_category ON olist_products_dataset(product_category_name)",
        "CREATE INDEX IF NOT EXISTS idx_products_weight ON olist_products_dataset(product_weight_g)",
        
        # Seller indexes
        "CREATE INDEX IF NOT EXISTS idx_sellers_state ON olist_sellers_dataset(seller_state)",
        "CREATE INDEX IF NOT EXISTS idx_sellers_city ON olist_sellers_dataset(seller_city)",
        
        # Geolocation indexes
        "CREATE INDEX IF NOT EXISTS idx_geo_state ON olist_geolocation_dataset(geolocation_state)",
        "CREATE INDEX IF NOT EXISTS idx_geo_city ON olist_geolocation_dataset(geolocation_city)",
        "CREATE INDEX IF NOT EXISTS idx_geo_zip_prefix ON olist_geolocation_dataset(geolocation_zip_code_prefix)",
        
        # Composite indexes for common join patterns
        "CREATE INDEX IF NOT EXISTS idx_orders_customer_status ON olist_orders_dataset(customer_id, order_status)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_order_product ON olist_order_items_dataset(order_id, product_id)",
        "CREATE INDEX IF NOT EXISTS idx_payments_order_type ON olist_order_payments_dataset(order_id, payment_type)",
    ]
    
    # Tables to analyze
    tables_to_analyze = [
        'olist_customers_dataset',
        'olist_orders_dataset', 
        'olist_order_items_dataset',
        'olist_order_payments_dataset',
        'olist_order_reviews_dataset',
        'olist_products_dataset',
        'olist_sellers_dataset',
        'olist_geolocation_dataset',
        'product_category_name_translation'
    ]
    
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        
        logger.info("Creating database indexes...")
        
        # Create indexes
        for i, index_sql in enumerate(indexes, 1):
            try:
                cursor.execute(index_sql)
                logger.info(f"Created index {i}/{len(indexes)}")
            except Exception as e:
                logger.warning(f"Index {i} failed: {e}")
        
        conn.commit()
        logger.info("All indexes created successfully")
        
        # Analyze tables to update statistics
        logger.info("Updating table statistics...")
        for table in tables_to_analyze:
            try:
                cursor.execute(f"ANALYZE {table};")
                logger.info(f"Analyzed {table}")
            except Exception as e:
                logger.warning(f"Failed to analyze {table}: {e}")
        
        conn.commit()
        logger.info("Database optimization completed successfully!")
        
        # Show index information
        cursor.execute("""
            SELECT schemaname, tablename, indexname, indexdef 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname LIKE 'idx_%'
            ORDER BY tablename, indexname;
        """)
        
        indexes_created = cursor.fetchall()
        logger.info(f"Total indexes created: {len(indexes_created)}")
        
        for schema, table, index, definition in indexes_created:
            logger.info(f"  {table}.{index}")
        
    except Exception as e:
        logger.error(f"Error during index creation: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    add_database_indexes()
