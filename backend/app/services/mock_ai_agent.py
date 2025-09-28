#!/usr/bin/env python3
"""
Mock AI Agent for testing Phase 2 without Hugging Face API
"""

import json
import pandas as pd
from typing import Dict, Any
from app.models.database import engine
from app.services.data_processor import data_processor
from sqlalchemy import text

class MockAIAgent:
    """Mock AI agent for testing without Hugging Face API"""
    
    def __init__(self):
        self.engine = engine
    
    def get_table_schema(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive schema information for AI analysis"""
        try:
            schema_info = data_processor.get_table_schema(session_id)
            
            # Enhance schema with sample data for better AI understanding
            enhanced_schema = {}
            with self.engine.connect() as connection:
                for table_name, table_info in schema_info.items():
                    # Get sample data (first 3 rows)
                    sample_query = text(f"SELECT * FROM {table_name} LIMIT 3")
                    sample_result = connection.execute(sample_query)
                    sample_data = [dict(row._mapping) for row in sample_result]
                    
                    enhanced_schema[table_name] = {
                        "columns": table_info["columns"],
                        "sample_data": sample_data,
                        "table_name": table_name
                    }
            
            return enhanced_schema
            
        except Exception as e:
            raise Exception(f"Error retrieving schema: {str(e)}")
    
    def execute_query(self, query: str, session_id: str) -> str:
        """Execute a simple query based on the question"""
        try:
            schema_info = self.get_table_schema(session_id)
            if not schema_info:
                return "No data found for this session"
            
            # Get the first table
            table_name = list(schema_info.keys())[0]
            
            with self.engine.connect() as connection:
                # Load data into pandas
                df = pd.read_sql(f"SELECT * FROM {table_name}", connection)
                
                # Simple query processing
                query_lower = query.lower()
                
                if "average salary" in query_lower or "avg salary" in query_lower:
                    # Convert salary to numeric, handling any data type issues
                    df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
                    avg_salary = df['salary'].mean()
                    return f"The average salary is ${avg_salary:,.2f}"
                
                elif "department" in query_lower and "how many" in query_lower:
                    dept_counts = df['department'].value_counts()
                    result = "Department counts:\n"
                    for dept, count in dept_counts.items():
                        result += f"  {dept}: {count} people\n"
                    return result.strip()
                
                elif "youngest" in query_lower:
                    df['age'] = pd.to_numeric(df['age'], errors='coerce')
                    youngest_idx = df['age'].idxmin()
                    youngest_person = df.loc[youngest_idx]
                    return f"The youngest employee is {youngest_person['name']} (age {youngest_person['age']})"
                
                elif "total salary" in query_lower and "engineering" in query_lower:
                    df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
                    eng_df = df[df['department'].str.lower() == 'engineering']
                    total_salary = eng_df['salary'].sum()
                    return f"Total salary for Engineering department: ${total_salary:,.2f}"
                
                elif "more than 70000" in query_lower or "> 70000" in query_lower:
                    df['salary'] = pd.to_numeric(df['salary'], errors='coerce')
                    high_earners = df[df['salary'] > 70000]
                    result = f"Employees earning more than $70,000:\n"
                    for _, person in high_earners.iterrows():
                        result += f"  {person['name']}: ${person['salary']:,.2f}\n"
                    return result.strip()
                
                else:
                    return f"Query processed. Found {len(df)} records in the dataset."
                    
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def generate_response(self, query: str, raw_data: str) -> Dict[str, Any]:
        """Generate a mock response"""
        return {
            "answer": raw_data,
            "explanation": f"This analysis was performed on your data based on the question: '{query}'",
            "chart_type": "table",
            "chart_data": raw_data
        }
    
    async def get_answer(self, query: str, session_id: str) -> Dict[str, Any]:
        """Main function to process user query and return mock analysis"""
        try:
            # Execute the query
            raw_result = self.execute_query(query, session_id)
            
            if raw_result.startswith("No data found"):
                return {
                    "error": "No data found for this session",
                    "answer": raw_result,
                    "chart_type": "none"
                }
            
            # Generate response
            result = self.generate_response(query, raw_result)
            result["raw_data"] = raw_result
            result["generated_code"] = "Mock code execution"
            
            return result
                
        except Exception as e:
            return {
                "error": str(e),
                "answer": f"I encountered an error while analyzing your data: {str(e)}",
                "chart_type": "none"
            }

# Create global instance
mock_ai_agent = MockAIAgent()
