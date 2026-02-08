"""
Database models and initialization for BHV application.

This module handles SQLite database setup, schema creation, and connection management
for users, images, narratives, and audit trails.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from config.settings import Config


def get_db_connection() -> sqlite3.Connection:
    """
    Get a database connection with row factory for dict-like access.
    
    Returns:
        sqlite3.Connection: Database connection with row factory
    """
    config = Config()
    db_config = config.get_database_config()
    
    conn = sqlite3.connect(db_config['database_path'])
    conn.row_factory = sqlite3.Row
    
    # Enable foreign key constraints
    conn.execute('PRAGMA foreign_keys = ON')
    
    return conn


def init_db():
    """
    Initialize the database with required tables and indexes.
    Creates all necessary tables for users, images, narratives, and audit trails.
    """
    conn = get_db_connection()
    
    try:
        # Users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'patient' CHECK (role IN ('patient', 'social_worker', 'admin')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                profile_data TEXT  -- JSON field for additional profile information
            )
        ''')
        
        # Images table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                mime_type TEXT,
                narrative TEXT,
                tags TEXT,  -- JSON array of tags
                is_private BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Narratives table (separate from images for flexibility)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS narratives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                narrative_type TEXT DEFAULT 'patient' CHECK (narrative_type IN ('patient', 'social_worker', 'clinical')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (image_id) REFERENCES images (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Audit trail table for compliance
        conn.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id INTEGER,
                details TEXT,  -- JSON field for additional details
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        ''')
        
        # Sessions table for session management
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for performance
        create_indexes(conn)
        
        # Create triggers for audit logging
        create_triggers(conn)
        
        # Insert default admin user if none exists
        create_default_admin(conn)
        
        conn.commit()
        print("Database initialized successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Database initialization failed: {e}")
        raise
    finally:
        conn.close()


def create_indexes(conn: sqlite3.Connection):
    """
    Create database indexes for improved query performance.
    
    Args:
        conn (sqlite3.Connection): Database connection
    """
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
        'CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)',
        'CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at)',
        'CREATE INDEX IF NOT EXISTS idx_narratives_image_id ON narratives(image_id)',
        'CREATE INDEX IF NOT EXISTS idx_narratives_user_id ON narratives(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_log(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)',
        'CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at)'
    ]
    
    for index_sql in indexes:
        conn.execute(index_sql)


def create_triggers(conn: sqlite3.Connection):
    """
    Create database triggers for automatic audit logging and timestamp updates.
    
    Args:
        conn (sqlite3.Connection): Database connection
    """
    # Update timestamp trigger for images
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS update_images_timestamp 
        AFTER UPDATE ON images
        BEGIN
            UPDATE images SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    ''')
    
    # Update timestamp trigger for narratives
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS update_narratives_timestamp 
        AFTER UPDATE ON narratives
        BEGIN
            UPDATE narratives SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    ''')
    
    # Audit trigger for user actions
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS audit_user_updates 
        AFTER UPDATE ON users
        BEGIN
            INSERT INTO audit_log (user_id, action, resource_type, resource_id, details)
            VALUES (NEW.id, 'UPDATE', 'user', NEW.id, 
                    json_object('old_email', OLD.email, 'new_email', NEW.email));
        END
    ''')


def create_default_admin(conn: sqlite3.Connection):
    """
    Create default admin user if no admin exists.
    
    Args:
        conn (sqlite3.Connection): Database connection
    """
    from werkzeug.security import generate_password_hash
    
    # Check if admin exists
    admin_exists = conn.execute(
        "SELECT id FROM users WHERE role = 'admin'"
    ).fetchone()
    
    if not admin_exists:
        # Create default admin
        default_password = 'admin123'  # Should be changed on first login
        password_hash = generate_password_hash(default_password)
        
        conn.execute('''
            INSERT INTO users (email, username, password_hash, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin@bhv.local', 'admin', password_hash, 'admin'))
        
        print("Default admin user created:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   CHANGE THIS PASSWORD IMMEDIATELY!")


class DatabaseManager:
    """
    Database management utilities for BHV application.
    
    Provides methods for database maintenance, backup, and health checks.
    """
    
    def __init__(self):
        """Initialize database manager with configuration."""
        self.config = Config()
        self.db_config = self.config.get_database_config()
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_path (Optional[str]): Custom backup path
            
        Returns:
            str: Path to backup file
        """
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"data/backup_bhv_{timestamp}.db"
        
        # Ensure backup directory exists
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup using SQLite backup API
        source = sqlite3.connect(self.db_config['database_path'])
        backup = sqlite3.connect(backup_path)
        
        source.backup(backup)
        
        source.close()
        backup.close()
        
        return backup_path
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics and health information.
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        conn = get_db_connection()
        
        stats = {}
        
        # Table counts
        tables = ['users', 'images', 'narratives', 'audit_log', 'user_sessions']
        for table in tables:
            result = conn.execute(f'SELECT COUNT(*) as count FROM {table}').fetchone()
            stats[f'{table}_count'] = result['count']
        
        # Database size
        db_path = Path(self.db_config['database_path'])
        stats['database_size_mb'] = db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0
        
        # Recent activity
        stats['recent_uploads'] = conn.execute('''
            SELECT COUNT(*) as count FROM images 
            WHERE created_at > datetime('now', '-24 hours')
        ''').fetchone()['count']
        
        stats['recent_logins'] = conn.execute('''
            SELECT COUNT(*) as count FROM users 
            WHERE last_login > datetime('now', '-24 hours')
        ''').fetchone()['count']
        
        conn.close()
        return stats
    
    def cleanup_expired_sessions(self):
        """Remove expired user sessions from database."""
        conn = get_db_connection()
        
        result = conn.execute('''
            DELETE FROM user_sessions 
            WHERE expires_at < CURRENT_TIMESTAMP OR is_active = 0
        ''')
        
        conn.commit()
        conn.close()
        
        return result.rowcount
    
    def vacuum_database(self):
        """Optimize database by running VACUUM command."""
        conn = get_db_connection()
        conn.execute('VACUUM')
        conn.close()


# Utility functions for common database operations
def log_audit_event(user_id: Optional[int], action: str, resource_type: str, 
                   resource_id: Optional[int] = None, details: Optional[str] = None,
                   ip_address: Optional[str] = None, user_agent: Optional[str] = None):
    """
    Log an audit event to the audit trail.
    
    Args:
        user_id (Optional[int]): User ID performing the action
        action (str): Action being performed
        resource_type (str): Type of resource being acted upon
        resource_id (Optional[int]): ID of the resource
        details (Optional[str]): Additional details in JSON format
        ip_address (Optional[str]): User's IP address
        user_agent (Optional[str]): User's browser user agent
    """
    conn = get_db_connection()
    
    conn.execute('''
        INSERT INTO audit_log (user_id, action, resource_type, resource_id, details, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, action, resource_type, resource_id, details, ip_address, user_agent))
    
    conn.commit()
    conn.close()


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    """
    Get user by ID.
    
    Args:
        user_id (int): User ID
        
    Returns:
        Optional[sqlite3.Row]: User record or None
    """
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user


def get_user_images(user_id: int, limit: int = 50) -> list:
    """
    Get images for a specific user.
    
    Args:
        user_id (int): User ID
        limit (int): Maximum number of images to return
        
    Returns:
        list: List of image records
    """
    conn = get_db_connection()
    images = conn.execute('''
        SELECT * FROM images 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return images