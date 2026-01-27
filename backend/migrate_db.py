import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bhv.db')

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        print("Added is_admin column to user table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column is_admin already exists")
        else:
            print(f"Error: {e}")
            
    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate()
