from fastapi import FastAPI, HTTPException, status

from .schemas import message, user
from .utl import (
    add_user,
    is_user_exists,
    authentication,
    create_message,
    delete_read_messages,
    get_messages,
    read_messages,
)
from .logger import get_logger

logger = get_logger(__name__)

app = FastAPI()


@app.post(path="/user/create")
async def create_user(usr: user.CreateUserPost) -> int:
    user_id = await add_user(user=usr)
    logger.info("Создан пользователь id=%s", user_id)
    return int(user_id)


@app.get(path="/user/is_exists")
async def is_user(id: int) -> bool:
    exists = await is_user_exists(user_id=id)
    logger.info("Проверка существования пользователя id=%s -> %s", id, exists)
    return exists


@app.post(path="/message/send")
async def send_message(msg: message.MessageSend) -> int:
    sender_id = await authentication(sender_hash=msg.sender_hash)

    if not await is_user_exists(user_id=msg.recipient_id):
        logger.warning(
            "Попытка отправки сообщения несуществующему получателю id=%s",
            msg.recipient_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Невозможно отправить сообщение несуществующему пользователю.",
        )

    message_id = await create_message(message=msg, sender_id=sender_id)
    logger.info("Сообщение от id=%s для id=%s отправлено", sender_id, msg.recipient_id)
    return int(message_id)


@app.get(path="/message/get")
async def check_messages(user_hash: str) -> message.MessagesGet:
    user_id = await authentication(sender_hash=user_hash)

    messages = await get_messages(user_id)

    if not messages.messages:
        logger.info("Нет новых сообщений для id=%s", user_id)
        return message.MessagesGet(messages=[])

    await read_messages(recipient_id=user_id)
    await delete_read_messages()
    logger.info("Получено и удалено %s сообщений для id=%s", len(messages.messages), user_id)

    return messages