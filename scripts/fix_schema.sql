-- Fix schema for products table to handle large integer values
-- Run this after the initial schema creation

-- Drop and recreate products table with BIGINT for large values
DROP TABLE IF EXISTS olist_products_dataset CASCADE;

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

-- Recreate the index
CREATE INDEX IF NOT EXISTS idx_products_category ON olist_products_dataset(product_category_name);

-- Recreate foreign key constraint for order_items
ALTER TABLE olist_order_items_dataset 
ADD CONSTRAINT fk_order_items_product 
FOREIGN KEY (product_id) REFERENCES olist_products_dataset(product_id);

SELECT 'Products table schema updated successfully!' as status;
