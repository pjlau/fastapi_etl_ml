import pandas as pd
import sqlite3
import os
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def extract_data():
    """Create and populate a temporary SQLite table with sample data."""
    db_file = os.path.join("data", "database.db")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # Create temporary table
    cursor.execute("""
        CREATE TEMPORARY TABLE temp_customers (
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)
    # Insert sample data
    sample_data = [
        ("Alice", 10, 5.0),
        ("Bob", 15, 3.0),
        ("Charlie", 8, 6.0)
    ]
    cursor.executemany(
        "INSERT INTO temp_customers (name, quantity, price) VALUES (?, ?, ?)",
        sample_data
    )
    conn.commit()
    # Read into DataFrame
    df = pd.read_sql("SELECT name, quantity, price FROM temp_customers", conn)
    conn.close()
    if df.empty:
        logger.error("Temporary table temp_customers is empty.")
        sys.exit(1)
    logger.info(f"Extracted {len(df)} rows from temp_customers table.")
    return df

def transform_data(df):
    """Transform data by cleaning and computing new columns."""
    df = df.dropna()
    df["total_spent"] = df["quantity"] * df["price"]
    # Ensure data/processed directory exists
    processed_dir = os.path.join("data", "processed")
    try:
        os.makedirs(processed_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory {processed_dir}: {e}")
        sys.exit(1)
    output_file = os.path.join(processed_dir, "customers_processed.csv")
    try:
        df.to_csv(output_file, index=False)
        logger.info(f"Saved transformed data to {output_file}")
    except Exception as e:
        logger.error(f"Failed to write to {output_file}: {e}")
        sys.exit(1)
    return df

def load_data(df):
    """Load data into permanent SQLite customers table."""
    db_file = os.path.join("data", "database.db")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # Create permanent table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            total_spent REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Clear existing data
    cursor.execute("DELETE FROM customers")
    # Insert data
    rows_inserted = 0
    for _, row in df.iterrows():
        cursor.execute(
            "INSERT INTO customers (name, total_spent) VALUES (?, ?)",
            (row["name"], row["total_spent"])
        )
        rows_inserted += 1
    conn.commit()
    # Verify insertion
    cursor.execute("SELECT COUNT(*) FROM customers")
    count = cursor.fetchone()[0]
    if count != rows_inserted:
        logger.error(f"Inserted {rows_inserted} rows, but found {count} in customers table")
        conn.close()
        sys.exit(1)
    logger.info(f"Inserted {rows_inserted} rows into customers table in {db_file}.")
    conn.close()

def run_etl():
    """Run the ETL pipeline."""
    logger.info("Starting ETL pipeline.")
    raw_data = extract_data()
    transformed_data = transform_data(raw_data)
    load_data(transformed_data)
    logger.info("ETL pipeline completed successfully.")

if __name__ == "__main__":
    run_etl()