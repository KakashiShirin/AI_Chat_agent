import pandas as pd
import uuid
from typing import Dict, List, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy import text
from app.models.database import engine, metadata
from app.core.config import settings
import io
import re

class DataProcessor:
    """Service for processing uploaded data files"""
    
    def __init__(self):
        self.engine = engine
    
    def sanitize_column_name(self, name: str) -> str:
        """Sanitize column names for SQL compatibility"""
        # Remove special characters and replace spaces with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', str(name))
        # Ensure it starts with a letter or underscore
        if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
            sanitized = '_' + sanitized
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        return sanitized or 'column'
    
    def infer_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Infer and convert data types for better analysis"""
        for column in df.columns:
            # Skip if column name suggests it should be numeric
            numeric_keywords = ['salary', 'experience', 'score', 'age', 'count', 'amount', 'price', 'value', 'number']
            is_likely_numeric = any(keyword in column.lower() for keyword in numeric_keywords)
            
            if is_likely_numeric:
                # Try to convert to numeric first for likely numeric columns
                try:
                    df[column] = pd.to_numeric(df[column])
                    continue  # Skip datetime conversion for numeric columns
                except (ValueError, TypeError):
                    pass
            
            # Try to convert to numeric for other columns
            try:
                df[column] = pd.to_numeric(df[column])
            except (ValueError, TypeError):
                # If conversion fails, try datetime only for non-numeric columns
                try:
                    df[column] = pd.to_datetime(df[column], format='mixed')
                except (ValueError, TypeError):
                    # If both fail, keep as original type
                    pass
            
            # Fill missing values
            if df[column].dtype == 'object':
                df[column] = df[column].fillna('NA')
            else:
                df[column] = df[column].fillna(0)
        
        return df
    
    async def process_and_store_file(self, file: UploadFile, session_id: str) -> Dict[str, Any]:
        """
        Process uploaded file and store in database
        
        Args:
            file: Uploaded file object
            session_id: Unique session identifier
            
        Returns:
            Dictionary containing metadata about stored tables
        """
        try:
            # Read file content
            content = await file.read()
            
            # Determine file type and read accordingly
            file_extension = file.filename.split('.')[-1].lower()
            
            if file_extension == 'csv':
                df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            elif file_extension in ['xlsx', 'xls']:
                # For Excel files, read all sheets
                excel_file = pd.ExcelFile(io.BytesIO(content))
                sheets_data = {}
                
                for sheet_name in excel_file.sheet_names:
                    df_sheet = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
                    sheets_data[sheet_name] = df_sheet
                
                # Process each sheet
                stored_tables = []
                for sheet_name, df_sheet in sheets_data.items():
                    table_info = self._process_dataframe(df_sheet, session_id, sheet_name)
                    stored_tables.append(table_info)
                
                return {
                    "session_id": session_id,
                    "tables": stored_tables,
                    "total_sheets": len(sheets_data)
                }
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")
            
            # Process single CSV file
            table_info = self._process_dataframe(df, session_id)
            return {
                "session_id": session_id,
                "tables": [table_info],
                "total_sheets": 1
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    def _process_dataframe(self, df: pd.DataFrame, session_id: str, sheet_name: str = None) -> Dict[str, Any]:
        """Process a single DataFrame and store it in the database"""
        
        # Clean column names
        df.columns = [self.sanitize_column_name(col) for col in df.columns]
        
        # Infer data types
        df = self.infer_data_types(df)
        
        # Generate table name
        table_suffix = f"_{sheet_name}" if sheet_name else ""
        table_name = f"data_{session_id}{table_suffix}".replace('-', '_')
        
        # Store in database
        df.to_sql(
            name=table_name,
            con=self.engine,
            if_exists='replace',
            index=False,
            method='multi'
        )
        
        # Get column information
        column_info = []
        for col in df.columns:
            column_info.append({
                "name": col,
                "type": str(df[col].dtype),
                "sample_values": df[col].head(3).tolist()
            })
        
        return {
            "table_name": table_name,
            "sheet_name": sheet_name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": column_info
        }
    
    def get_table_schema(self, session_id: str) -> Dict[str, Any]:
        """Get schema information for all tables in a session"""
        try:
            with self.engine.connect() as connection:
                # Find all tables for this session (convert hyphens to underscores)
                session_pattern = session_id.replace('-', '_')
                query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE :pattern
                """)
                
                result = connection.execute(query, {"pattern": f"data_{session_pattern}%"})
                tables = [row[0] for row in result]
                
                schema_info = {}
                for table_name in tables:
                    # Get column information
                    column_query = text("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = :table_name
                        ORDER BY ordinal_position
                    """)
                    
                    columns_result = connection.execute(column_query, {"table_name": table_name})
                    columns = [
                        {
                            "name": row[0],
                            "type": row[1],
                            "nullable": row[2] == 'YES'
                        }
                        for row in columns_result
                    ]
                    
                    # Get sample data (first 5 rows)
                    sample_query = text(f"SELECT * FROM {table_name} LIMIT 5")
                    sample_result = connection.execute(sample_query)
                    sample_data = []
                    
                    for row in sample_result:
                        # Convert row to dictionary
                        row_dict = {}
                        for i, value in enumerate(row):
                            column_name = columns[i]['name'] if i < len(columns) else f'column_{i}'
                            row_dict[column_name] = value
                        sample_data.append(row_dict)
                    
                    schema_info[table_name] = {
                        "columns": columns,
                        "table_name": table_name,
                        "sample_data": sample_data
                    }
                
                return schema_info
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving schema: {str(e)}")

# Create global instance
data_processor = DataProcessor()
