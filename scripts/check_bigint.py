#!/usr/bin/env python3
"""
Check for BIGINT range issues in products data
"""

import pandas as pd

def check_bigint_range():
    """Check if any values exceed BIGINT range"""
    print("Loading products dataset...")
    df = pd.read_csv('data/olist_products_dataset.csv')
    
    bigint_max = 2**63 - 1
    print(f"BIGINT max value: {bigint_max}")
    
    numeric_cols = [
        'product_name_lenght', 'product_description_lenght', 
        'product_photos_qty', 'product_weight_g', 
        'product_length_cm', 'product_height_cm', 'product_width_cm'
    ]
    
    print("\nChecking for values exceeding BIGINT range:")
    for col in numeric_cols:
        max_val = df[col].max()
        exceeds = max_val > bigint_max
        print(f"{col}: max={max_val}, exceeds_bigint={exceeds}")
        
        if exceeds:
            print(f"  WARNING: {col} has values exceeding BIGINT range!")
            large_values = df[df[col] > bigint_max][col]
            print(f"  Found {len(large_values)} values exceeding BIGINT range")
            print(f"  Sample: {large_values.head(5).tolist()}")
    
    # Check for any values that might cause issues
    print("\nChecking for problematic values:")
    for col in numeric_cols:
        # Check for very large values
        large_values = df[df[col] > 1000000][col]
        if len(large_values) > 0:
            print(f"{col}: {len(large_values)} values > 1,000,000")
            print(f"  Max: {large_values.max()}")
            print(f"  Sample: {large_values.head(3).tolist()}")
        
        # Check for negative values
        negative_values = df[df[col] < 0][col]
        if len(negative_values) > 0:
            print(f"{col}: {len(negative_values)} negative values")
            print(f"  Sample: {negative_values.head(3).tolist()}")

if __name__ == "__main__":
    check_bigint_range()
