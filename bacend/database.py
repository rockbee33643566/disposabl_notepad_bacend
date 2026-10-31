import sqlite3 
from sqlite3 import Connection
from contextlib import contextmanager
from collections.abc import Generator

@contextmanager
def get_db_connection(
    name: str | None = None,
    commit: bool = False
) -> Generator[Connection, None, None]:
    if name is None:
        name = "database.db"

    conn = sqlite3.connect(name)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        if commit:
            conn.commit()
    finally:
        conn.close()

def init_db(conn: Connection) -> None:
    with get_db_connection(commit=True) as conn:
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