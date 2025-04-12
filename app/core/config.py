import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "CollabogGames0406 API"
    API_V1_STR: str = "/api"
    
    # CORSの設定
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    # JWT設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 開発モード設定
    DEV_MODE: bool = True
    
    # データベース設定
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "collabodb")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))

settings = Settings()