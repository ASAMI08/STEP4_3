import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース接続設定
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "collabodb")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

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

# FastAPI依存性注入用の関数
def get_db():
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()