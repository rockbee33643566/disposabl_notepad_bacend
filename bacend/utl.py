from fastapi import status, HTTPException

import time 
import sqlite3

from .schemas import message, user
from .database import get_db_connection
from .logger import get_logger

logger = get_logger(__name__)


async def add_user(user: user.CreateUserPost) -> int:
    async with get_db_connection(commit=True) as conn:
        cursor = await conn.cursor()
        
        try:
            await cursor.execute("""--sql
                    INSERT INTO users (user_name, hash) VALUES (?, ?)
                """,
                (user.name, user.hash)
            )
        except sqlite3.IntegrityError: 
            await conn.rollback()
            logger.warning("Конфликт: хеш %s уже используется", user.hash)

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Этот хеш уже используется. Сгенерируйте другой."
            )
        
    async with get_db_connection() as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            "SELECT id FROM users WHERE hash=?",
            (user.hash, )
        )
        row = await cursor.fetchone()

    return row["id"]

async def is_user_exists(user_id: int) -> bool:
    async with get_db_connection() as conn:
        cursor = await conn.cursor()

        await cursor.execute(
            "SELECT id FROM users WHERE id=?",
            (user_id, )
        )

        row = await cursor.fetchone()

    if row is None:
        return False
    else:
        return True

async def authentication(sender_hash: str) -> int:
    async with get_db_connection() as conn:
        cursor = await conn.cursor()
        
        await cursor.execute(
            "SELECT id, hash FROM users WHERE hash=?",
            (sender_hash, )
        )

        row = await cursor.fetchone()
        if row is None:
            logger.warning("Аутентификация не удалась: хеш %s не найден", sender_hash)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Пользователь не идентифицирован."
            )
        
    return row["id"]

async def create_message(message: message.MessageSend, sender_id: int) -> int:
    async with get_db_connection(commit=True) as conn:
        cursor = await conn.cursor()

        await cursor.execute("""--sql
            INSERT INTO messages (
                sender_id, 
                recipient_id, 
                text, 
                time, 
                used_notepad
            ) VALUES (?, ?, ?, ?, ?)
            """, 
            (
                sender_id,
                message.recipient_id,
                message.text,
                int(time.time()), 
                message.used_notepad
            )
        )

        return cursor.lastrowid

async def get_messages(user_id: int) -> message.MessagesGet:
    async with get_db_connection() as conn:
        cursor = await conn.cursor()

        await cursor.execute("""--sql
            SELECT
                text,
                sender_id, 
                used_notepad,
                time
            FROM messages
            WHERE recipient_id = ?
                AND is_readed = 0
            """,
            (user_id, )
        )
        messages = await cursor.fetchall()

    return message.MessagesGet(messages=[dict(i) for i in messages])

async def read_messages(recipient_id: int) -> None:
    async with get_db_connection(commit=True) as conn:
        cursor = await conn.cursor()

        await cursor.execute(
            "UPDATE messages SET is_readed = 1 WHERE recipient_id = ?",
            (recipient_id, )
        )

async def delete_read_messages() -> None:
    async with get_db_connection(commit=True) as conn:
        cursor = await conn.cursor()

        await cursor.execute(
            "DELETE FROM messages WHERE is_readed=1"
        )