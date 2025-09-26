#!/usr/bin/env python3
"""
Diagnose products table import issues
"""

import pandas as pd
import numpy as np

def diagnose_products_data():
    """Diagnose issues with products data"""
    print("Loading products dataset...")
    df = pd.read_csv('data/olist_products_dataset.csv')
    
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Check data types
    print("\nData types:")
    print(df.dtypes)
    
    # Check for null values
    print("\nNull values:")
    print(df.isnull().sum())
    
    # Check numeric columns
    numeric_cols = [
        'product_name_lenght', 'product_description_lenght', 
        'product_photos_qty', 'product_weight_g', 
        'product_length_cm', 'product_height_cm', 'product_width_cm'
    ]
    
    print("\nNumeric columns analysis:")
    for col in numeric_cols:
        print(f"\n{col}:")
        print(f"  Min: {df[col].min()}")
        print(f"  Max: {df[col].max()}")
        print(f"  Null count: {df[col].isnull().sum()}")
        print(f"  Unique values: {df[col].nunique()}")
        
        # Check for problematic values
        if df[col].max() > 2**63 - 1:  # BIGINT max value
            print(f"  WARNING: Max value exceeds BIGINT range!")
        
        # Check for infinity values
        if np.isinf(df[col]).any():
            print(f"  WARNING: Contains infinity values!")
        
        # Check for very large values
        large_values = df[df[col] > 1000000][col]
        if len(large_values) > 0:
            print(f"  WARNING: {len(large_values)} values > 1,000,000")
            print(f"  Sample large values: {large_values.head(5).tolist()}")
    
    # Test conversion to int
    print("\nTesting int conversion:")
    for col in numeric_cols:
        try:
            # Convert to int, handling NaN
            test_series = df[col].fillna(0).astype(int)
            print(f"  {col}: OK")
        except Exception as e:
            print(f"  {col}: ERROR - {e}")
    
    # Check for string values in numeric columns
    print("\nChecking for string values in numeric columns:")
    for col in numeric_cols:
        # Convert to string and check for non-numeric patterns
        str_values = df[col].astype(str)
        non_numeric = str_values[~str_values.str.replace('.', '').str.replace('-', '').str.isdigit()]
        if len(non_numeric) > 0:
            print(f"  {col}: {len(non_numeric)} non-numeric values")
            print(f"    Sample: {non_numeric.head(5).tolist()}")
        else:
            print(f"  {col}: All values are numeric")

if __name__ == "__main__":
    diagnose_products_data()
