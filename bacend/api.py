from fastapi import (
    FastAPI, 
    HTTPException, 
    status, 
    Request
)

import sqlite3

from schemas import message, user
from utl import (
    add_user,
    is_user_exists,
    authentication,
    create_message, 
    delete_read_messages,
    get_messages,
    read_messages
)

app = FastAPI()

@app.exception_handler(sqlite3.OperationalError)
def integrity_error_handler(request: Request, exc: sqlite3.IntegrityError) -> None:
    raise HTTPException(
       status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
       detail="База данных не доступна. Попробуйте позже." 
    )

@app.post(path="/user/create")
def create_user(usr: user.CreateUserPost) -> int: 
    user_id = add_user(user=usr)
    return int(user_id)

@app.get(path="user/is_exists")
def is_user(id: int) -> bool:
    return is_user_exists(user_id=id)

@app.post(path="message/send")
def send_message(msg: message.MessageSend):
    sender_id = authentication(sender_hash=msg.sender_hash)
    if not is_user_exists(user_id=sender_id): 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Невозможно отправить сообщение не сушествующему прользователю."
        )

    create_message(message=message)

@app.get(path="message/get")
def check_messages(user_hash: str) -> message.MessagesGet:
    recipient_id = authentication(sender_hash=user_hash)

    messages = get_messages(recipient_id=recipient_id)
    if not messages.messages: 
        return message.MessagesGet(
            messages=[]
        )
    else:
        read_messages(recipient_id)
        delete_read_messages()

        return messages
        