-- Database Setup Script for Cordly AI - Olist E-commerce Dataset
-- This script creates all tables and imports the Brazilian E-commerce dataset
-- Note: Run this script while connected to the cordly_ai database

-- Create tables for Olist dataset

-- 1. Customers dataset
CREATE TABLE IF NOT EXISTS olist_customers_dataset (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);

-- 2. Geolocation dataset
CREATE TABLE IF NOT EXISTS olist_geolocation_dataset (
    geolocation_zip_code_prefix VARCHAR(10),
    geolocation_lat DECIMAL(10, 8),
    geolocation_lng DECIMAL(11, 8),
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(10)
);

-- 3. Order items dataset
CREATE TABLE IF NOT EXISTS olist_order_items_dataset (
    order_id VARCHAR(50),
    order_item_id INTEGER,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date TIMESTAMP,
    price DECIMAL(10, 2),
    freight_value DECIMAL(10, 2)
);

-- 4. Order payments dataset
CREATE TABLE IF NOT EXISTS olist_order_payments_dataset (
    order_id VARCHAR(50),
    payment_sequential INTEGER,
    payment_type VARCHAR(50),
    payment_installments INTEGER,
    payment_value DECIMAL(10, 2)
);

-- 5. Order reviews dataset
CREATE TABLE IF NOT EXISTS olist_order_reviews_dataset (
    review_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    review_score INTEGER,
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);

-- 6. Orders dataset (main table)
CREATE TABLE IF NOT EXISTS olist_orders_dataset (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_status VARCHAR(50),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

-- 7. Products dataset
CREATE TABLE IF NOT EXISTS olist_products_dataset (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);

-- 8. Sellers dataset
CREATE TABLE IF NOT EXISTS olist_sellers_dataset (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(10),
    seller_city VARCHAR(100),
    seller_state VARCHAR(10)
);

-- 9. Product category name translation
CREATE TABLE IF NOT EXISTS product_category_name_translation (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON olist_orders_dataset(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON olist_orders_dataset(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_purchase_date ON olist_orders_dataset(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON olist_order_items_dataset(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON olist_order_items_dataset(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_seller_id ON olist_order_items_dataset(seller_id);
CREATE INDEX IF NOT EXISTS idx_order_payments_order_id ON olist_order_payments_dataset(order_id);
CREATE INDEX IF NOT EXISTS idx_order_reviews_order_id ON olist_order_reviews_dataset(order_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON olist_products_dataset(product_category_name);
CREATE INDEX IF NOT EXISTS idx_geolocation_zip ON olist_geolocation_dataset(geolocation_zip_code_prefix);

-- Add foreign key constraints
ALTER TABLE olist_orders_dataset 
ADD CONSTRAINT fk_orders_customer 
FOREIGN KEY (customer_id) REFERENCES olist_customers_dataset(customer_id);

ALTER TABLE olist_order_items_dataset 
ADD CONSTRAINT fk_order_items_order 
FOREIGN KEY (order_id) REFERENCES olist_orders_dataset(order_id);

ALTER TABLE olist_order_items_dataset 
ADD CONSTRAINT fk_order_items_product 
FOREIGN KEY (product_id) REFERENCES olist_products_dataset(product_id);

ALTER TABLE olist_order_items_dataset 
ADD CONSTRAINT fk_order_items_seller 
FOREIGN KEY (seller_id) REFERENCES olist_sellers_dataset(seller_id);

ALTER TABLE olist_order_payments_dataset 
ADD CONSTRAINT fk_order_payments_order 
FOREIGN KEY (order_id) REFERENCES olist_orders_dataset(order_id);

ALTER TABLE olist_order_reviews_dataset 
ADD CONSTRAINT fk_order_reviews_order 
FOREIGN KEY (order_id) REFERENCES olist_orders_dataset(order_id);

-- Display table creation summary
SELECT 'Database setup completed successfully!' as status;
SELECT 'Tables created:' as info;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
