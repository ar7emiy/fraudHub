"""
Database operations for investigation status tracking
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

from config import DATABASE_PATH, VALID_STATUSES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for investigation status tracking"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_PATH
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create investigation status history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investigation_status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_entity_name 
                ON investigation_status_history(entity_name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON investigation_status_history(timestamp)
            """)
            
            logger.info(f"Database initialized at {self.db_path}")
    
    def add_status(self, entity_name: str, status: str) -> bool:
        """
        Add a status change for an entity
        
        Args:
            entity_name: Name of the entity
            status: New status value
            
        Returns:
            True if successful, False otherwise
        """
        if status not in VALID_STATUSES:
            logger.error(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")
            return False
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO investigation_status_history (entity_name, status)
                    VALUES (?, ?)
                """, (entity_name, status))
                
                logger.info(f"Status updated for {entity_name}: {status}")
                return True
        except Exception as e:
            logger.error(f"Error adding status: {e}")
            return False
    
    def get_latest_status(self, entity_name: str) -> Optional[str]:
        """
        Get the latest status for an entity
        
        Args:
            entity_name: Name of the entity
            
        Returns:
            Latest status string or None if no status exists
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT status FROM investigation_status_history
                    WHERE entity_name = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (entity_name,))
                
                result = cursor.fetchone()
                return result['status'] if result else None
        except Exception as e:
            logger.error(f"Error getting latest status: {e}")
            return None
    
    def get_status_history(self, entity_name: str) -> List[Dict]:
        """
        Get full status history for an entity
        
        Args:
            entity_name: Name of the entity
            
        Returns:
            List of status history records
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, entity_name, status, timestamp
                    FROM investigation_status_history
                    WHERE entity_name = ?
                    ORDER BY timestamp DESC
                """, (entity_name,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting status history: {e}")
            return []
    
    def get_all_latest_statuses(self) -> Dict[str, str]:
        """
        Get latest status for all entities
        
        Returns:
            Dictionary mapping entity_name to latest status
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT entity_name, status
                    FROM investigation_status_history h1
                    WHERE timestamp = (
                        SELECT MAX(timestamp)
                        FROM investigation_status_history h2
                        WHERE h2.entity_name = h1.entity_name
                    )
                """)
                
                rows = cursor.fetchall()
                return {row['entity_name']: row['status'] for row in rows}
        except Exception as e:
            logger.error(f"Error getting all latest statuses: {e}")
            return {}
    
    def initialize_entity_statuses(self, entity_names: List[str], default_status: str = 'Not Reviewed'):
        """
        Initialize status for entities that don't have one
        
        Args:
            entity_names: List of entity names
            default_status: Default status to assign
        """
        existing_statuses = self.get_all_latest_statuses()
        
        for entity_name in entity_names:
            if entity_name not in existing_statuses:
                self.add_status(entity_name, default_status)
        
        logger.info(f"Initialized {len(entity_names)} entity statuses")


if __name__ == "__main__":
    # Test database operations
    db = DatabaseManager()
    
    # Test adding statuses
    db.add_status("Dr. Michael Rodriguez", "Not Reviewed")
    db.add_status("Dr. Michael Rodriguez", "Under Investigation")
    db.add_status("James Mitchell", "Bad Actor")
    
    # Test getting latest status
    latest = db.get_latest_status("Dr. Michael Rodriguez")
    print(f"Latest status: {latest}")
    
    # Test getting history
    history = db.get_status_history("Dr. Michael Rodriguez")
    print(f"History: {history}")
    
    # Test getting all statuses
    all_statuses = db.get_all_latest_statuses()
    print(f"All statuses: {all_statuses}")