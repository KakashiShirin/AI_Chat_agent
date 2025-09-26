#!/usr/bin/env python3
"""
Verification Script for olist_order_reviews_dataset
"""

import os
import sys
import psycopg2

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

def verify_reviews_data():
    """Verify the imported reviews data"""
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check total count
        cursor.execute('SELECT COUNT(*) FROM olist_order_reviews_dataset;')
        total_count = cursor.fetchone()[0]
        print(f'Total reviews: {total_count}')
        
        # Check review score distribution
        cursor.execute('''
            SELECT review_score, COUNT(*) 
            FROM olist_order_reviews_dataset 
            GROUP BY review_score 
            ORDER BY review_score;
        ''')
        print('\nReview score distribution:')
        for score, count in cursor.fetchall():
            print(f'  Score {score}: {count:,} reviews')
        
        # Check for null values
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(review_comment_title) as with_title,
                COUNT(review_comment_message) as with_message
            FROM olist_order_reviews_dataset;
        ''')
        total, with_title, with_message = cursor.fetchone()
        print(f'\nComment statistics:')
        print(f'  Total reviews: {total:,}')
        print(f'  With comment title: {with_title:,} ({with_title/total*100:.1f}%)')
        print(f'  With comment message: {with_message:,} ({with_message/total*100:.1f}%)')
        
        # Sample data
        cursor.execute('''
            SELECT review_id, order_id, review_score, review_comment_title
            FROM olist_order_reviews_dataset 
            LIMIT 5;
        ''')
        print(f'\nSample reviews:')
        for row in cursor.fetchall():
            print(f'  {row[0][:8]}... | Order: {row[1][:8]}... | Score: {row[2]} | Title: {row[3][:30] if row[3] else "None"}...')
        
        print('\nReviews table verification completed successfully!')
        
    except Exception as e:
        print(f'Error during verification: {e}')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_reviews_data()
