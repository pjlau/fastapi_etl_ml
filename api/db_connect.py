import sqlite3
from sqlite3 import Error
import os

def get_db_connection():
    """Connect to SQLite database."""
    db_file = os.path.join("data", "database.db")
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"Error connecting to SQLite: {e}")
        return None