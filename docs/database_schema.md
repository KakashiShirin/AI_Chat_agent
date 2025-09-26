# Database Schema Documentation

## Overview
The Cordly AI project uses the Brazilian E-Commerce Public Dataset by Olist, imported into PostgreSQL. This document provides a comprehensive overview of the database schema and data quality.

## Database Statistics
- **Total Orders**: 99,441
- **Total Customers**: 99,441 (unique customers)
- **Total Order Items**: 112,650
- **Total Sellers**: 3,095
- **Date Range**: September 2016 to October 2018
- **Geographic Coverage**: All Brazilian states

## Table Schema

### 1. olist_orders_dataset (99,441 rows)
**Primary Table** - Contains order information
- `order_id` (VARCHAR, PRIMARY KEY) - Unique order identifier
- `customer_id` (VARCHAR) - Reference to customer
- `order_status` (VARCHAR) - Order status (delivered, shipped, canceled, etc.)
- `order_purchase_timestamp` (TIMESTAMP) - When order was placed
- `order_approved_at` (TIMESTAMP) - When order was approved
- `order_delivered_carrier_date` (TIMESTAMP) - When shipped to carrier
- `order_delivered_customer_date` (TIMESTAMP) - When delivered to customer
- `order_estimated_delivery_date` (TIMESTAMP) - Estimated delivery date

### 2. olist_customers_dataset (99,441 rows)
**Customer Information**
- `customer_id` (VARCHAR, PRIMARY KEY) - Unique customer identifier
- `customer_unique_id` (VARCHAR) - Unique customer ID
- `customer_zip_code_prefix` (VARCHAR) - ZIP code prefix
- `customer_city` (VARCHAR) - Customer city
- `customer_state` (VARCHAR) - Customer state (Brazilian states)

### 3. olist_order_items_dataset (112,650 rows)
**Order Items** - Individual items within orders
- `order_id` (VARCHAR) - Reference to order
- `order_item_id` (INTEGER) - Item sequence within order
- `product_id` (VARCHAR) - Reference to product
- `seller_id` (VARCHAR) - Reference to seller
- `shipping_limit_date` (TIMESTAMP) - Shipping deadline
- `price` (NUMERIC) - Item price
- `freight_value` (NUMERIC) - Shipping cost

### 4. olist_order_payments_dataset (103,886 rows)
**Payment Information**
- `order_id` (VARCHAR) - Reference to order
- `payment_sequential` (INTEGER) - Payment sequence
- `payment_type` (VARCHAR) - Payment method
- `payment_installments` (INTEGER) - Number of installments
- `payment_value` (NUMERIC) - Payment amount

### 5. olist_sellers_dataset (3,095 rows)
**Seller Information**
- `seller_id` (VARCHAR, PRIMARY KEY) - Unique seller identifier
- `seller_zip_code_prefix` (VARCHAR) - Seller ZIP code prefix
- `seller_city` (VARCHAR) - Seller city
- `seller_state` (VARCHAR) - Seller state

### 6. olist_geolocation_dataset (8,001,304 rows)
**Geographic Data**
- `geolocation_zip_code_prefix` (VARCHAR) - ZIP code prefix
- `geolocation_lat` (DECIMAL) - Latitude
- `geolocation_lng` (DECIMAL) - Longitude
- `geolocation_city` (VARCHAR) - City name
- `geolocation_state` (VARCHAR) - State name

### 7. olist_order_reviews_dataset (98,410 rows)
**Customer Reviews**
- `review_id` (VARCHAR, PRIMARY KEY) - Unique review identifier
- `order_id` (VARCHAR) - Reference to order
- `review_score` (INTEGER) - Review score (1-5)
- `review_comment_title` (VARCHAR) - Review title
- `review_comment_message` (TEXT) - Review message
- `review_creation_date` (TIMESTAMP) - When review was created
- `review_answer_timestamp` (TIMESTAMP) - When review was answered

### 8. product_category_name_translation (71 rows)
**Product Category Translations**
- `product_category_name` (VARCHAR, PRIMARY KEY) - Category name in Portuguese
- `product_category_name_english` (VARCHAR) - Category name in English

### 9. olist_products_dataset (32,951 rows)
**Product Information** - Successfully imported
- `product_id` (VARCHAR, PRIMARY KEY) - Unique product identifier
- `product_category_name` (VARCHAR) - Product category
- `product_name_lenght` (BIGINT) - Product name length
- `product_description_lenght` (BIGINT) - Description length
- `product_photos_qty` (BIGINT) - Number of photos
- `product_weight_g` (BIGINT) - Weight in grams
- `product_length_cm` (BIGINT) - Length in cm
- `product_height_cm` (BIGINT) - Height in cm
- `product_width_cm` (BIGINT) - Width in cm

## Data Quality Issues

### 1. Products Data Successfully Imported
- The `olist_products_dataset` table now contains 32,951 products
- All product information is available for analytics
- **Status**: ✅ Complete and ready for use

### 2. Incomplete Reviews Data
- Only 3,318 reviews imported out of expected ~99,000
- Duplicate key constraints caused import failures
- **Impact**: Limited review-based analytics

### 3. Data Completeness
- Some timestamp fields contain NULL values
- Geographic data has some inconsistencies
- **Impact**: May affect time-series and location-based queries

## Key Insights from Data Exploration

### Order Status Distribution
- **Delivered**: 96,478 orders (97%)
- **Shipped**: 1,107 orders (1.1%)
- **Canceled**: 625 orders (0.6%)
- **Other statuses**: <1% each

### Geographic Distribution
- **São Paulo (SP)**: 41,746 customers (42%)
- **Rio de Janeiro (RJ)**: 12,852 customers (13%)
- **Minas Gerais (MG)**: 11,635 customers (12%)
- **Other states**: <6% each

### Payment Methods
- **Credit Card**: 76,795 payments (74%)
- **Boleto**: 19,784 payments (19%)
- **Voucher**: 5,775 payments (6%)
- **Debit Card**: 1,529 payments (1%)

### Temporal Trends
- **Peak Activity**: November 2017 (7,544 orders)
- **Growth Period**: 2017-2018
- **Data Range**: September 2016 to October 2018

## Recommendations for AI Agent Development

### 1. Leverage Complete Product Data
- Use the full products dataset for product-level analytics
- Implement category-based filtering and analysis
- Provide rich product information in responses

### 2. Focus on Available Data
- Leverage order, customer, and payment data for most queries
- Use geographic data for location-based insights
- Implement time-series analysis using order timestamps

### 3. Data Validation
- Check for NULL values before processing
- Validate date ranges and formats
- Handle edge cases in geographic data

### 4. Query Optimization
- Use appropriate indexes for common query patterns
- Consider data partitioning for large tables
- Implement caching for frequently accessed data

## Sample Queries for Testing

### Basic Analytics
```sql
-- Total revenue by state
SELECT 
    c.customer_state,
    SUM(oi.price) as total_revenue,
    COUNT(DISTINCT o.order_id) as order_count
FROM olist_orders_dataset o
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_revenue DESC;
```

### Time Series Analysis
```sql
-- Monthly order trends
SELECT 
    DATE_TRUNC('month', order_purchase_timestamp) as month,
    COUNT(*) as order_count,
    AVG(oi.price) as avg_order_value
FROM olist_orders_dataset o
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY month
ORDER BY month;
```

### Customer Segmentation
```sql
-- Customer value analysis
SELECT 
    c.customer_id,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(oi.price) as total_spent,
    AVG(oi.price) as avg_order_value
FROM olist_customers_dataset c
JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
GROUP BY c.customer_id
ORDER BY total_spent DESC
LIMIT 10;
```

## Next Steps
1. ✅ **Products Import**: Successfully imported 32,951 products
2. ✅ **AI Agent Implementation**: Hybrid rule-based + AI approach
3. ✅ **API Endpoints**: RESTful API with natural language processing
4. ✅ **Reviews Import**: Successfully imported 98,410 reviews (duplicates removed)
5. **Create Indexes**: Add performance indexes for common query patterns
6. **Data Validation**: Implement comprehensive data quality checks
7. **Frontend Development**: React interface with chart visualizations
