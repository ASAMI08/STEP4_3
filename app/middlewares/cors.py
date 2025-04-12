from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app: FastAPI) -> None:
    """CORSミドルウェアを設定する"""
    
    # 環境変数からCORSオリジンを取得（カンマ区切りで複数指定可能）
    origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    origins = [origin.strip() for origin in origins_str.split(",")]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )