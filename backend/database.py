import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.getenv('DATABASE_PATH', './skinny_legend.db')

def init_db():
    """Initialize the database with the schema"""
    conn = sqlite3.connect(DATABASE_PATH)
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE_PATH}")

def run_migrations():
    """Run all database migrations (safe to run on existing databases)"""
    conn = sqlite3.connect(DATABASE_PATH)
    migrate_db(conn)
    conn.close()

def migrate_db(conn):
    """Run database migrations"""
    cursor = conn.cursor()

    # Migration: Remove UNIQUE constraint from weight_logs
    try:
        # Check if weight_logs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weight_logs'")
        if cursor.fetchone():
            print("Migrating weight_logs table to remove UNIQUE constraint...")

            # Recreate table without UNIQUE constraint
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weight_logs_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    weight_kg REAL NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Copy data from old table
            cursor.execute('''
                INSERT INTO weight_logs_new (id, user_id, date, weight_kg, notes, created_at)
                SELECT id, user_id, date, weight_kg, notes, created_at FROM weight_logs
            ''')

            # Drop old table and rename new one
            cursor.execute('DROP TABLE weight_logs')
            cursor.execute('ALTER TABLE weight_logs_new RENAME TO weight_logs')

            print("Migration complete!")
            conn.commit()
    except Exception as e:
        print(f"Migration error (safe to ignore if first run): {e}")
        conn.rollback()

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def query_db(query, args=(), one=False):
    """Execute a query and return results"""
    with get_db() as conn:
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        return (dict(rv[0]) if rv else None) if one else [dict(row) for row in rv]

def execute_db(query, args=()):
    """Execute a query that modifies the database"""
    with get_db() as conn:
        cur = conn.execute(query, args)
        return cur.lastrowid
