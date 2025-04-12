from fastapi import APIRouter, Depends, HTTPException, status
from app.api.categories.models import CategoryModel
from typing import List

router = APIRouter()

@router.get("/", response_model=List[str])
async def get_categories():
    """カテゴリー一覧を取得するエンドポイント"""
    
    # カテゴリーがデータベースにない場合はデフォルトカテゴリーを返す
    categories = CategoryModel.get_all_categories()
    
    if not categories:
        # データベースから取得できない場合はデフォルト値を返す
        return CategoryModel.get_default_categories()
    
    # 名前のリストに変換
    return [category["name"] for category in categories]