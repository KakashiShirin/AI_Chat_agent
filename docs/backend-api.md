# Backend API Documentation

## Overview

The Cordly AI backend provides a RESTful API for natural language to SQL conversion with intelligent query processing and response formatting.

## Architecture

### Hybrid AI Service
- **Rule-based generation** for simple queries (COUNT, TOP, AVERAGE, SUM)
- **Hugging Face AI** for complex queries (microsoft/DialoGPT-small)
- **Automatic fallback** to rule-based if AI fails
- **Smart query routing** based on complexity detection

### Database Service
- **Async PostgreSQL** connection pool
- **Schema introspection** and caching
- **Query validation** and safety checks
- **Performance optimization** through connection pooling

## API Endpoints

### 1. Health Check

**GET** `/health`

Returns the health status of the application and its services.

**Response**:
```json
{
  "status": "healthy",
  "services": {
    "ai_service": true,
    "db_service": true
  }
}
```

### 2. Ask Question

**POST** `/api/ask`

Processes a natural language question and returns structured results with visualizations.

**Request Body**:
```json
{
  "question": "What are the top 5 states by customer count?"
}
```

**Response**:
```json
{
  "summary": "The results show the top 10 records.",
  "visualization": {
    "type": "bar_chart",
    "data": [...],
    "dataKey": "customer_state",
    "barKey": "customer_count",
    "title": "Top 10 by customer_count"
  },
  "tableData": {
    "columns": ["customer_state", "customer_count"],
    "rows": [["SP", 41746], ["RJ", 12852], ...]
  },
  "sqlQuery": "SELECT customer_state, COUNT(*) as customer_count FROM olist_customers_dataset GROUP BY customer_state ORDER BY customer_count DESC LIMIT 10;",
  "executionTime": 0.025426864624023438
}
```

### 3. Database Schema

**GET** `/api/schema`

Returns comprehensive database schema information.

**Response**:
```json
{
  "schema": {
    "olist_orders_dataset": {
      "columns": {
        "order_id": {
          "data_type": "character varying",
          "is_nullable": false,
          "column_default": null
        },
        ...
      },
      "primary_keys": ["order_id"],
      "foreign_keys": [
        {
          "column": "customer_id",
          "references_table": "olist_customers_dataset",
          "references_column": "customer_id"
        }
      ]
    },
    ...
  }
}
```

### 4. Available Tables

**GET** `/api/tables`

Returns a list of available database tables.

**Response**:
```json
{
  "tables": [
    "olist_customers_dataset",
    "olist_geolocation_dataset",
    "olist_order_items_dataset",
    "olist_order_payments_dataset",
    "olist_order_reviews_dataset",
    "olist_orders_dataset",
    "olist_products_dataset",
    "olist_sellers_dataset",
    "product_category_name_translation"
  ]
}
```

### 5. Sample Queries

**GET** `/api/sample-queries`

Returns example questions that users can ask.

**Response**:
```json
{
  "sample_queries": [
    "What are the top 5 product categories by revenue?",
    "Which states have the highest average order value?",
    "How many orders were placed each month in 2017?",
    "What is the distribution of payment methods?",
    "Which sellers have the highest customer satisfaction?",
    "What are the most popular products in São Paulo?",
    "How does order volume vary by day of the week?",
    "What is the average delivery time by state?",
    "Which product categories have the highest profit margins?",
    "How many customers made repeat purchases?"
  ]
}
```

## Query Processing Pipeline

### 1. Query Analysis
- Extract keywords and intent from natural language
- Identify relevant database tables
- Determine query complexity

### 2. Generation Method Selection
- **Simple queries**: Rule-based generation
- **Complex queries**: AI-based generation
- **Fallback**: Rule-based if AI fails

### 3. SQL Generation
- **Rule-based**: Pattern matching and template generation
- **AI-based**: Hugging Face model with schema context
- **Validation**: Safety checks and query validation

### 4. Execution and Formatting
- Execute SQL query against database
- Format results for frontend consumption
- Generate visualization data
- Create natural language summary

## Supported Query Types

### Simple Queries (Rule-based)
- **COUNT**: "How many orders are there?"
- **TOP**: "What are the top 5 states by customer count?"
- **AVERAGE**: "What is the average order value?"
- **SUM**: "What is the total revenue?"
- **TIME SERIES**: "Show monthly order trends"

### Complex Queries (AI-based)
- **MULTI-TABLE JOINS**: "Which products have the highest customer satisfaction?"
- **COMPLEX FILTERS**: "Find customers in São Paulo who bought electronics"
- **AGGREGATIONS**: "Average order value by state and product category"
- **TEMPORAL ANALYSIS**: "Customer behavior changes over time"

## Error Handling

### 1. Query Validation
- SQL injection prevention
- Dangerous operation blocking
- Syntax validation

### 2. Fallback Mechanisms
- AI service unavailable → Rule-based generation
- Database connection issues → Graceful error messages
- Invalid queries → Helpful error responses

### 3. Error Responses
```json
{
  "error": "Processing failed",
  "message": "Unable to generate SQL for the given question",
  "details": {
    "suggestion": "Try rephrasing your question or ask a simpler query"
  }
}
```

## Performance Metrics

### Response Times
- **Simple queries**: 0.01-0.03 seconds
- **Complex queries**: 0.5-2.0 seconds
- **Fallback queries**: 0.01-0.03 seconds

### Resource Usage
- **Memory**: ~500MB (optimized for Vercel)
- **CPU**: Efficient serverless execution
- **Network**: Minimal API calls

## Security Considerations

### 1. Query Safety
- Only SELECT statements allowed
- No DDL or DML operations
- Parameterized queries to prevent injection

### 2. Rate Limiting
- Built-in request throttling
- Hugging Face API rate limits
- Database connection limits

### 3. Data Privacy
- No sensitive data exposure
- Query logging for debugging only
- Secure API key management

## Deployment Configuration

### Environment Variables
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cordly_ai
DB_USER=postgres
DB_PASSWORD=your_password

# Hugging Face Configuration
HF_API_TOKEN=your_token  # Optional for free tier
```

### Vercel Configuration
- **Runtime**: Python 3.9+
- **Memory**: 1024MB
- **Timeout**: 10 seconds
- **Dependencies**: Lightweight for fast cold starts

## Monitoring and Logging

### 1. Application Logs
- Query processing steps
- Performance metrics
- Error tracking
- AI service status

### 2. Metrics
- Response times
- Success/failure rates
- AI vs rule-based usage
- Database performance

### 3. Health Monitoring
- Service availability
- Database connectivity
- AI service status
- Resource usage

## Future Enhancements

### 1. Planned Features
- **Query caching**: Cache frequent queries
- **Advanced visualizations**: More chart types
- **Query optimization**: SQL performance improvements
- **User analytics**: Query pattern analysis

### 2. Scalability Improvements
- **Horizontal scaling**: Load balancing
- **Database optimization**: Connection pooling
- **CDN integration**: Static asset optimization
- **Monitoring**: Comprehensive metrics and alerts
