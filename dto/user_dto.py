from pydantic import BaseModel


class UserRegisterDTO(BaseModel):
    username: str
    password: str

class UserUpdateDTO(BaseModel):
    username: str = None
    password: str = None