import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

@asynccontextmanager
async def get_db_connection(
    name: str | None = None,
    commit: bool = False
) -> AsyncIterator[aiosqlite.Connection]:
    path = (
        name
        if name is not None
        else str(Path(__file__).parent.parent / "database.db")
    )

    conn = await aiosqlite.connect(path)
    conn.row_factory = aiosqlite.Row

    try:
        yield conn
    except Exception:
        await conn.rollback()
        raise
    else:
        if commit:
            await conn.commit()
    finally:
        await conn.close()

async def init_db() -> None:
    async with get_db_connection(commit=True) as conn:
        await conn.execute('''--sql
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_name TEXT NOT NULL,
            hash TEXT NOT NULL UNIQUE
        )
        ''')
        await conn.execute('''--sql
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