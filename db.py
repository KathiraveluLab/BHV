import sqlite3

DB_NAME = "users.db"

def get_db():
    db = sqlite3.connect(DB_NAME, check_same_thread=False)
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()


def init_db():
    db = sqlite3.connect(DB_NAME)
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            is_private INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            filename TEXT,
            metadata TEXT,
            visibility TEXT DEFAULT 'private',
            narrative TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)

    db.commit()
    db.close()
