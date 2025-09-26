-- Database Performance Indexes for Cordly AI
-- These indexes optimize common query patterns for the AI agent

-- Customer-related indexes
CREATE INDEX IF NOT EXISTS idx_customers_state ON olist_customers_dataset(customer_state);
CREATE INDEX IF NOT EXISTS idx_customers_city ON olist_customers_dataset(customer_city);
CREATE INDEX IF NOT EXISTS idx_customers_zip_prefix ON olist_customers_dataset(customer_zip_code_prefix);

-- Order-related indexes
CREATE INDEX IF NOT EXISTS idx_orders_status ON olist_orders_dataset(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_purchase_date ON olist_orders_dataset(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_orders_delivered_date ON olist_orders_dataset(order_delivered_customer_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON olist_orders_dataset(customer_id);

-- Order items indexes
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON olist_order_items_dataset(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON olist_order_items_dataset(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_seller_id ON olist_order_items_dataset(seller_id);
CREATE INDEX IF NOT EXISTS idx_order_items_price ON olist_order_items_dataset(price);

-- Payment indexes
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON olist_order_payments_dataset(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_type ON olist_order_payments_dataset(payment_type);
CREATE INDEX IF NOT EXISTS idx_payments_value ON olist_order_payments_dataset(payment_value);

-- Review indexes
CREATE INDEX IF NOT EXISTS idx_reviews_order_id ON olist_order_reviews_dataset(order_id);
CREATE INDEX IF NOT EXISTS idx_reviews_score ON olist_order_reviews_dataset(review_score);
CREATE INDEX IF NOT EXISTS idx_reviews_creation_date ON olist_order_reviews_dataset(review_creation_date);

-- Product indexes
CREATE INDEX IF NOT EXISTS idx_products_category ON olist_products_dataset(product_category_name);
CREATE INDEX IF NOT EXISTS idx_products_weight ON olist_products_dataset(product_weight_g);
CREATE INDEX IF NOT EXISTS idx_products_price_range ON olist_products_dataset(product_length_cm, product_height_cm, product_width_cm);

-- Seller indexes
CREATE INDEX IF NOT EXISTS idx_sellers_state ON olist_sellers_dataset(seller_state);
CREATE INDEX IF NOT EXISTS idx_sellers_city ON olist_sellers_dataset(seller_city);

-- Geolocation indexes
CREATE INDEX IF NOT EXISTS idx_geo_state ON olist_geolocation_dataset(geolocation_state);
CREATE INDEX IF NOT EXISTS idx_geo_city ON olist_geolocation_dataset(geolocation_city);
CREATE INDEX IF NOT EXISTS idx_geo_zip_prefix ON olist_geolocation_dataset(geolocation_zip_code_prefix);

-- Composite indexes for common join patterns
CREATE INDEX IF NOT EXISTS idx_orders_customer_status ON olist_orders_dataset(customer_id, order_status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_product ON olist_order_items_dataset(order_id, product_id);
CREATE INDEX IF NOT EXISTS idx_payments_order_type ON olist_order_payments_dataset(order_id, payment_type);

-- Date-based indexes for time series queries
CREATE INDEX IF NOT EXISTS idx_orders_purchase_year_month ON olist_orders_dataset(DATE_TRUNC('month', order_purchase_timestamp));
CREATE INDEX IF NOT EXISTS idx_reviews_creation_year_month ON olist_order_reviews_dataset(DATE_TRUNC('month', review_creation_date));

-- Analyze tables to update statistics
ANALYZE olist_customers_dataset;
ANALYZE olist_orders_dataset;
ANALYZE olist_order_items_dataset;
ANALYZE olist_order_payments_dataset;
ANALYZE olist_order_reviews_dataset;
ANALYZE olist_products_dataset;
ANALYZE olist_sellers_dataset;
ANALYZE olist_geolocation_dataset;
ANALYZE product_category_name_translation;
