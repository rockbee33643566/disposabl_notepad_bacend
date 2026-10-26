import sqlite3 
from sqlite3 import Connection

def get_db_connection(name: str = "database.db") -> Connection:
    conn = sqlite3.connect(name)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn: Connection):
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_name TEXT,
        hash TEXT UNIQUE
    )
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        recipient_id INTEGER, 
        text TEXT,
        time REAL,
        used_notepad INTEGER,
        is_readed INTEGER CHECK (is_readed IN (0, 1))
    )
    ''')
    conn.commit()