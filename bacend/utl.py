# Тут будет всякая шняка что бы не грамоздить api.py
import time 
import sqlite3

import database
from fastapi import status, HTTPException
from schemas.message import *
from schemas.user import *


def add_user(user: CreateUserPost) -> int:
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO (user_name, hash) VALUES (?, ?)",
            (user.name, user.hash)
        )
    except sqlite3.IntegrityError: 
        conn.rollback()
        conn.close()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detailuser="Этот хеш уже используется. Сгенерируйте другой."
        )
    
    conn.commit()
    cursor.fetchall()

    cursor.execute(
        "SELECT id FROM users WHERE hash=?",
        (user.hash, )
    )
    row = cursor.fetchone()
    conn.close()

    return row["id"]

def is_user_exists(user_id: int) -> bool:
    conn = database.get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE id=?",
        (user_id, )
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False
    else:
        return True

def authentication(sender_hash: str) -> int:
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, hash FROM users WHERE hash=?",
        (sender_hash, )
    )

    row = cursor.fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пользаватель и индефицирован."
        )
    conn.close()
    
    return row["id"]


def create_message(message: MessageSend, sender_id: int) -> None:
    conn = database.get_db_connection()
    cursor = conn.cursor()

    event_time = time.time()

    cursor.execute(
        """INSERT INTO (
            sender_id, 
            recipiend_id, 
            text, 
            time, 
            used_notepad, 
            is_readed
        ) VALUES (?, ?, ?, ?, ?, ?)
        """, 
        (
            sender_id,
            message.recipient_id,
            message.text,
            event_time, 
            message.used_notepad,
            0
        )
    )
    
    conn.commit()
    conn.close()

def get_messages(recipient_id: int) -> MessagesGet:
    conn = database.get_db_connection()
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

    conn.close()

    return MessagesGet(
        messages=messages
    )

def delete_read_messages() -> None:
    conn = database.get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROPM messages WHERE is_readed=1"
    )
    
    conn.commit()
    conn.close()
