import requests
import json
import io
import sys
import google.generativeai as genai
import logging
import time
from typing import Dict, Any, List
from contextlib import redirect_stdout
from app.core.config import settings
from app.models.database import engine
from app.services.data_processor import data_processor
from sqlalchemy import text
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgent:
    """Core AI analysis engine for natural language data queries"""
    
    def __init__(self):
        # Multi-Gemini API system
        self.gemini_api_keys = []
        self.current_api_index = 0
        self.gemini_model_name = 'gemini-2.0-flash'
        
        # Initialize with default API key if available
        default_key = getattr(settings, 'GEMINI_API_KEY', '')
        if default_key:
            self.gemini_api_keys.append(default_key)
            genai.configure(api_key=default_key)
            self.gemini_model = genai.GenerativeModel(self.gemini_model_name)
        
        # Retry and credit management settings
        self.max_retry_attempts = 3
        self.max_code_generation_attempts = 2
        self.max_synthesis_attempts = 2
        
        # Credit tracking per API key
        self.api_call_count = 0
        self.total_tokens_used = 0
        self.api_key_usage = {}  # Track usage per API key
        
    def add_gemini_api_key(self, api_key: str) -> bool:
        """Add a new Gemini API key to the pool"""
        try:
            # Test the API key first
            genai.configure(api_key=api_key)
            test_model = genai.GenerativeModel(self.gemini_model_name)
            test_response = test_model.generate_content("test")
            
            # If successful, add to pool
            if api_key not in self.gemini_api_keys:
                self.gemini_api_keys.append(api_key)
                self.api_key_usage[api_key] = {
                    'calls_made': 0,
                    'tokens_used': 0,
                    'last_used': None
                }
                logger.info(f"Added new Gemini API key (total: {len(self.gemini_api_keys)})")
                return True
            else:
                logger.warning("API key already exists")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add API key: {str(e)}")
            return False
    
    def get_next_api_key(self) -> str:
        """Get the next available API key in round-robin fashion"""
        if not self.gemini_api_keys:
            raise Exception("No Gemini API keys available")
        
        # Round-robin selection
        api_key = self.gemini_api_keys[self.current_api_index]
        self.current_api_index = (self.current_api_index + 1) % len(self.gemini_api_keys)
        
        return api_key
    
    
    def _call_gemini_api(self, prompt: str, api_key: str = None) -> str:
        """Call Google Gemini API with multi-key support"""
        try:
            # Use provided API key or get next available one
            if api_key is None:
                api_key = self.get_next_api_key()
            
            logger.info(f"Calling Gemini API with key #{self.gemini_api_keys.index(api_key) + 1}")
            
            # Configure Gemini with the specific API key
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(self.gemini_model_name)
            
            response = model.generate_content(prompt)
            result = response.text
            
            # Update usage tracking
            self.api_call_count += 1
            self.api_key_usage[api_key]['calls_made'] += 1
            self.api_key_usage[api_key]['last_used'] = time.time()
            
            # Log token usage if available
            if hasattr(response, 'usage_metadata'):
                tokens = response.usage_metadata.total_token_count
                self.total_tokens_used += tokens
                self.api_key_usage[api_key]['tokens_used'] += tokens
                logger.info(f"Gemini API call: {tokens} tokens used")
            
            # Extract code from markdown code blocks if present
            if "```python" in result:
                start = result.find("```python") + 9
                end = result.find("```", start)
                if end != -1:
                    result = result[start:end].strip()
            elif "```" in result:
                start = result.find("```") + 3
                end = result.find("```", start)
                if end != -1:
                    result = result[start:end].strip()
            
            logger.info(f"Gemini API call successful")
            return result
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _call_llm_api(self, prompt: str) -> str:
        """Call LLM API with multi-Gemini fallback system"""
        if not self.gemini_api_keys:
            raise Exception("No Gemini API keys available")
        
        last_error = None
        
        # Try each API key in order
        for i, api_key in enumerate(self.gemini_api_keys):
            try:
                logger.info(f"Trying Gemini API key #{i + 1}")
                return self._call_gemini_api(prompt, api_key)
            except Exception as e:
                last_error = e
                logger.warning(f"Gemini API key #{i + 1} failed: {str(e)}")
                continue
        
        # If all API keys failed
        raise Exception(f"All Gemini API keys failed. Last error: {last_error}")
    
    def get_table_schema(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive schema information for AI analysis"""
        try:
            schema_info = data_processor.get_table_schema(session_id)
            
            # Enhance schema with sample data for better AI understanding
            enhanced_schema = {}
            with engine.connect() as connection:
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
    
    def generate_pandas_prompt(self, query: str, schema_info: Dict[str, Any]) -> str:
        """Generate prompt for pandas code generation"""
        
        # Build schema description
        schema_description = "You are working with the following data tables:\n\n"
        for table_name, table_info in schema_info.items():
            schema_description += f"Table: {table_name}\n"
            schema_description += "Columns:\n"
            for col in table_info["columns"]:
                schema_description += f"  - {col['name']} ({col['type']})\n"
            
            if table_info.get("sample_data"):
                schema_description += "Sample data:\n"
                for i, row in enumerate(table_info["sample_data"][:2]):
                    schema_description += f"  Row {i+1}: {row}\n"
            schema_description += "\n"
        
        prompt = f"""You are an expert Python data analyst. Write ONLY executable Python code to answer the user's question.

{schema_description}

User's question: "{query}"

Write a complete Python script that:
1. Loads data from the PostgreSQL database using pd.read_sql()
2. Performs the analysis to answer the question
3. Prints only the final result

Database connection is available as 'engine' (SQLAlchemy engine).
Table name: {list(schema_info.keys())[0] if schema_info else 'data_table'}

IMPORTANT: Return ONLY the Python code, no explanations or markdown formatting.

Code:"""
        
        return prompt
    
    def _generate_code_with_retry(self, query: str, schema_info: Dict[str, Any], attempt: int = 1) -> str:
        """Generate code with retry logic and error feedback"""
        try:
            if attempt > self.max_code_generation_attempts:
                raise Exception(f"Maximum code generation attempts ({self.max_code_generation_attempts}) exceeded")
            
            # Generate prompt with error context if this is a retry
            if attempt > 1:
                error_context = f"\n\nIMPORTANT: This is attempt #{attempt}. Previous attempts failed. Please ensure the code is syntactically correct and uses only the available variables (pd, engine, text, session_id)."
                pandas_prompt = self.generate_pandas_prompt(query, schema_info) + error_context
            else:
                pandas_prompt = self.generate_pandas_prompt(query, schema_info)
            
            # Generate code using LLM
            generated_code = self._call_llm_api(pandas_prompt)
            
            if not generated_code or generated_code.strip() == "":
                raise Exception("Empty code generated")
            
            # Test the code syntax before returning
            try:
                compile(generated_code, '<string>', 'exec')
            except SyntaxError as e:
                raise Exception(f"Syntax error in generated code: {str(e)}")
            
            return generated_code
            
        except Exception as e:
            if attempt < self.max_code_generation_attempts:
                logger.warning(f"Code generation attempt {attempt} failed: {str(e)}")
                return self._generate_code_with_retry(query, schema_info, attempt + 1)
            else:
                logger.error(f"Code generation failed after {self.max_code_generation_attempts} attempts: {str(e)}")
                raise Exception(f"Code generation failed after {self.max_code_generation_attempts} attempts: {str(e)}")
    
    def _execute_code_with_retry(self, code: str, session_id: str, attempt: int = 1) -> str:
        """Execute code with retry logic and error feedback"""
        try:
            if attempt > self.max_retry_attempts:
                raise Exception(f"Maximum execution attempts ({self.max_retry_attempts}) exceeded")
            
            # Execute the code
            result = self.execute_code_safely(code, session_id)
            
            if result.startswith("Error executing code"):
                raise Exception(result)
            
            return result
            
        except Exception as e:
            if attempt < self.max_retry_attempts:
                logger.warning(f"Code execution attempt {attempt} failed: {str(e)}")
                # Try to fix the code based on the error
                fixed_code = self._fix_code_based_on_error(code, str(e))
                if fixed_code != code:
                    logger.info(f"Attempting to fix code based on error: {str(e)}")
                    return self._execute_code_with_retry(fixed_code, session_id, attempt + 1)
                else:
                    return self._execute_code_with_retry(code, session_id, attempt + 1)
            else:
                logger.error(f"Code execution failed after {self.max_retry_attempts} attempts: {str(e)}")
                raise Exception(f"Code execution failed after {self.max_retry_attempts} attempts: {str(e)}")
    
    def _fix_code_based_on_error(self, code: str, error_msg: str) -> str:
        """Attempt to fix code based on error message"""
        try:
            # Create a fix prompt for Gemini
            fix_prompt = f"""The following Python code failed to execute with this error:

ERROR: {error_msg}

CODE:
```python
{code}
```

Please fix the code to resolve the error. Return ONLY the corrected Python code, no explanations.

Fixed code:"""
            
            # Get fixed code from Gemini
            fixed_code = self._call_gemini_api(fix_prompt)
            
            # Extract code from markdown if present
            if "```python" in fixed_code:
                start = fixed_code.find("```python") + 9
                end = fixed_code.find("```", start)
                if end != -1:
                    fixed_code = fixed_code[start:end].strip()
            elif "```" in fixed_code:
                start = fixed_code.find("```") + 3
                end = fixed_code.find("```", start)
                if end != -1:
                    fixed_code = fixed_code[start:end].strip()
            
            return fixed_code
            
        except Exception as e:
            logger.error(f"Failed to fix code: {str(e)}")
            return code  # Return original code if fix fails
    
    def _synthesize_result_with_retry(self, query: str, raw_data: str, attempt: int = 1) -> str:
        """Synthesize result with retry logic"""
        try:
            if attempt > self.max_synthesis_attempts:
                raise Exception(f"Maximum synthesis attempts ({self.max_synthesis_attempts}) exceeded")
            
            synthesis_prompt = self.generate_synthesis_prompt(query, raw_data)
            synthesis_result = self._call_llm_api(synthesis_prompt)
            
            if not synthesis_result or synthesis_result.strip() == "":
                raise Exception("Empty synthesis result")
            
            return synthesis_result
            
        except Exception as e:
            if attempt < self.max_synthesis_attempts:
                logger.warning(f"Synthesis attempt {attempt} failed: {str(e)}")
                return self._synthesize_result_with_retry(query, raw_data, attempt + 1)
            else:
                logger.error(f"Synthesis failed after {self.max_synthesis_attempts} attempts: {str(e)}")
                raise Exception(f"Synthesis failed after {self.max_synthesis_attempts} attempts: {str(e)}")
    
    def execute_code_safely(self, code: str, session_id: str) -> str:
        
        # Create a safe execution environment
        safe_globals = {
            'pd': pd,
            'engine': engine,
            'text': text,
            'session_id': session_id,
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'min': min,
                'max': max,
                'sum': sum,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
                'any': any,
                'all': all,
                'isinstance': isinstance,
                'type': type,
                'hasattr': hasattr,
                'getattr': getattr,
                'setattr': setattr,
                '__import__': __import__,
            }
        }
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            # Execute the code
            exec(code, safe_globals)
            result = captured_output.getvalue()
            return result.strip()
            
        except Exception as e:
            return f"Error executing code: {str(e)}"
        finally:
            # Restore stdout
            sys.stdout = old_stdout
    
    def get_credit_usage(self) -> Dict[str, Any]:
        """Get current credit usage statistics for all API keys"""
        return {
            "total_api_calls": self.api_call_count,
            "total_tokens_used": self.total_tokens_used,
            "estimated_cost_usd": self.total_tokens_used * 0.000001,  # Rough estimate
            "api_keys_count": len(self.gemini_api_keys),
            "api_key_usage": self.api_key_usage,
            "max_retry_attempts": self.max_retry_attempts,
            "max_code_generation_attempts": self.max_code_generation_attempts,
            "max_synthesis_attempts": self.max_synthesis_attempts
        }
    
    def reset_credit_tracking(self):
        """Reset credit tracking counters for all API keys"""
        self.api_call_count = 0
        self.total_tokens_used = 0
        for api_key in self.api_key_usage:
            self.api_key_usage[api_key] = {
                'calls_made': 0,
                'tokens_used': 0,
                'last_used': None
            }
        logger.info("Credit tracking reset for all API keys")
    
    def generate_synthesis_prompt(self, query: str, raw_data: str) -> str:
        """Generate prompt for result synthesis"""
        
        prompt = f"""You are a helpful data analyst assistant. Given the user's question and the analysis results, provide a friendly, natural language response.

User's question: "{query}"

Analysis results: {raw_data}

Please provide:
1. A clear, conversational answer to the user's question
2. A brief explanation of what the data shows
3. Suggest an appropriate chart type for visualization (choose from: 'bar', 'line', 'pie', 'scatter', 'table', 'none')

Format your response as JSON:
{{
    "answer": "Your natural language answer here",
    "explanation": "Brief explanation of the findings",
    "chart_type": "suggested_chart_type",
    "chart_data": "Any specific data points for the chart (if applicable)"
}}

Response:"""
        
        return prompt
    
    def get_answer(self, query: str, session_id: str) -> Dict[str, Any]:
        """Main function to process user query and return AI analysis with comprehensive error handling"""
        try:
            logger.info(f"Processing query: '{query}' for session: {session_id}")
            
            # Step 1: Get schema information
            schema_info = data_processor.get_table_schema(session_id)
            
            if not schema_info:
                logger.warning(f"No schema found for session: {session_id}")
                return {
                    "error": "No data found for this session",
                    "answer": "I couldn't find any data associated with this session. Please upload a file first.",
                    "chart_type": "none"
                }
            
            logger.info(f"Schema retrieved for session {session_id}: {len(schema_info)} tables")
            
            # Step 2: Generate pandas code with retry logic
            generated_code = self._generate_code_with_retry(query, schema_info)
            
            if not generated_code:
                logger.error("Failed to generate analysis code")
                return {
                    "error": "Failed to generate analysis code",
                    "answer": "I'm having trouble analyzing your data right now. Please try again.",
                    "chart_type": "none"
                }
            
            logger.info("Code generated successfully")
            
            # Step 3: Execute the code safely with retry logic
            raw_result = self._execute_code_with_retry(generated_code, session_id)
            
            if raw_result.startswith("Error executing code"):
                logger.error(f"Code execution failed: {raw_result}")
                return {
                    "error": "Code execution failed",
                    "answer": f"I generated analysis code but encountered an error: {raw_result}",
                    "chart_type": "none"
                }
            
            logger.info("Code executed successfully")
            
            # Step 4: Synthesize the result with retry logic
            synthesis_result = self._synthesize_result_with_retry(query, raw_result)
            
            logger.info("Result synthesis completed")
            
            # Step 5: Parse the synthesis result
            try:
                # Try to parse as JSON
                synthesis_data = json.loads(synthesis_result)
                
                # Validate required fields
                if "answer" not in synthesis_data:
                    synthesis_data["answer"] = raw_result
                
                # Add metadata
                synthesis_data["generated_code"] = generated_code
                synthesis_data["raw_data"] = raw_result
                synthesis_data["api_calls_made"] = self.api_call_count
                synthesis_data["total_tokens_used"] = self.total_tokens_used
                
                logger.info(f"Query processed successfully. API calls made: {self.api_call_count}")
                return synthesis_data
                
            except json.JSONDecodeError:
                # If not JSON, create a simple response
                logger.warning("Synthesis result is not valid JSON, creating simple response")
                return {
                    "answer": synthesis_result if synthesis_result else raw_result,
                    "explanation": "Analysis completed successfully.",
                    "chart_type": "table",
                    "chart_data": raw_result,
                    "raw_data": raw_result,
                    "generated_code": generated_code,
                    "api_calls_made": self.api_call_count,
                    "total_tokens_used": self.total_tokens_used
                }
                
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "answer": "I encountered an error while analyzing your data. Please try again or rephrase your question.",
                "chart_type": "none",
                "api_calls_made": self.api_call_count,
                "total_tokens_used": self.total_tokens_used
            }

# Create global instance
ai_agent = AIAgent()
