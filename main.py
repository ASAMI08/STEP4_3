from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends

# 環境変数の読み込み
load_dotenv()

# APIルーターのインポート
from app.api.auth.router import router as auth_router
from app.api.users.router import router as users_router
from app.api.categories.router import router as categories_router
# 必要に応じて他のルーターもインポート
# from app.api.projects.router import router as projects_router
# from app.api.troubles.router import router as troubles_router
# from app.api.messages.router import router as messages_router

# カテゴリーの初期セットアップ
from app.api.categories.models import CategoryModel
CategoryModel.ensure_categories_exist()

app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 重要: ルートURLでもトークンエンドポイントを提供
# フロントエンドが ${API_URL}/token にアクセスしているため
@app.post("/token")
async def token_root(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    ルートレベルでのトークンエンドポイント
    フロントエンド互換性のために提供
    """
    # auth_router内の関数を直接インポートして使用
    from app.api.auth.router import login_for_access_token
    return await login_for_access_token(form_data)

# APIルートに各ルーターを登録
app.include_router(auth_router, prefix="/api/auth", tags=["認証"])
app.include_router(users_router, prefix="/api/users", tags=["ユーザー"])
app.include_router(categories_router, prefix="/api/categories", tags=["カテゴリー"])
# 必要に応じて他のルーターも追加
# app.include_router(projects_router, prefix="/api/projects", tags=["プロジェクト"])
# app.include_router(troubles_router, prefix="/api/troubles", tags=["お困りごと"])
# app.include_router(messages_router, prefix="/api/messages", tags=["メッセージ"])

# ルートエンドポイント
@app.get("/")
def read_root():
    return {
        "message": "CollabogGames API サーバーが正常に動作しています",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)