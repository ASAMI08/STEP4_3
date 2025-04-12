from pydantic import BaseModel, Field
from typing import Optional, List
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
    categories: Optional[str] = None  # カテゴリーの文字列（カンマ区切り）
    num_answer: Optional[int] = None
    point_total: Optional[int] = None
    last_login_at: Optional[datetime] = None

class UserInDB(User):
    password: str

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    categories: Optional[List[str]] = None  # フロントから送られるカテゴリー名のリスト

class UserUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    categories: Optional[List[str]] = None