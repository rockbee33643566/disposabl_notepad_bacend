from pydantic import BaseModel

class CreateUserPost(BaseModel):
    name: str
    hash: str

class UserGet(BaseModel):
    id: int