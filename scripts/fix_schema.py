#!/usr/bin/env python3
"""
Fix schema for products table to handle large integer values
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

def fix_schema():
    """Fix the products table schema"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        logger.info("Fixing products table schema...")
        
        # Drop and recreate products table with BIGINT for large values
        cursor.execute("DROP TABLE IF EXISTS olist_products_dataset CASCADE;")
        
        cursor.execute("""
            CREATE TABLE olist_products_dataset (
                product_id VARCHAR(50) PRIMARY KEY,
                product_category_name VARCHAR(100),
                product_name_lenght BIGINT,
                product_description_lenght BIGINT,
                product_photos_qty BIGINT,
                product_weight_g BIGINT,
                product_length_cm BIGINT,
                product_height_cm BIGINT,
                product_width_cm BIGINT
            );
        """)
        
        # Recreate the index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON olist_products_dataset(product_category_name);")
        
        # Recreate foreign key constraint for order_items
        cursor.execute("""
            ALTER TABLE olist_order_items_dataset 
            ADD CONSTRAINT fk_order_items_product 
            FOREIGN KEY (product_id) REFERENCES olist_products_dataset(product_id);
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Products table schema updated successfully!")
        
    except Exception as e:
        logger.error(f"Error fixing schema: {e}")
        raise

if __name__ == "__main__":
    fix_schema()
