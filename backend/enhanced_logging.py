#!/usr/bin/env python3
"""
Enhanced logging configuration for AI Data Agent
"""
import logging
import sys
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to the level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        return super().format(record)

def setup_enhanced_logging():
    """Set up enhanced logging configuration"""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Set encoding to UTF-8 to handle Unicode characters
    if hasattr(console_handler.stream, 'reconfigure'):
        console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
    
    # Create formatter
    formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler for detailed logs with UTF-8 encoding
    file_handler = logging.FileHandler('ai_agent_detailed.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

def log_query_start(query: str, session_id: str):
    """Log the start of a query processing"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info(f"[START] STARTING QUERY PROCESSING")
    logger.info(f"[NOTE] Query: {query}")
    logger.info(f"[ID] Session ID: {session_id}")
    logger.info(f"[TIME] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

def log_query_end(query: str, success: bool, duration: float = None):
    """Log the end of a query processing"""
    logger = logging.getLogger(__name__)
    status = "[SUCCESS] SUCCESS" if success else "[ERROR] FAILED"
    duration_str = f" (Duration: {duration:.2f}s)" if duration else ""
    
    logger.info("=" * 80)
    logger.info(f"[COMPLETE] QUERY PROCESSING COMPLETED")
    logger.info(f"[NOTE] Query: {query}")
    logger.info(f"[STATUS] Status: {status}{duration_str}")
    logger.info(f"[TIME] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

def log_api_call(api_key_index: int, prompt_length: int, response_length: int, tokens: int = None):
    """Log API call details"""
    logger = logging.getLogger(__name__)
    token_str = f", Tokens: {tokens}" if tokens else ""
    logger.info(f"[NETWORK] API Call #{api_key_index} | Prompt: {prompt_length} chars | Response: {response_length} chars{token_str}")

def log_code_execution(code: str, result: str, success: bool):
    """Log code execution details"""
    logger = logging.getLogger(__name__)
    status = "[SUCCESS] SUCCESS" if success else "[ERROR] FAILED"
    logger.info(f"[TOOL] Code Execution {status}")
    logger.info(f"[NOTE] Code Length: {len(code)} chars")
    logger.info(f"[ANALYSIS] Result Length: {len(result)} chars")

if __name__ == "__main__":
    # Test the logging setup
    setup_enhanced_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("[TEST] Testing enhanced logging...")
    logger.warning("[WARNING] This is a warning message")
    logger.error("[ERROR] This is an error message")
    
    log_query_start("Test query", "test-session-123")
    log_api_call(1, 500, 200, 150)
    log_code_execution("print('hello')", "hello", True)
    log_query_end("Test query", True, 1.5)
