import psycopg2
from psycopg2.extras import RealDictCursor
import os
from urllib.parse import urlparse

def get_db_connection():
    # Get the DATABASE_URL from environment variable
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    # Parse the DATABASE_URL
    db_url = urlparse(database_url)
    
    return psycopg2.connect(
        dbname=db_url.path[1:],  # Remove leading slash
        user=db_url.username,
        password=db_url.password,
        host=db_url.hostname,
        port=db_url.port,
        cursor_factory=RealDictCursor
    )

def close_db_connection(conn):
    if conn is not None:
        conn.close()