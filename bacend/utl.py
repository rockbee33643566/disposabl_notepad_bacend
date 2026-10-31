from fastapi import status, HTTPException

import time 
import sqlite3

from schemas import message, user
from database import get_db_connection


def add_user(user: user.CreateUserPost) -> int:
    with get_db_connection(commit=True) as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO (user_name, hash) VALUES (?, ?)",
                (user.name, user.hash)
            )
        except sqlite3.IntegrityError: 
            conn.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detailuser="Этот хеш уже используется. Сгенерируйте другой."
            )
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE hash=?",
            (user.hash, )
        )
        row = cursor.fetchone()

    return row["id"]

def is_user_exists(user_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE id=?",
            (user_id, )
        )

        row = cursor.fetchone()

    if row is None:
        return False
    else:
        return True

def authentication(sender_hash: str) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, hash FROM users WHERE hash=?",
            (sender_hash, )
        )

        row = cursor.fetchone()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Пользаватель не индефицирован."
            )
        
    return row["id"]


def create_message(message: message.MessageSend, sender_id: int) -> None:
    event_time = time.time()

    with get_db_connection(commit=True) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO (
                sender_id, 
                recipiend_id, 
                text, 
                time, 
                used_notepad, 
                is_readed
            ) VALUES (?, ?, ?, ?, ?, 0)
            """, 
            (
                sender_id,
                message.recipient_id,
                message.text,
                event_time, 
                message.used_notepad
            )
        )

def get_messages(recipient_id: int) -> message.MessagesGet:
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                text,
                recipient_id,
                used_notepad,
                time
            FROM messages
            WHERE recipient_id = ?
                AND is_readed = 0
            """,
            (recipient_id, )
        )
        messages = cursor.fetchall()

    return message.MessagesGet(
        messages=messages
    )

def read_messages(recipient_id: int) -> None:
    with get_db_connection(commit=True) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE messages SET is_readed = 1 WHERE recipient_id = ?",
            (recipient_id, )
        )

def delete_read_messages() -> None:
    with get_db_connection(commit=True) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROPM messages WHERE is_readed=1"
        )