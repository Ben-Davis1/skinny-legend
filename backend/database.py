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
