import sqlite3 
from sqlite3 import Connection
from contextlib import contextmanager
from collections.abc import Generator
from pathlib import Path

@contextmanager
def get_db_connection(
    name: str | None = None,
    commit: bool = False
) -> Generator[Connection, None, None]:
    if name is None:
        path = str(
            Path(__file__).parent.parent / "database.db"
        )

    conn = sqlite3.connect(path)
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

def init_db() -> None:
    with get_db_connection(commit=True) as conn:
        conn.execute('''--sql
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_name TEXT NOT NULL,
            hash TEXT NOT NULL UNIQUE
        )
        ''')
        conn.execute('''--sql
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL, 
            text TEXT NOT NULL,
            time INTEGER NOT NULL,
            used_notepad INTEGER,
            is_readed INTEGER DEFAULT 0 CHECK (is_readed IN (0, 1))
        )
        ''')