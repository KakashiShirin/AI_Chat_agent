import requests
import json
import io
import sys
import google.generativeai as genai
import logging
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
        self.hf_api_key = settings.HUGGINGFACE_API_KEY
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        self.model_name = "bigcode/starcoder"  # Primary model for code generation
        self.fallback_model = "microsoft/CodeBERT-base"  # Fallback model
        
        # Initialize Gemini
        self.gemini_api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Retry and credit management settings
        self.max_retry_attempts = 3
        self.max_code_generation_attempts = 2
        self.max_synthesis_attempts = 2
        
        # Credit tracking
        self.api_call_count = 0
        self.total_tokens_used = 0
        
    def _call_huggingface_api(self, prompt: str, max_retries: int = 3) -> str:
        """Call Hugging Face Inference API with retry logic"""
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.1,
                "return_full_text": False
            }
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.hf_api_url}/{self.model_name}",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "")
                    return str(result)
                elif response.status_code == 503 and attempt < max_retries - 1:
                    # Model is loading, wait and retry
                    import time
                    time.sleep(5)
                    continue
                else:
                    # Try fallback model
                    if attempt == max_retries - 1:
                        return self._call_fallback_model(prompt)
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Hugging Face API error: {str(e)}")
                continue
                
        return ""
    
    def _call_fallback_model(self, prompt: str) -> str:
        """Call fallback model if primary model fails"""
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.1,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                f"{self.hf_api_url}/{self.fallback_model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                return str(result)
            else:
                raise Exception(f"Fallback model failed: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Both models failed: {str(e)}")
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Call Google Gemini API as fallback with comprehensive logging"""
        try:
            if not self.gemini_api_key:
                raise Exception("Gemini API key not configured")
            
            logger.info(f"Calling Gemini API (Call #{self.api_call_count + 1})")
            self.api_call_count += 1
            
            response = self.gemini_model.generate_content(prompt)
            result = response.text
            
            # Log token usage if available
            if hasattr(response, 'usage_metadata'):
                tokens = response.usage_metadata.total_token_count
                self.total_tokens_used += tokens
                logger.info(f"Gemini API call #{self.api_call_count}: {tokens} tokens used")
            
            # Extract code from markdown code blocks if present
            if "```python" in result:
                # Extract code between ```python and ```
                start = result.find("```python") + 9
                end = result.find("```", start)
                if end != -1:
                    result = result[start:end].strip()
            elif "```" in result:
                # Extract code between ``` and ```
                start = result.find("```") + 3
                end = result.find("```", start)
                if end != -1:
                    result = result[start:end].strip()
            
            logger.info(f"Gemini API call #{self.api_call_count} successful")
            return result
            
        except Exception as e:
            logger.error(f"Gemini API call #{self.api_call_count} failed: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _call_llm_api(self, prompt: str) -> str:
        """Call LLM API with fallback chain: HuggingFace -> Gemini"""
        try:
            # Try Hugging Face first
            return self._call_huggingface_api(prompt)
        except Exception as hf_error:
            print(f"Hugging Face failed: {hf_error}")
            try:
                # Fallback to Gemini
                return self._call_gemini_api(prompt)
            except Exception as gemini_error:
                raise Exception(f"All LLM APIs failed. HF: {hf_error}, Gemini: {gemini_error}")
    
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
        """Get current credit usage statistics"""
        return {
            "api_calls_made": self.api_call_count,
            "total_tokens_used": self.total_tokens_used,
            "estimated_cost_usd": self.total_tokens_used * 0.000001,  # Rough estimate
            "max_retry_attempts": self.max_retry_attempts,
            "max_code_generation_attempts": self.max_code_generation_attempts,
            "max_synthesis_attempts": self.max_synthesis_attempts
        }
    
    def reset_credit_tracking(self):
        """Reset credit tracking counters"""
        self.api_call_count = 0
        self.total_tokens_used = 0
        logger.info("Credit tracking reset")
    
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
