# Database Setup and Data Import Guide

This directory contains scripts to set up the PostgreSQL database and import the Olist e-commerce dataset.

## Prerequisites

1. PostgreSQL 17 installed and running
2. Python 3.8+ with pip
3. Olist dataset CSV files downloaded from Kaggle

## Setup Steps

### 1. Create Database
First create the database, then connect to it and run the table creation script:

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE cordly_ai;"

# Connect to the database and create tables
psql -U postgres -d cordly_ai -f setup_database_complete.sql
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download Olist Dataset
1. Go to https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
2. Download all CSV files
3. Place them in the `../data/` directory

### 4. Import Data
```bash
python import_data.py
```

### 5. Run Data Exploration
```bash
python data_exploration.py
```

## Files Description

- `setup_database.sql`: Creates database schema and tables
- `import_data.py`: Imports CSV files into PostgreSQL
- `data_exploration.py`: Performs data analysis and generates reports
- `requirements.txt`: Python dependencies

## Expected Output

After successful import, you should have:
- 9 tables with data imported
- Data profiling reports in HTML format
- Sample analytical queries executed
- Data quality analysis completed

## Troubleshooting

- Ensure PostgreSQL service is running
- Check database connection credentials
- Verify CSV files are in the correct location
- Check file permissions for data directory
