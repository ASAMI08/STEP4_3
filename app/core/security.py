from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# シークレットキーの設定
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 開発モード設定 - パスワードハッシュをスキップ
DEV_MODE = True  # 開発モードをオンに

# パスワードハッシュのためのコンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, stored_password):
    if DEV_MODE:
        # 開発モード: 平文パスワード同士を直接比較
        print(f"平文パスワード比較: {plain_password} と {stored_password}")
        return plain_password == stored_password
    else:
        # 本番モード: ハッシュ化されたパスワードを検証
        return pwd_context.verify(plain_password, stored_password)

def get_password_hash(password):
    if DEV_MODE:
        return password
    return pwd_context.hash(password)

# JWTトークン作成
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return {"username": username}
    except JWTError:
        return None