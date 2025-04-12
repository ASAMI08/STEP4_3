from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor

# 環境変数の読み込み
load_dotenv()

# シークレットキーの設定（本番環境では.envファイルから読み込むべき）
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 開発モード設定 - パスワードハッシュをスキップ
DEV_MODE = True  # 開発モードをオンに

# データベース接続設定
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "collabodb")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

# パスワードハッシュのためのコンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2スキーマの設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.jsのデフォルトのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース接続関数
def get_db_connection():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        port=DB_PORT,
        charset='utf8mb4',
        cursorclass=DictCursor,
        autocommit=True
    )
    return connection


# モデル定義
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


def verify_password(plain_password, stored_password):
    if DEV_MODE:
        # 開発モード: 平文パスワード同士を直接比較
        print(f"平文パスワード比較: {plain_password} と {stored_password}")
        return plain_password == stored_password
    else:
        # 本番モード: ハッシュ化されたパスワードを検証
        return pwd_context.verify(plain_password, stored_password)

# ユーザー認証
def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# ユーザー取得（ユーザー名で検索）
def get_user_by_username(username: str):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE name = %s"
            cursor.execute(sql, (username,))
            user_data = cursor.fetchone()
            
        connection.close()
        
        if user_data:
            return UserInDB(**user_data)
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None

# ユーザー取得（ID検索）
def get_user_by_id(user_id: int):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            user_data = cursor.fetchone()
            
        connection.close()
        
        if user_data:
            return UserInDB(**user_data)
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None

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

# 現在のユーザー取得
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception    
    return user

# アクティブなユーザー取得
async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    return current_user

# ログイン時に最終ログイン時間を更新
def update_last_login(user_id: int):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE users SET last_login_at = NOW() WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating last login: {e}")
        return False

# ログインルート
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
# 最終ログイン時間を更新
    update_last_login(user.user_id)        
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ユーザー登録ルート
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    # 既存ユーザーチェック
    existing_user = get_user_by_username(user.name)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    # パスワードハッシュ化
    #hashed_password = pwd_context.hash(user.password)
    
    # パスワード処理 - 開発モードでは平文で保存
    password_to_store = user.password  # 開発モードでは平文パスワードをそのまま使用
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO users (name, password, category_id, last_login_at) 
            VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(sql, (user.name, password_to_store, user.category_id))
            user_id = cursor.lastrowid
        connection.close()
        
        return {"user_id": user_id, "message": "User successfully registered"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# ユーザー情報取得ルート
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    user_dict = current_user.dict()
    # パスワードを除外
    user_dict.pop("password", None)
    return user_dict

# ポイント更新ルート
@app.post("/users/points")
async def update_user_points(points: int, current_user: UserInDB = Depends(get_current_active_user)):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE users SET point_total = point_total + %s WHERE user_id = %s"
            cursor.execute(sql, (points, current_user.user_id))
        connection.close()
        
        return {"message": f"Added {points} points to user {current_user.name}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating points: {str(e)}"
        )

# 回答数更新ルート
@app.post("/users/answers")
async def increment_user_answers(current_user: UserInDB = Depends(get_current_active_user)):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE users SET num_answer = num_answer + 1 WHERE user_id = %s"
            cursor.execute(sql, (current_user.user_id,))
        connection.close()
        
        return {"message": f"Incremented answer count for user {current_user.name}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating answer count: {str(e)}"
        )

# ログイン状態確認ルート
@app.get("/validate-token")
async def validate_token(current_user: User = Depends(get_current_active_user)):
    return {"valid": True, "username": current_user.name}

# サーバーの起動確認用ルート
@app.get("/")
async def root():
    return {"message": "ログインAPIサーバーが正常に動作しています", "dev_mode": DEV_MODE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)