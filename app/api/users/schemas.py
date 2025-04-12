from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    user_id: int
    name: str
    category_id: Optional[int] = None
    num_answer: Optional[int] = None
    point_total: Optional[int] = None
    last_login_at: Optional[datetime] = None

class UserInDB(User):
    password: str

class UserCreate(BaseModel):
    name: str
    password: str
    category_id: Optional[int] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None