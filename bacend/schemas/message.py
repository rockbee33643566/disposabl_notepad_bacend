from pydantic import BaseModel

class MessageGet(BaseModel):
    text: str
    recipient_id: int
    used_notepad: int
    time: int

class MessagesGet(BaseModel):
    messages: list[MessageGet]

class MessageSend(BaseModel):
    text: str
    sender_hash: str
    recipient_id: int
    used_notepad: int