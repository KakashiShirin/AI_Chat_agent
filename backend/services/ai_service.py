"""
AI service for Text-to-SQL generation and natural language processing
Using a lightweight rule-based approach for Vercel deployment
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
import json
import re
import pandas as pd

from .db_service import DatabaseService
from models.schemas import VisualizationType

logger = logging.getLogger(__name__)

class AIService:
    """Service for rule-based Text-to-SQL generation (Vercel-optimized)"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.schema_info = None
        self.table_aliases = {
            'orders': 'olist_orders_dataset',
            'order': 'olist_orders_dataset',
            'customers': 'olist_customers_dataset',
            'customer': 'olist_customers_dataset',
            'products': 'olist_products_dataset',
            'product': 'olist_products_dataset',
            'sellers': 'olist_sellers_dataset',
            'seller': 'olist_sellers_dataset',
            'payments': 'olist_order_payments_dataset',
            'payment': 'olist_order_payments_dataset',
            'reviews': 'olist_order_reviews_dataset',
            'review': 'olist_order_reviews_dataset',
            'items': 'olist_order_items_dataset',
            'item': 'olist_order_items_dataset',
            'geolocation': 'olist_geolocation_dataset',
            'categories': 'product_category_name_translation',
            'category': 'product_category_name_translation'
        }
    
    async def initialize(self):
        """Initialize the AI service and load schema information"""
        try:
            logger.info("Initializing lightweight AI service...")
            
            # Load schema information
            self.schema_info = await self.db_service.get_schema_info()
            
            logger.info("AI service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            raise
    
    def _extract_keywords(self, question: str) -> Dict[str, Any]:
        """Extract keywords and intent from the question"""
        question_lower = question.lower()
        
        # Common patterns
        patterns = {
            'top': r'\b(top|highest|best|most)\b',
            'count': r'\b(count|how many|number of)\b',
            'average': r'\b(average|avg|mean)\b',
            'sum': r'\b(sum|total)\b',
            'by': r'\b(by|grouped by|group by)\b',
            'where': r'\b(where|in|from|of)\b',
            'order': r'\b(order|orders)\b',
            'customer': r'\b(customer|customers)\b',
            'product': r'\b(product|products)\b',
            'payment': r'\b(payment|payments)\b',
            'state': r'\b(state|states)\b',
            'category': r'\b(category|categories)\b',
            'revenue': r'\b(revenue|sales|money|value)\b',
            'month': r'\b(month|monthly)\b',
            'year': r'\b(year|yearly)\b',
            'date': r'\b(date|time|when)\b'
        }
        
        extracted = {}
        for key, pattern in patterns.items():
            if re.search(pattern, question_lower):
                extracted[key] = True
        
        return extracted
    
    def _identify_tables(self, question: str) -> List[str]:
        """Identify relevant tables from the question"""
        question_lower = question.lower()
        tables = []
        
        for alias, table_name in self.table_aliases.items():
            if alias in question_lower:
                tables.append(table_name)
        
        # If no specific tables found, use common ones
        if not tables:
            if any(word in question_lower for word in ['order', 'customer', 'product']):
                tables = ['olist_orders_dataset', 'olist_customers_dataset']
            else:
                tables = ['olist_orders_dataset']  # Default table
        
        return tables
    
    def _generate_sql_rule_based(self, question: str) -> str:
        """Generate SQL using rule-based approach"""
        keywords = self._extract_keywords(question)
        tables = self._identify_tables(question)
        
        # Check for specific patterns first
        if 'top' in keywords and 'state' in keywords and 'customer' in keywords:
            return self._generate_top_states_by_customers_query()
        elif 'top' in keywords and 'category' in keywords and 'revenue' in keywords:
            return self._generate_top_categories_by_revenue_query()
        elif 'top' in keywords and 'category' in keywords:
            return self._generate_top_categories_query()
        elif 'count' in keywords and 'order' in keywords:
            return self._generate_count_query(question, keywords, tables)
        elif 'count' in keywords and 'customer' in keywords:
            return self._generate_count_query(question, keywords, tables)
        elif 'count' in keywords and 'product' in keywords:
            return self._generate_count_query(question, keywords, tables)
        elif 'average' in keywords:
            return self._generate_average_query(question, keywords, tables)
        elif 'sum' in keywords:
            return self._generate_sum_query(question, keywords, tables)
        else:
            return self._generate_basic_query(question, keywords, tables)
    
    def _generate_count_query(self, question: str, keywords: Dict, tables: List[str]) -> str:
        """Generate COUNT queries"""
        if 'order' in keywords:
            return "SELECT COUNT(*) as total_orders FROM olist_orders_dataset;"
        elif 'customer' in keywords:
            return "SELECT COUNT(*) as total_customers FROM olist_customers_dataset;"
        elif 'product' in keywords:
            return "SELECT COUNT(*) as total_products FROM olist_products_dataset;"
        else:
            return "SELECT COUNT(*) as total_count FROM olist_orders_dataset;"
    
    def _generate_top_states_by_customers_query(self) -> str:
        """Generate query for top states by customer count"""
        return """
            SELECT customer_state, COUNT(*) as customer_count 
            FROM olist_customers_dataset 
            GROUP BY customer_state 
            ORDER BY customer_count DESC 
            LIMIT 10;
        """
    
    def _generate_top_categories_by_revenue_query(self) -> str:
        """Generate query for top categories by revenue"""
        return """
            SELECT p.product_category_name, SUM(oi.price) as total_revenue
            FROM olist_products_dataset p
            JOIN olist_order_items_dataset oi ON p.product_id = oi.product_id
            GROUP BY p.product_category_name
            ORDER BY total_revenue DESC
            LIMIT 10;
        """
    
    def _generate_top_categories_query(self) -> str:
        """Generate query for top categories by product count"""
        return """
            SELECT product_category_name, COUNT(*) as product_count
            FROM olist_products_dataset
            GROUP BY product_category_name
            ORDER BY product_count DESC
            LIMIT 10;
        """
    
    def _generate_average_query(self, question: str, keywords: Dict, tables: List[str]) -> str:
        """Generate AVERAGE queries"""
        if 'order' in keywords and 'value' in keywords:
            return """
                SELECT AVG(payment_value) as avg_order_value
                FROM olist_order_payments_dataset;
            """
        else:
            return """
                SELECT AVG(price) as avg_price
                FROM olist_order_items_dataset;
            """
    
    def _generate_sum_query(self, question: str, keywords: Dict, tables: List[str]) -> str:
        """Generate SUM queries"""
        return """
            SELECT SUM(payment_value) as total_revenue
            FROM olist_order_payments_dataset;
        """
    
    def _generate_basic_query(self, question: str, keywords: Dict, tables: List[str]) -> str:
        """Generate basic SELECT queries"""
        if 'month' in keywords or 'year' in keywords:
            return """
                SELECT DATE_TRUNC('month', order_purchase_timestamp) as month, 
                       COUNT(*) as order_count
                FROM olist_orders_dataset
                GROUP BY month
                ORDER BY month;
            """
        else:
            return """
                SELECT order_status, COUNT(*) as count
                FROM olist_orders_dataset
                GROUP BY order_status
                ORDER BY count DESC;
            """
    
    async def generate_sql(self, question: str) -> str:
        """Generate SQL query from natural language question using rule-based approach"""
        try:
            sql_query = self._generate_sql_rule_based(question)
            sql_query = self._clean_sql_query(sql_query)
            
            logger.info(f"Generated SQL: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """Clean and validate the generated SQL query"""
        # Remove extra whitespace
        sql_query = re.sub(r'\s+', ' ', sql_query.strip())
        
        # Ensure it ends with semicolon
        if not sql_query.endswith(';'):
            sql_query += ';'
        
        # Basic validation - ensure it starts with SELECT
        if not sql_query.upper().startswith('SELECT'):
            raise ValueError("Generated query is not a SELECT statement")
        
        return sql_query
    
    async def process_question(self, question: str) -> Dict[str, Any]:
        """Process a natural language question and return structured response"""
        try:
            # Generate SQL query
            sql_query = await self.generate_sql(question)
            
            # Validate query safety
            if not await self.db_service.validate_query(sql_query):
                raise ValueError("Generated query is not safe to execute")
            
            # Execute query
            results = await self.db_service.execute_query(sql_query)
            
            if not results:
                return {
                    "summary": "No data found for your query.",
                    "sqlQuery": sql_query,
                    "tableData": {
                        "columns": [],
                        "rows": []
                    }
                }
            
            # Convert results to DataFrame for analysis
            df = pd.DataFrame(results)
            
            # Generate summary
            summary = self._generate_summary(question, df)
            
            # Determine visualization type and create data
            visualization = self._create_visualization(question, df)
            
            # Create table data
            table_data = {
                "columns": list(df.columns),
                "rows": df.values.tolist()
            }
            
            return {
                "summary": summary,
                "visualization": visualization,
                "tableData": table_data,
                "sqlQuery": sql_query
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            raise
    
    def _generate_summary(self, question: str, df: pd.DataFrame) -> str:
        """Generate a natural language summary of the results"""
        try:
            num_rows = len(df)
            
            if num_rows == 0:
                return "No data found for your query."
            
            # Basic summary based on question type
            if "top" in question.lower() or "highest" in question.lower():
                if num_rows == 1:
                    return f"The result shows {num_rows} record."
                else:
                    return f"The results show the top {num_rows} records."
            
            elif "count" in question.lower() or "how many" in question.lower():
                if num_rows == 1 and len(df.columns) == 1:
                    count_value = df.iloc[0, 0]
                    return f"The count is {count_value}."
                else:
                    return f"Found {num_rows} records."
            
            elif "average" in question.lower() or "avg" in question.lower():
                return f"The analysis shows {num_rows} data points."
            
            else:
                return f"Query returned {num_rows} records."
                
        except Exception as e:
            logger.warning(f"Error generating summary: {e}")
            return f"Query returned {len(df)} records."
    
    def _create_visualization(self, question: str, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Create visualization data based on the question and results"""
        try:
            if len(df) == 0:
                return None
            
            # Determine visualization type based on question and data
            question_lower = question.lower()
            
            # Check for time-based questions
            if any(word in question_lower for word in ["month", "year", "date", "time", "trend"]):
                return self._create_time_series_chart(df)
            
            # Check for comparison questions
            elif any(word in question_lower for word in ["top", "highest", "best", "compare"]):
                return self._create_bar_chart(df)
            
            # Check for distribution questions
            elif any(word in question_lower for word in ["distribution", "percentage", "share"]):
                return self._create_pie_chart(df)
            
            # Default to table for complex data
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Error creating visualization: {e}")
            return None
    
    def _create_bar_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create bar chart data"""
        try:
            # Find the best columns for x and y axes
            numeric_cols = df.select_dtypes(include=['number']).columns
            text_cols = df.select_dtypes(include=['object']).columns
            
            if len(text_cols) > 0 and len(numeric_cols) > 0:
                x_col = text_cols[0]
                y_col = numeric_cols[0]
                
                # Limit to top 10 for readability
                df_sorted = df.sort_values(y_col, ascending=False).head(10)
                
                return {
                    "type": VisualizationType.BAR_CHART,
                    "data": df_sorted.to_dict('records'),
                    "dataKey": x_col,
                    "barKey": y_col,
                    "title": f"Top {len(df_sorted)} by {y_col}"
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Error creating bar chart: {e}")
            return None
    
    def _create_pie_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create pie chart data"""
        try:
            # Find the best columns for labels and values
            numeric_cols = df.select_dtypes(include=['number']).columns
            text_cols = df.select_dtypes(include=['object']).columns
            
            if len(text_cols) > 0 and len(numeric_cols) > 0:
                label_col = text_cols[0]
                value_col = numeric_cols[0]
                
                # Limit to top 8 for readability
                df_sorted = df.sort_values(value_col, ascending=False).head(8)
                
                return {
                    "type": VisualizationType.PIE_CHART,
                    "data": df_sorted.to_dict('records'),
                    "dataKey": label_col,
                    "barKey": value_col,
                    "title": f"Distribution by {label_col}"
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Error creating pie chart: {e}")
            return None
    
    def _create_time_series_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create time series chart data"""
        try:
            # Find date/time columns
            date_cols = df.select_dtypes(include=['datetime64']).columns
            if len(date_cols) == 0:
                # Check for string columns that might be dates
                for col in df.columns:
                    if any(word in col.lower() for word in ['date', 'time', 'month', 'year']):
                        try:
                            df[col] = pd.to_datetime(df[col])
                            date_cols = [col]
                            break
                        except:
                            continue
            
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(date_cols) > 0 and len(numeric_cols) > 0:
                date_col = date_cols[0]
                value_col = numeric_cols[0]
                
                # Sort by date
                df_sorted = df.sort_values(date_col)
                
                return {
                    "type": VisualizationType.LINE_CHART,
                    "data": df_sorted.to_dict('records'),
                    "dataKey": date_col,
                    "barKey": value_col,
                    "title": f"Trend over time"
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Error creating time series chart: {e}")
            return None
