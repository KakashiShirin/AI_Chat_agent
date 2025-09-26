"""
Database service for PostgreSQL operations
"""

import asyncio
import asyncpg
import logging
from typing import List, Dict, Any, Optional
import json
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DB_CONFIG

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.pool = None
        self.schema_cache = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            # Convert sync config to async
            async_config = {
                'host': DB_CONFIG['host'],
                'port': DB_CONFIG['port'],
                'database': DB_CONFIG['database'],
                'user': DB_CONFIG['user'],
                'password': DB_CONFIG['password']
            }
            
            self.pool = await asyncpg.create_pool(
                **async_config,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            
            logger.info("Database connection pool initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results"""
        try:
            async with self.pool.acquire() as conn:
                if params:
                    rows = await conn.fetch(query, *params)
                else:
                    rows = await conn.fetch(query)
                
                # Convert rows to list of dictionaries
                results = []
                for row in rows:
                    results.append(dict(row))
                
                return results
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get comprehensive database schema information"""
        if self.schema_cache:
            return self.schema_cache
        
        try:
            # Get tables and their columns
            tables_query = """
                SELECT 
                    t.table_name,
                    t.table_type,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    c.column_default,
                    c.character_maximum_length,
                    c.numeric_precision,
                    c.numeric_scale
                FROM information_schema.tables t
                LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
                WHERE t.table_schema = 'public'
                AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name, c.ordinal_position;
            """
            
            tables_data = await self.execute_query(tables_query)
            
            # Get foreign key relationships
            fk_query = """
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    tc.constraint_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public';
            """
            
            fk_data = await self.execute_query(fk_query)
            
            # Get primary keys
            pk_query = """
                SELECT
                    tc.table_name,
                    kcu.column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_schema = 'public';
            """
            
            pk_data = await self.execute_query(pk_query)
            
            # Organize schema information
            schema = {}
            
            # Process tables
            for row in tables_data:
                table_name = row['table_name']
                if table_name not in schema:
                    schema[table_name] = {
                        'columns': {},
                        'primary_keys': [],
                        'foreign_keys': []
                    }
                
                if row['column_name']:
                    schema[table_name]['columns'][row['column_name']] = {
                        'data_type': row['data_type'],
                        'is_nullable': row['is_nullable'] == 'YES',
                        'column_default': row['column_default'],
                        'character_maximum_length': row['character_maximum_length'],
                        'numeric_precision': row['numeric_precision'],
                        'numeric_scale': row['numeric_scale']
                    }
            
            # Process primary keys
            for row in pk_data:
                table_name = row['table_name']
                if table_name in schema:
                    schema[table_name]['primary_keys'].append(row['column_name'])
            
            # Process foreign keys
            for row in fk_data:
                table_name = row['table_name']
                if table_name in schema:
                    schema[table_name]['foreign_keys'].append({
                        'column': row['column_name'],
                        'references_table': row['foreign_table_name'],
                        'references_column': row['foreign_column_name'],
                        'constraint_name': row['constraint_name']
                    })
            
            # Cache the schema
            self.schema_cache = schema
            
            logger.info(f"Schema information cached for {len(schema)} tables")
            return schema
            
        except Exception as e:
            logger.error(f"Error getting schema info: {e}")
            raise
    
    async def get_tables(self) -> List[str]:
        """Get list of table names"""
        try:
            query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """
            
            results = await self.execute_query(query)
            return [row['table_name'] for row in results]
            
        except Exception as e:
            logger.error(f"Error getting tables: {e}")
            raise
    
    async def get_table_sample(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample data from a table"""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit};"
            return await self.execute_query(query)
            
        except Exception as e:
            logger.error(f"Error getting table sample for {table_name}: {e}")
            raise
    
    async def validate_query(self, query: str) -> bool:
        """Validate if a SQL query is safe to execute"""
        try:
            # Basic safety checks
            dangerous_keywords = [
                'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
            ]
            
            query_upper = query.upper()
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    logger.warning(f"Query contains dangerous keyword: {keyword}")
                    return False
            
            # Try to parse the query (basic validation)
            async with self.pool.acquire() as conn:
                await conn.fetch(f"EXPLAIN {query}")
            
            return True
            
        except Exception as e:
            logger.warning(f"Query validation failed: {e}")
            return False
