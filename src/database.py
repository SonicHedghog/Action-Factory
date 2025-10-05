import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="postgres",
        port="5432",
        cursor_factory=RealDictCursor
    )

def close_db_connection(conn):
    if conn is not None:
        conn.close()