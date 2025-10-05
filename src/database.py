import os
import json
import psycopg2  # type: ignore
from psycopg2.extras import RealDictCursor  # type: ignore
from typing import Dict, List, Optional, Any
import threading
import time

class DatabaseManager:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        self._connection = None
        self._lock = threading.Lock()
        
    def get_connection(self):
        """Get a database connection, creating one if needed"""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
            self._connection.autocommit = True
        return self._connection
    
    def init_database(self):
        """Initialize database tables"""
        with self._lock:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # Create tool_updates table for pub/sub like functionality
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tool_updates (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        code TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create a table to track last processed update for each subscriber
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS subscriber_state (
                        subscriber_id VARCHAR(255) PRIMARY KEY,
                        last_processed_id INTEGER DEFAULT 0,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
    
    def publish_tool_update(self, name: str, description: str, code: str):
        """Publish a tool update (equivalent to Redis publish)"""
        with self._lock:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO tool_updates (name, description, code)
                    VALUES (%s, %s, %s)
                """, (name, description, code))
    
    def get_new_tool_updates(self, subscriber_id: str) -> List[Dict]:
        """Get new tool updates for a subscriber (equivalent to Redis subscribe)"""
        with self._lock:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                # Get the last processed ID for this subscriber
                cursor.execute("""
                    SELECT last_processed_id FROM subscriber_state 
                    WHERE subscriber_id = %s
                """, (subscriber_id,))
                
                result = cursor.fetchone()
                last_processed_id = int(result['last_processed_id']) if result else 0  # type: ignore
                
                # Get new updates
                cursor.execute("""
                    SELECT id, name, description, code, created_at
                    FROM tool_updates 
                    WHERE id > %s 
                    ORDER BY id ASC
                """, (last_processed_id,))
                
                updates = cursor.fetchall()
                
                if updates:
                    # Update the last processed ID
                    latest_id = int(updates[-1]['id'])  # type: ignore
                    cursor.execute("""
                        INSERT INTO subscriber_state (subscriber_id, last_processed_id, updated_at)
                        VALUES (%s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (subscriber_id) 
                        DO UPDATE SET 
                            last_processed_id = EXCLUDED.last_processed_id,
                            updated_at = EXCLUDED.updated_at
                    """, (subscriber_id, latest_id))
                
                return [dict(update) for update in updates]
    
    def close(self):
        """Close the database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()

# Global database manager instance
db_manager = DatabaseManager()