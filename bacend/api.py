from fastapi import FastAPI, HTTPException, status

import sqlite3

import bacend.database as database
from schemas.user import *
from schemas.message import *

app = FastAPI()

@app.post(path="/create_user")
def create_user(user: CreateUserPost) -> UserGet: 
    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO (user_name, hash) VALUES (?, ?)",
            (user.name, user.hash)
        )
    except sqlite3.IntegrityError as e: 
        conn.rollback()
        conn.close()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detailuser="Этот хеш уже используется. Сгенерируйте другой."
        )
    except Exception as e:
        conn.rollback()
        conn.close()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера."
        )
    conn.commit()
    database.close_db_connention(conn=conn)
    user = cursor.fetchone()

    return UserGet(
        id=user["id"]
    )

app.post(path="message/send")
def send_message(message: MessageSend):
    user_hash = message.sender_hash
    conn = database.get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, hash FROM users WHERE hash=(?)",
        (user_hash, )
    )
    cursor.fetchone()

app.get(path="message/get")
def get_messages():
    pass
