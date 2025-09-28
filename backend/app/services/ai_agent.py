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
from app.services.chat_session_manager import chat_session_manager
from sqlalchemy import text
import pandas as pd

# Configure matplotlib to prevent popup windows
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Set up enhanced logging
import logging
from enhanced_logging import setup_enhanced_logging, log_query_start, log_query_end, log_api_call, log_code_execution

# Initialize enhanced logging
setup_enhanced_logging()
logger = logging.getLogger(__name__)

class AIAgent:
    """Core AI analysis engine for natural language data queries"""
    
    def __init__(self):
        # Multi-Gemini API system
        self.gemini_api_keys = []
        self.current_api_index = 0
        self.primary_model_name = 'gemini-2.5-pro'           # Gemini 2.5 Pro (most advanced)
        self.fallback_model_name = 'gemini-2.5-flash'        # Gemini 2.5 Flash (price-performance)
        self.tertiary_model_name = 'gemini-2.5-flash-lite'   # Gemini 2.5 Flash-Lite (cost-efficient)
        self.current_model_name = self.primary_model_name
        self.env_api_key = None  # Store environment API key separately
        
        # Initialize with default API key from environment if available
        default_key = getattr(settings, 'GEMINI_API_KEY', '')
        if default_key and default_key.strip():
            self.env_api_key = default_key.strip()
            self.gemini_api_keys.append(self.env_api_key)
            genai.configure(api_key=self.env_api_key)
            self.gemini_model = genai.GenerativeModel(self.current_model_name)
            logger.info(f"Initialized with environment API key using {self.current_model_name} (total keys: {len(self.gemini_api_keys)})")
        else:
            logger.warning("No GEMINI_API_KEY found in environment variables")
        
        # Retry and credit management settings
        self.max_retry_attempts = 3
        self.max_code_generation_attempts = 2
        self.max_synthesis_attempts = 2
        
        # Credit tracking per API key
        self.api_call_count = 0
        self.total_tokens_used = 0
        self.api_key_usage = {}  # Track usage per API key
        
        # Initialize credit tracking for environment API key
        if self.env_api_key:
            self.api_key_usage[self.env_api_key] = {
                'calls_made': 0,
                'tokens_used': 0,
                'last_used': None
            }
        
    def add_gemini_api_key(self, api_key: str) -> bool:
        """Add a new Gemini API key to the pool"""
        try:
            api_key = api_key.strip()
            
            # Don't add if it's the same as environment key
            if api_key == self.env_api_key:
                logger.warning("API key is the same as environment key, skipping")
                return False
            
            # Don't add duplicates
            if api_key in self.gemini_api_keys:
                logger.warning("API key already exists in pool")
                return False
            
            # Test the API key first
            genai.configure(api_key=api_key)
            test_model = genai.GenerativeModel(self.current_model_name)
            test_response = test_model.generate_content("test")
            
            # If successful, add to pool
            self.gemini_api_keys.append(api_key)
            self.api_key_usage[api_key] = {
                'calls_made': 0,
                'tokens_used': 0,
                'last_used': None
            }
            logger.info(f"Added new Gemini API key (total: {len(self.gemini_api_keys)})")
            return True
                
        except Exception as e:
            logger.error(f"Failed to add API key: {str(e)}")
            return False
    
    def ensure_env_api_key_available(self) -> bool:
        """Ensure environment API key is available as fallback"""
        if not self.env_api_key:
            logger.warning("No environment API key available")
            return False
        
        # If environment key is not in the pool, add it
        if self.env_api_key not in self.gemini_api_keys:
            self.gemini_api_keys.append(self.env_api_key)
            if self.env_api_key not in self.api_key_usage:
                self.api_key_usage[self.env_api_key] = {
                    'calls_made': 0,
                    'tokens_used': 0,
                    'last_used': None
                }
            logger.info("Environment API key added as fallback")
        
        return True
    
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
            
            # Log the prompt being sent (truncated for readability)
            prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
            logger.info(f"📤 Sending prompt to Gemini (length: {len(prompt)} chars): {prompt_preview}")
            
            # Configure Gemini with the specific API key
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(self.current_model_name)
            
            logger.info(f"🤖 Calling Gemini model: {self.current_model_name}")
            response = model.generate_content(prompt)
            result = response.text
            
            # Log the response received (truncated for readability)
            result_preview = result[:200] + "..." if len(result) > 200 else result
            logger.info(f"📥 Received response from Gemini (length: {len(result)} chars): {result_preview}")
            
            # Update usage tracking
            self.api_call_count += 1
            self.api_key_usage[api_key]['calls_made'] += 1
            self.api_key_usage[api_key]['last_used'] = time.time()
            
            # Log token usage if available
            if hasattr(response, 'usage_metadata'):
                tokens = response.usage_metadata.total_token_count
                self.total_tokens_used += tokens
                self.api_key_usage[api_key]['tokens_used'] += tokens
                logger.info(f"💰 Token usage: {tokens} tokens (total: {self.total_tokens_used})")
            
            # Extract code from markdown code blocks if present
            original_result = result
            if "```python" in result:
                start = result.find("```python") + 9
                end = result.find("```", start)
                if end != -1:
                    result = result[start:end].strip()
                    logger.info(f"[CODE] Extracted Python code from markdown block (length: {len(result)} chars)")
            elif "```" in result:
                start = result.find("```") + 3
                end = result.find("```", start)
                if end != -1:
                    result = result[start:end].strip()
                    logger.info(f"[CODE] Extracted code from markdown block (length: {len(result)} chars)")
            
            logger.info(f"[SUCCESS] Gemini API call successful")
            return result
            
        except Exception as e:
            error_msg = str(e)
            # Sanitize API key from error messages
            if api_key and api_key in error_msg:
                error_msg = error_msg.replace(api_key, "***API_KEY***")
            
            # Check if it's a rate limit or quota exceeded error
            if self._is_model_limit_error(error_msg):
                logger.warning(f"Model limit exceeded for {self.current_model_name}: {error_msg}")
                if self._switch_to_fallback_model():
                    logger.info(f"Switched to fallback model: {self.current_model_name}")
                    # Retry with fallback model
                    try:
                        model = genai.GenerativeModel(self.current_model_name)
                        logger.info(f"🤖 Retrying with fallback model: {self.current_model_name}")
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
                            logger.info(f"💰 Token usage: {tokens} tokens (total: {self.total_tokens_used})")
                        
                        # Extract code from markdown code blocks if present
                        original_result = result
                        if "```python" in result:
                            start = result.find("```python") + 9
                            end = result.find("```", start)
                            if end != -1:
                                result = result[start:end].strip()
                                logger.info(f"[CODE] Extracted Python code from markdown block (length: {len(result)} chars)")
                        elif "```" in result:
                            start = result.find("```") + 3
                            end = result.find("```", start)
                            if end != -1:
                                result = result[start:end].strip()
                                logger.info(f"[CODE] Extracted code from markdown block (length: {len(result)} chars)")
                        
                        logger.info(f"[SUCCESS] Gemini API call successful with fallback model")
                        return result
                    except Exception as retry_error:
                        logger.error(f"Fallback model also failed: {str(retry_error)}")
                        raise Exception(f"Both primary and fallback models failed. Last error: {str(retry_error)}")
                else:
                    logger.error(f"No fallback model available")
                    raise Exception(f"Model limit exceeded and no fallback available: {error_msg}")
            else:
                logger.error(f"Gemini API call failed: {error_msg}")
                raise Exception(f"Gemini API error: {error_msg}")
    
    def _call_llm_api(self, prompt: str) -> str:
        """Call LLM API with multi-Gemini fallback system"""
        # Ensure environment API key is available as fallback
        self.ensure_env_api_key_available()
        
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
                error_msg = str(e)
                # Sanitize API key from error messages
                if api_key and api_key in error_msg:
                    error_msg = error_msg.replace(api_key, "***API_KEY***")
                logger.warning(f"Gemini API key #{i + 1} failed: {error_msg}")
                continue
        
        # If all API keys failed
        final_error_msg = str(last_error) if last_error else "Unknown error"
        # Sanitize any remaining API keys in the final error
        for api_key in self.gemini_api_keys:
            if api_key and api_key in final_error_msg:
                final_error_msg = final_error_msg.replace(api_key, "***API_KEY***")
        raise Exception(f"All Gemini API keys failed. Last error: {final_error_msg}")
    
    def _is_model_limit_error(self, error_msg: str) -> bool:
        """Check if the error indicates model limits are exceeded"""
        limit_indicators = [
            'quota exceeded',
            'rate limit',
            'limit exceeded',
            'too many requests',
            'quota_exceeded',
            'rate_limit_exceeded',
            'model not available',
            'model unavailable',
            'resource_exhausted'
        ]
        error_lower = error_msg.lower()
        return any(indicator in error_lower for indicator in limit_indicators)
    
    def _switch_to_fallback_model(self) -> bool:
        """Switch to next available model in priority order"""
        if self.current_model_name == self.primary_model_name:
            # Switch from Pro to Flash
            self.current_model_name = self.fallback_model_name
            logger.info(f"[PROCESSING] Switched from {self.primary_model_name} to {self.fallback_model_name}")
            return True
        elif self.current_model_name == self.fallback_model_name:
            # Switch from Flash to Flash-Lite
            self.current_model_name = self.tertiary_model_name
            logger.info(f"[PROCESSING] Switched from {self.fallback_model_name} to {self.tertiary_model_name}")
            return True
        return False
    
    def reset_to_primary_model(self) -> None:
        """Reset to primary model (useful for testing or manual override)"""
        if self.current_model_name != self.primary_model_name:
            self.current_model_name = self.primary_model_name
            logger.info(f"[PROCESSING] Reset to primary model: {self.primary_model_name}")
    
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
1. Uses the provided 'engine' variable (SQLAlchemy engine) to connect to the database
2. Loads data using: df = pd.read_sql(f"SELECT * FROM {{table_name}}", engine)
3. Performs the analysis to answer the question
4. Prints only the final result

IMPORTANT: If you need to create charts or visualizations:
- Use matplotlib with non-interactive backend: matplotlib.use('Agg')
- DO NOT use plt.show() - this will cause popup windows
- Instead, save charts or just print the data for the frontend to render

Available variables:
- engine: SQLAlchemy engine (already connected to database)
- pd: pandas library
- text: SQLAlchemy text function
- plt: matplotlib.pyplot (configured for non-interactive use)
- matplotlib: matplotlib library
- session_id: current session ID

Table name: {list(schema_info.keys())[0] if schema_info else 'data_table'}

CRITICAL: Do NOT create new database connections. Use the provided 'engine' variable only.
Do NOT use psycopg2.connect() or any other connection methods.

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
                error_context = f"\n\nIMPORTANT: This is attempt #{attempt}. Previous attempts failed. Please ensure the code is syntactically correct and uses only the available variables (pd, engine, text, session_id). Do NOT create new database connections - use the provided 'engine' variable only."
                pandas_prompt = self.generate_pandas_prompt(query, schema_info) + error_context
            else:
                pandas_prompt = self.generate_pandas_prompt(query, schema_info)
            
            # Generate code using LLM
            logger.info(f"[PROCESSING] Generating code for query: '{query}' (attempt {attempt})")
            generated_code = self._call_llm_api(pandas_prompt)
            
            if not generated_code or generated_code.strip() == "":
                raise Exception("Empty code generated")
            
            logger.info(f"[NOTE] Generated code (length: {len(generated_code)} chars):")
            logger.info(f"```python\n{generated_code}\n```")
            
            # Test the code syntax before returning
            try:
                compile(generated_code, '<string>', 'exec')
                logger.info(f"[SUCCESS] Code syntax validation passed")
            except SyntaxError as e:
                logger.error(f"❌ Syntax error in generated code: {str(e)}")
                raise Exception(f"Syntax error in generated code: {str(e)}")
            
            logger.info(f"[SUCCESS] Code generation successful")
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
            logger.info(f"[START] Executing code (attempt {attempt}):")
            logger.info(f"```python\n{code}\n```")
            
            result = self.execute_code_safely(code, session_id)
            
            if result.startswith("Error executing code"):
                logger.error(f"❌ Code execution failed: {result}")
                raise Exception(result)
            
            logger.info(f"[SUCCESS] Code execution successful!")
            logger.info(f"[CHART] Execution result (length: {len(result)} chars):")
            logger.info(f"```\n{result}\n```")
            
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

Please fix the code to resolve the error. 

IMPORTANT RULES:
- Use ONLY the provided variables: pd, engine, text, session_id
- Do NOT create new database connections (no psycopg2.connect(), no new engines)
- Use the existing 'engine' variable for database queries
- Use pd.read_sql() with the provided engine

Return ONLY the corrected Python code, no explanations.

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
            logger.info(f"[PROCESSING] Synthesizing result for query: '{query}' (attempt {attempt})")
            logger.info(f"[CHART] Raw data length: {len(raw_data)} chars")
            
            synthesis_result = self._call_llm_api(synthesis_prompt)
            
            if not synthesis_result or synthesis_result.strip() == "":
                raise Exception("Empty synthesis result")
            
            logger.info(f"[SUCCESS] Result synthesis successful!")
            logger.info(f"[NOTE] Synthesis result (length: {len(synthesis_result)} chars):")
            logger.info(f"```\n{synthesis_result}\n```")
            
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
            'plt': plt,
            'matplotlib': matplotlib,
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
                # Exception classes
                'Exception': Exception,
                'BaseException': BaseException,
                'ImportError': ImportError,
                'ValueError': ValueError,
                'TypeError': TypeError,
                'KeyError': KeyError,
                'IndexError': IndexError,
                'AttributeError': AttributeError,
                'NameError': NameError,
                'RuntimeError': RuntimeError,
                'OSError': OSError,
                'FileNotFoundError': FileNotFoundError,
                'PermissionError': PermissionError,
                'ConnectionError': ConnectionError,
                'TimeoutError': TimeoutError,
                'MemoryError': MemoryError,
                'NotImplementedError': NotImplementedError,
                'StopIteration': StopIteration,
                'GeneratorExit': GeneratorExit,
                'SystemExit': SystemExit,
                'KeyboardInterrupt': KeyboardInterrupt,
            }
        }
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            # Ensure matplotlib is configured for non-interactive use
            matplotlib.use('Agg')
            plt.ioff()  # Turn off interactive mode
            
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
        logger.info(f"[DELETE] Resetting credit tracking for {len(self.api_key_usage)} API keys")
        self.api_call_count = 0
        self.total_tokens_used = 0
        for api_key in self.api_key_usage:
            self.api_key_usage[api_key] = {
                'calls_made': 0,
                'tokens_used': 0,
                'last_used': None
            }
        logger.info("[DELETE] Credit tracking reset successfully")
    
    def generate_synthesis_prompt(self, query: str, raw_data: str) -> str:
        """Generate prompt for result synthesis"""
        
        prompt = f"""You are a helpful data analyst assistant. Given the user's question and the analysis results, provide a friendly, natural language response.

User's question: "{query}"

Analysis results: {raw_data}

Please provide a conversational response that:
1. Directly answers the user's question in a friendly, natural way
2. Explains what the data shows in simple terms
3. ALWAYS generate charts when the data contains categorical, numerical, or comparative information that would benefit from visualization

IMPORTANT CHART GENERATION RULES:
- If the user asks for "graph", "chart", "visualization", or "spread" → ALWAYS generate a chart
- If the data contains categories (departments, cities, etc.) → Generate a chart
- If the data contains counts, frequencies, or distributions → Generate a chart
- If the data contains comparisons between groups → Generate a chart
- For department/category data → Use "bar" chart
- For percentage/proportion data → Use "pie" chart
- For trends over time → Use "line" chart
- For correlations → Use "scatter" chart

MULTI-STEP QUERY HANDLING:
- If the user asks multiple questions, address each one
- Generate separate charts for different aspects of the analysis
- Break down complex queries into clear, actionable responses

CRITICAL: You MUST use the exact format below. Do not deviate from this format.

Response format (choose one):
- If chart is needed: "Answer: [your answer] | Chart: [chart_type] | Data: [specific data description]"
- If no chart needed: "Answer: [your answer]"

Examples:
- "Answer: The dataset contains employee information. Engineering has 5 employees, Sales has 4, Marketing has 3, and HR has 3. | Chart: bar | Data: Department employee counts"
- "Answer: There are 15 employees total, with 5 in Engineering, 4 in Sales, 3 in Marketing, and 3 in HR. | Chart: pie | Data: Department distribution"

IMPORTANT: 
- ALWAYS include the "| Chart:" part when data can be visualized
- Use "bar" for department/category comparisons
- Use "pie" for proportions/percentages
- Use "line" for trends over time
- Use "scatter" for correlations

Response:"""
        
        return prompt
    
    def _handle_multi_step_query(self, query: str) -> List[str]:
        """Break down multi-step queries into individual components"""
        # Look for common multi-step patterns
        multi_step_indicators = [
            " and ", " also ", " then ", " next ", " furthermore ", " additionally ",
            "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.",
            "first", "second", "third", "fourth", "fifth"
        ]
        
        # Check if this looks like a multi-step query
        is_multi_step = any(indicator in query.lower() for indicator in multi_step_indicators)
        
        if is_multi_step:
            logger.info(f"[PROCESSING] Detected multi-step query: {query}")
            
            # Try to split by common separators
            if " and " in query.lower():
                parts = [part.strip() for part in query.split(" and ") if part.strip()]
            elif any(f"{i}." in query for i in range(1, 10)):
                # Split by numbered points
                import re
                parts = re.split(r'\d+\.', query)
                parts = [part.strip() for part in parts if part.strip()]
            else:
                # Keep as single query
                parts = [query]
            
            logger.info(f"[NOTE] Split into {len(parts)} parts: {parts}")
            return parts
        
        return [query]
    
    def _break_down_query_into_tasks(self, query: str, schema_info: Dict) -> List[Dict[str, str]]:
        """Use AI to break down complex queries into individual tasks"""
        try:
            logger.info(f"[PROCESSING] Breaking down query into tasks: {query}")
            
            # Create a prompt for task breakdown
            breakdown_prompt = f"""You are a data analysis task planner. Given a user's complex query and the available data schema, break it down into individual, actionable tasks.

User's Query: "{query}"

Available Data Schema: {json.dumps(schema_info, indent=2)}

Break down this query into individual tasks. Each task should be:
1. Specific and actionable
2. Focused on one aspect of the analysis
3. Include the type of visualization needed (if any)

Return ONLY a JSON array of tasks in this exact format:
[
  {{
    "task_id": "task_1",
    "description": "Brief description of what this task does",
    "query": "Specific question for this task",
    "chart_type": "bar|pie|line|scatter|none",
    "priority": 1
  }},
  {{
    "task_id": "task_2", 
    "description": "Brief description of what this task does",
    "query": "Specific question for this task",
    "chart_type": "bar|pie|line|scatter|none",
    "priority": 2
  }}
]

Examples:
- For "piechart of department population spread" → chart_type: "pie"
- For "highest salary" → chart_type: "none" 
- For "which department has most people from seattle" → chart_type: "bar"

Return ONLY the JSON array, no other text:"""
            
            # Call Gemini to break down the query
            response = self._call_gemini_api(breakdown_prompt)
            
            if response:
                try:
                    # Parse the JSON response
                    tasks = json.loads(response)
                    logger.info(f"[SUCCESS] Successfully broke down query into {len(tasks)} tasks")
                    for i, task in enumerate(tasks):
                        logger.info(f"[TASK] Task {i+1}: {task.get('description', 'No description')} (Chart: {task.get('chart_type', 'none')})")
                    return tasks
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse task breakdown JSON: {e}")
                    logger.error(f"[NOTE] Raw response: {response}")
                    return self._fallback_task_breakdown(query)
            else:
                logger.warning("⚠️ No response from AI for task breakdown, using fallback")
                return self._fallback_task_breakdown(query)
                
        except Exception as e:
            logger.error(f"❌ Error breaking down query: {e}")
            return self._fallback_task_breakdown(query)
    
    def _fallback_task_breakdown(self, query: str) -> List[Dict[str, str]]:
        """Fallback task breakdown when AI fails"""
        logger.info("[PROCESSING] Using fallback task breakdown")
        
        # Simple keyword-based breakdown
        tasks = []
        task_counter = 1
        
        # Check for common patterns
        if "description" in query.lower() or "what" in query.lower():
            tasks.append({
                "task_id": f"task_{task_counter}",
                "description": "General dataset description",
                "query": "Provide a general description of the dataset",
                "chart_type": "none",
                "priority": task_counter
            })
            task_counter += 1
        
        if "pie" in query.lower() or "piechart" in query.lower():
            tasks.append({
                "task_id": f"task_{task_counter}",
                "description": "Department population pie chart",
                "query": "Create a pie chart showing department population spread",
                "chart_type": "pie",
                "priority": task_counter
            })
            task_counter += 1
        
        if "highest salary" in query.lower() or "maximum salary" in query.lower():
            tasks.append({
                "task_id": f"task_{task_counter}",
                "description": "Find highest salary",
                "query": "What is the highest salary in the dataset?",
                "chart_type": "none",
                "priority": task_counter
            })
            task_counter += 1
        
        if "seattle" in query.lower() or "department" in query.lower():
            tasks.append({
                "task_id": f"task_{task_counter}",
                "description": "Department analysis for Seattle employees",
                "query": "Which department has the most employees from Seattle?",
                "chart_type": "bar",
                "priority": task_counter
            })
            task_counter += 1
        
        # If no specific patterns found, treat as single task
        if not tasks:
            tasks.append({
                "task_id": "task_1",
                "description": "General analysis",
                "query": query,
                "chart_type": "none",
                "priority": 1
            })
        
        logger.info(f"[TASK] Fallback breakdown created {len(tasks)} tasks")
        return tasks
    
    def _process_single_task(self, task: Dict[str, str], session_id: str, schema_info: Dict) -> Dict[str, Any]:
        """Process a single task and return the result"""
        try:
            logger.info(f"[PROCESSING] Processing task: {task['description']}")
            
            # Generate code for this specific task
            generated_code = self._generate_code_with_retry(task['query'], schema_info)
            
            if not generated_code:
                logger.error(f"❌ Failed to generate code for task: {task['description']}")
                return {
                    "task_id": task['task_id'],
                    "description": task['description'],
                    "answer": f"I couldn't analyze: {task['query']}",
                    "chart_type": "none",
                    "chart_data": None,
                    "error": "Code generation failed"
                }
            
            # Execute the code
            raw_result = self._execute_code_with_retry(generated_code, session_id)
            
            if raw_result.startswith("Error executing code"):
                logger.error(f"❌ Code execution failed for task: {task['description']}")
                return {
                    "task_id": task['task_id'],
                    "description": task['description'],
                    "answer": f"I encountered an error while analyzing: {task['query']}",
                    "chart_type": "none",
                    "chart_data": None,
                    "error": raw_result
                }
            
            # Synthesize the result
            synthesis_result = self._synthesize_result_with_retry(task['query'], raw_result)
            
            # Parse the synthesis result
            parsed_result = self._parse_synthesis_result(synthesis_result, raw_result, generated_code)
            
            # Add task metadata
            parsed_result['task_id'] = task['task_id']
            parsed_result['description'] = task['description']
            parsed_result['priority'] = task['priority']
            
            logger.info(f"[SUCCESS] Completed task: {task['description']}")
            return parsed_result
            
        except Exception as e:
            logger.error(f"❌ Error processing task {task['task_id']}: {e}")
            return {
                "task_id": task['task_id'],
                "description": task['description'],
                "answer": f"I encountered an error while processing: {task['query']}",
                "chart_type": "none",
                "chart_data": None,
                "error": str(e)
            }
    
    def get_answer_with_task_breakdown(self, query: str, session_id: str) -> Dict[str, Any]:
        """Main function that breaks down complex queries into tasks and processes them sequentially"""
        import time
        start_time = time.time()
        
        try:
            log_query_start(query, session_id)
            logger.info(f"🔑 Available API keys: {len(self.gemini_api_keys)}")
            
            # Step 1: Get schema information
            logger.info(f"[CHART] Retrieving schema for session: {session_id}")
            schema_info = data_processor.get_table_schema(session_id)
            
            if not schema_info:
                logger.warning(f"❌ No schema found for session: {session_id}")
                log_query_end(query, False, time.time() - start_time)
                return {
                    "error": "No data found for this session",
                    "answer": "I couldn't find any data associated with this session. Please upload a file first.",
                    "chart_type": "none",
                    "tasks": []
                }
            
            logger.info(f"[SUCCESS] Schema retrieved for session {session_id}: {len(schema_info)} tables")
            
            # Step 2: Break down the query into tasks
            logger.info(f"[PROCESSING] Breaking down query into tasks...")
            tasks = self._break_down_query_into_tasks(query, schema_info)
            
            if not tasks:
                logger.warning("⚠️ No tasks generated, falling back to single query processing")
                return self.get_answer(query, session_id)
            
            logger.info(f"[TASK] Generated {len(tasks)} tasks to process")
            
            # Step 3: Process tasks sequentially
            results = []
            for i, task in enumerate(tasks):
                logger.info(f"[PROCESSING] Processing task {i+1}/{len(tasks)}: {task['description']}")
                result = self._process_single_task(task, session_id, schema_info)
                results.append(result)
            
            # Step 4: Combine results
            logger.info(f"[PROCESSING] Combining {len(results)} task results...")
            
            # Create a comprehensive response
            combined_answer = f"I've analyzed your request and completed {len(results)} tasks:\n\n"
            
            for i, result in enumerate(results):
                combined_answer += f"**{i+1}. {result['description']}**\n"
                combined_answer += f"{result['answer']}\n\n"
            
            # Check if any tasks generated charts
            charts_generated = [r for r in results if r.get('chart_type') != 'none' and r.get('chart_data')]
            
            if charts_generated:
                # Use the first chart (or prioritize pie charts)
                pie_charts = [r for r in charts_generated if r.get('chart_type') == 'pie']
                if pie_charts:
                    selected_chart = pie_charts[0]
                else:
                    selected_chart = charts_generated[0]
                
                logger.info(f"[CHART] Using chart from task: {selected_chart['description']}")
                
                final_result = {
                    "answer": combined_answer,
                    "chart_type": selected_chart['chart_type'],
                    "chart_data": selected_chart['chart_data'],
                    "raw_data": f"Processed {len(results)} tasks",
                    "generated_code": f"Multiple code blocks for {len(results)} tasks",
                    "api_calls_made": self.api_call_count,
                    "total_tokens_used": self.total_tokens_used,
                    "tasks": results
                }
            else:
                final_result = {
                    "answer": combined_answer,
                    "chart_type": "none",
                    "chart_data": None,
                    "raw_data": f"Processed {len(results)} tasks",
                    "generated_code": f"Multiple code blocks for {len(results)} tasks",
                    "api_calls_made": self.api_call_count,
                    "total_tokens_used": self.total_tokens_used,
                    "tasks": results
                }
            
            logger.info(f"[SUCCESS] Successfully processed {len(results)} tasks")
            log_query_end(query, True, time.time() - start_time)
            return final_result
                
        except Exception as e:
            logger.error(f"💥 Error processing query with task breakdown '{query}': {str(e)}")
            log_query_end(query, False, time.time() - start_time)
            return {
                "error": "Task breakdown failed",
                "answer": f"I encountered an error while processing your request: {str(e)}",
                "chart_type": "none",
                "tasks": []
            }
    
    def get_answer_with_chat_context(self, query: str, chat_id: str) -> Dict[str, Any]:
        """Process query with chat session context isolation"""
        import time
        start_time = time.time()
        
        try:
            # Get chat session
            chat_session = chat_session_manager.get_chat_session(chat_id)
            if not chat_session:
                log_query_end(query, False, time.time() - start_time)
                return {
                    "error": "Invalid chat session",
                    "answer": "This chat session is no longer valid. Please start a new chat.",
                    "chart_type": "none"
                }
            
            database_session_id = chat_session.database_session_id
            logger.info(f"[CHAT] Processing query in chat {chat_id} with database {database_session_id}")
            
            # Get chat context
            context = chat_session_manager.get_chat_context(chat_id)
            if not context:
                context = {}
            
            # Check if we have cached schema info
            schema_info = context.get("schema_info")
            if not schema_info:
                logger.info(f"[CHART] Retrieving fresh schema for chat {chat_id}")
                schema_info = data_processor.get_table_schema(database_session_id)
                if schema_info:
                    chat_session_manager.update_chat_context(chat_id, {"schema_info": schema_info})
                else:
                    logger.warning(f"❌ No schema found for chat {chat_id}")
                    log_query_end(query, False, time.time() - start_time)
                    return {
                        "error": "No data found for this chat session",
                        "answer": "I couldn't find any data associated with this chat session. Please upload a file first.",
                        "chart_type": "none"
                    }
            else:
                logger.info(f"[CHART] Using cached schema for chat {chat_id}")
            
            # Add conversation context to the query
            conversation_history = context.get("conversation_history", [])
            contextual_query = self._build_contextual_query(query, conversation_history, schema_info)
            
            # Process the query with task breakdown
            result = self.get_answer_with_task_breakdown(contextual_query, database_session_id)
            
            # Update chat context with the result
            chat_session_manager.update_chat_context(chat_id, {
                "last_query": query,
                "last_result": result,
                "data_summary": self._extract_data_summary(result)
            })
            
            # Add message to conversation history
            chat_session_manager.add_message_to_history(chat_id, {
                "type": "user",
                "content": query,
                "timestamp": time.time()
            })
            
            chat_session_manager.add_message_to_history(chat_id, {
                "type": "assistant", 
                "content": result.get("answer", ""),
                "chart_type": result.get("chart_type", "none"),
                "chart_data": result.get("chart_data"),
                "timestamp": time.time()
            })
            
            # Add chat metadata to result
            result["chat_id"] = chat_id
            result["database_session_id"] = database_session_id
            result["message_count"] = chat_session.message_count
            
            logger.info(f"[SUCCESS] Successfully processed query for chat {chat_id}")
            log_query_end(query, True, time.time() - start_time)
            return result
                
        except Exception as e:
            logger.error(f"💥 Error processing query with chat context '{query}': {str(e)}")
            log_query_end(query, False, time.time() - start_time)
            return {
                "error": "Chat context processing failed",
                "answer": f"I encountered an error while processing your request: {str(e)}",
                "chart_type": "none",
                "chat_id": chat_id
            }
    
    def _build_contextual_query(self, query: str, conversation_history: List[Dict], schema_info: Dict) -> str:
        """Build a contextual query using conversation history"""
        if not conversation_history:
            return query
        
        # Get recent conversation context (last 3 messages)
        recent_messages = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
        
        context_parts = []
        for msg in recent_messages:
            if msg.get("type") == "user":
                context_parts.append(f"Previous user question: {msg.get('content', '')}")
            elif msg.get("type") == "assistant":
                context_parts.append(f"Previous answer: {msg.get('content', '')[:100]}...")
        
        if context_parts:
            context_str = "\n".join(context_parts)
            contextual_query = f"""Based on our previous conversation:
{context_str}

Current question: {query}

Please provide a response that builds on our previous discussion while answering the current question."""
            return contextual_query
        
        return query
    
    def _extract_data_summary(self, result: Dict[str, Any]) -> str:
        """Extract a summary of the data analysis for context"""
        if not result or result.get("error"):
            return "No data analysis available"
        
        answer = result.get("answer", "")
        chart_type = result.get("chart_type", "none")
        
        summary_parts = []
        if answer:
            summary_parts.append(f"Analysis: {answer[:100]}...")
        if chart_type != "none":
            summary_parts.append(f"Visualization: {chart_type} chart")
        
        return " | ".join(summary_parts) if summary_parts else "Basic analysis completed"
    
    def _parse_synthesis_result(self, synthesis_result: str, raw_data: str, generated_code: str) -> Dict[str, Any]:
        """Parse the synthesis result and generate charts when appropriate"""
        try:
            logger.info(f"[PROCESSING] Parsing synthesis result: {synthesis_result[:200]}...")
            
            # Default response
            result = {
                "answer": synthesis_result if synthesis_result else raw_data,
                "chart_type": "none",
                "chart_data": None,
                "raw_data": raw_data,
                "generated_code": generated_code,
                "api_calls_made": self.api_call_count,
                "total_tokens_used": self.total_tokens_used
            }
            
            # Check if the result contains chart information
            if "| Chart:" in synthesis_result:
                logger.info("[CHART] Found chart format in synthesis result")
                parts = synthesis_result.split("|")
                answer_part = parts[0].replace("Answer:", "").strip()
                chart_part = parts[1].replace("Chart:", "").strip() if len(parts) > 1 else ""
                data_part = parts[2].replace("Data:", "").strip() if len(parts) > 2 else ""
                
                logger.info(f"[NOTE] Answer part: {answer_part[:100]}...")
                logger.info(f"[CHART] Chart part: {chart_part}")
                logger.info(f"📈 Data part: {data_part}")
                
                result["answer"] = answer_part
                result["chart_type"] = chart_part.lower()
                result["chart_data"] = data_part
                
                # Generate actual chart data if chart is suggested
                if result["chart_type"] != "none" and result["chart_type"] in ["bar", "pie", "line", "scatter"]:
                    logger.info(f"[PROCESSING] Generating chart data for type: {result['chart_type']}")
                    chart_data = self._generate_chart_data(raw_data, result["chart_type"], data_part)
                    if chart_data:
                        result["chart_data"] = chart_data
                        logger.info(f"[CHART] Generated {result['chart_type']} chart data successfully")
                    else:
                        result["chart_type"] = "none"
                        logger.warning("⚠️ Could not generate chart data, setting chart_type to 'none'")
                else:
                    logger.warning(f"⚠️ Invalid chart type: {result['chart_type']}")
            
            elif synthesis_result.startswith("Answer:"):
                logger.info("[NOTE] Found simple answer format (no chart)")
                # Simple answer format
                result["answer"] = synthesis_result.replace("Answer:", "").strip()
            else:
                logger.warning("⚠️ No recognized format found in synthesis result")
            
            logger.info(f"[SUCCESS] Final result - Chart type: {result['chart_type']}, Chart data: {result['chart_data'] is not None}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing synthesis result: {e}")
            return {
                "answer": synthesis_result if synthesis_result else raw_data,
                "chart_type": "none",
                "chart_data": None,
                "raw_data": raw_data,
                "generated_code": generated_code,
                "api_calls_made": self.api_call_count,
                "total_tokens_used": self.total_tokens_used
            }
    
    def _generate_chart_data(self, raw_data: str, chart_type: str, data_description: str) -> Dict[str, Any]:
        """Generate actual chart data from raw analysis results"""
        try:
            logger.info(f"[PROCESSING] Generating {chart_type} chart data from: {raw_data[:200]}...")
            logger.info(f"[NOTE] Data description: {data_description}")
            
            # This is a simplified chart data generator
            # In a real implementation, you'd parse the raw_data more intelligently
            
            if chart_type == "bar":
                # Try to extract numerical data for bar charts
                import re
                
                # Look for patterns like "Department: 5, Sales: 4, Marketing: 3"
                department_pattern = r'(\w+):\s*(\d+)'
                matches = re.findall(department_pattern, raw_data)
                
                if matches:
                    logger.info(f"[CHART] Found department pattern matches: {matches}")
                    return {
                        "type": "bar",
                        "data": {
                            "labels": [match[0] for match in matches],
                            "datasets": [{
                                "label": "Count",
                                "data": [int(match[1]) for match in matches],
                                "backgroundColor": ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"]
                            }]
                        }
                    }
                
                # Look for patterns like "Engineering has employees in 2 unique cities"
                city_pattern = r'(\w+)\s+has\s+employees\s+in\s+(\d+)\s+unique\s+cities?'
                city_matches = re.findall(city_pattern, raw_data)
                
                if city_matches:
                    logger.info(f"[CHART] Found city pattern matches: {city_matches}")
                    return {
                        "type": "bar",
                        "data": {
                            "labels": [match[0] for match in city_matches],
                            "datasets": [{
                                "label": "Unique Cities",
                                "data": [int(match[1]) for match in city_matches],
                                "backgroundColor": ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"]
                            }]
                        }
                    }
                
                # Look for department patterns like "Engineering has 5 employees"
                dept_pattern = r'(\w+)\s+has\s+(\d+)\s+employees?'
                dept_matches = re.findall(dept_pattern, raw_data)
                
                if dept_matches:
                    logger.info(f"[CHART] Found department pattern matches: {dept_matches}")
                    return {
                        "type": "bar",
                        "data": {
                            "labels": [match[0] for match in dept_matches],
                            "datasets": [{
                                "label": "Employee Count",
                                "data": [int(match[1]) for match in dept_matches],
                                "backgroundColor": ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"]
                            }]
                        }
                    }
                
                # Look for patterns like "Engineering department has the most employees from Seattle"
                seattle_pattern = r'(\w+)\s+department\s+has\s+the\s+most\s+employees?\s+from\s+Seattle'
                seattle_matches = re.findall(seattle_pattern, raw_data)
                
                if seattle_matches:
                    logger.info(f"[CHART] Found Seattle pattern matches: {seattle_matches}")
                    return {
                        "type": "bar",
                        "data": {
                            "labels": [match[0] for match in seattle_matches],
                            "datasets": [{
                                "label": "Seattle Employees",
                                "data": [1],  # Just showing which department
                                "backgroundColor": ["#3b82f6"]
                            }]
                        }
                    }
                
                # Look for salary patterns
                salary_pattern = r'(\$[\d,]+)'
                salaries = re.findall(salary_pattern, raw_data)
                if salaries:
                    # Convert to numbers and create ranges
                    salary_values = [int(s.replace('$', '').replace(',', '')) for s in salaries]
                    ranges = ["$50k-60k", "$60k-70k", "$70k-80k", "$80k-90k", "$90k+"]
                    counts = [0] * len(ranges)
                    
                    for salary in salary_values:
                        if salary < 60000:
                            counts[0] += 1
                        elif salary < 70000:
                            counts[1] += 1
                        elif salary < 80000:
                            counts[2] += 1
                        elif salary < 90000:
                            counts[3] += 1
                        else:
                            counts[4] += 1
                    
                    return {
                        "type": "bar",
                        "data": {
                            "labels": ranges,
                            "datasets": [{
                                "label": "Number of Employees",
                                "data": counts,
                                "backgroundColor": ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"]
                            }]
                        }
                    }
            
            elif chart_type == "pie":
                # Similar logic for pie charts
                department_pattern = r'(\w+):\s*(\d+)'
                matches = re.findall(department_pattern, raw_data)
                
                if matches:
                    logger.info(f"[CHART] Found pie chart department pattern matches: {matches}")
                    return {
                        "type": "pie",
                        "data": {
                            "labels": [match[0] for match in matches],
                            "datasets": [{
                                "data": [int(match[1]) for match in matches],
                                "backgroundColor": ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"]
                            }]
                        }
                    }
                
                # Look for department patterns like "Engineering has 5 employees" for pie charts
                dept_pattern = r'(\w+)\s+has\s+(\d+)\s+employees?'
                dept_matches = re.findall(dept_pattern, raw_data)
                
                if dept_matches:
                    logger.info(f"[CHART] Found pie chart department pattern matches: {dept_matches}")
                    return {
                        "type": "pie",
                        "data": {
                            "labels": [match[0] for match in dept_matches],
                            "datasets": [{
                                "data": [int(match[1]) for match in dept_matches],
                                "backgroundColor": ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"]
                            }]
                        }
                    }
            
            # Try more generic patterns if specific ones don't match
            logger.info("[PROCESSING] Trying generic pattern matching...")
            
            # Look for any word-number patterns
            generic_pattern = r'(\w+)\s*[:\-]?\s*(\d+)'
            generic_matches = re.findall(generic_pattern, raw_data)
            
            if generic_matches and len(generic_matches) >= 2:
                logger.info(f"[CHART] Found generic pattern matches: {generic_matches}")
                return {
                    "type": chart_type,
                    "data": {
                        "labels": [match[0] for match in generic_matches],
                        "datasets": [{
                            "label": "Count" if chart_type == "bar" else "Value",
                            "data": [int(match[1]) for match in generic_matches],
                            "backgroundColor": ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"]
                        }]
                    }
                }
            
            # If no patterns match, return None
            logger.warning("⚠️ No chart data patterns found in raw data")
            return None
            
        except Exception as e:
            logger.error(f"Error generating chart data: {e}")
            return None
    
    def get_answer(self, query: str, session_id: str) -> Dict[str, Any]:
        """Main function to process user query and return AI analysis with comprehensive error handling"""
        import time
        start_time = time.time()
        
        try:
            log_query_start(query, session_id)
            logger.info(f"🔑 Available API keys: {len(self.gemini_api_keys)}")
            
            # Step 1: Get schema information
            logger.info(f"[CHART] Retrieving schema for session: {session_id}")
            schema_info = data_processor.get_table_schema(session_id)
            
            if not schema_info:
                logger.warning(f"❌ No schema found for session: {session_id}")
                log_query_end(query, False, time.time() - start_time)
                return {
                    "error": "No data found for this session",
                    "answer": "I couldn't find any data associated with this session. Please upload a file first.",
                    "chart_type": "none"
                }
            
            logger.info(f"[SUCCESS] Schema retrieved for session {session_id}: {len(schema_info)} tables")
            for table_name, table_info in schema_info.items():
                logger.info(f"[TASK] Table: {table_name} with {len(table_info['columns'])} columns")
            
            # Step 1.5: Handle multi-step queries
            query_parts = self._handle_multi_step_query(query)
            if len(query_parts) > 1:
                logger.info(f"[PROCESSING] Processing {len(query_parts)} query parts")
                # For now, process the first part that asks for visualization
                visualization_query = None
                for part in query_parts:
                    if any(word in part.lower() for word in ["graph", "chart", "visualization", "spread"]):
                        visualization_query = part
                        break
                
                if visualization_query:
                    query = visualization_query
                    logger.info(f"[CHART] Using visualization-focused query: {query}")
            
            # Step 2: Generate pandas code with retry logic
            logger.info(f"[PROCESSING] Starting code generation phase...")
            generated_code = self._generate_code_with_retry(query, schema_info)
            
            if not generated_code:
                logger.error("❌ Failed to generate analysis code")
                log_query_end(query, False, time.time() - start_time)
                return {
                    "error": "Failed to generate analysis code",
                    "answer": "I'm having trouble analyzing your data right now. Please try again.",
                    "chart_type": "none"
                }
            
            logger.info("[SUCCESS] Code generation phase completed")
            
            # Step 3: Execute the code safely with retry logic
            logger.info(f"[START] Starting code execution phase...")
            raw_result = self._execute_code_with_retry(generated_code, session_id)
            
            if raw_result.startswith("Error executing code"):
                logger.error(f"❌ Code execution phase failed: {raw_result}")
                log_query_end(query, False, time.time() - start_time)
                return {
                    "error": "Code execution failed",
                    "answer": f"I generated analysis code but encountered an error: {raw_result}",
                    "chart_type": "none"
                }
            
            logger.info("[SUCCESS] Code execution phase completed")
            
            # Step 4: Synthesize the result with retry logic
            logger.info(f"[PROCESSING] Starting result synthesis phase...")
            synthesis_result = self._synthesize_result_with_retry(query, raw_result)
            
            logger.info("[SUCCESS] Result synthesis phase completed")
            
            # Step 5: Parse the synthesis result
            logger.info(f"[PROCESSING] Parsing synthesis result...")
            
            # Parse the new format: "Answer: ... | Chart: ... | Data: ..." or just "Answer: ..."
            parsed_result = self._parse_synthesis_result(synthesis_result, raw_result, generated_code)
            
            logger.info(f"[SUCCESS] Successfully parsed synthesis response")
            logger.info(f"[NOTE] Final answer: {parsed_result.get('answer', '')[:100]}...")
            logger.info(f"[CHART] Chart type: {parsed_result.get('chart_type', 'none')}")
            
            log_query_end(query, True, time.time() - start_time)
            return parsed_result
                
        except Exception as e:
            logger.error(f"💥 Error processing query '{query}': {str(e)}")
            logger.error(f"🔍 Error type: {type(e).__name__}")
            logger.error(f"[CHART] Current API calls: {self.api_call_count}, Tokens: {self.total_tokens_used}")
            
            log_query_end(query, False, time.time() - start_time)
            return {
                "error": f"Analysis failed: {str(e)}",
                "answer": "I encountered an error while analyzing your data. Please try again or rephrase your question.",
                "chart_type": "none",
                "api_calls_made": self.api_call_count,
                "total_tokens_used": self.total_tokens_used
            }

# Create global instance
ai_agent = AIAgent()
