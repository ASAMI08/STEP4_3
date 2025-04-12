from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_current_active_user
from app.api.users.models import UserModel
from app.api.users.schemas import User, UserInDB

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    user_dict = dict(current_user)
    # パスワードを除外
    user_dict.pop("password", None)
    return user_dict

@router.post("/points")
async def update_user_points(points: int, current_user: UserInDB = Depends(get_current_active_user)):
    success = UserModel.update_points(current_user.user_id, points)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating points"
        )
    
    return {"message": f"Added {points} points to user {current_user.name}"}

@router.post("/answers")
async def increment_user_answers(current_user: UserInDB = Depends(get_current_active_user)):
    success = UserModel.increment_answers(current_user.user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating answer count"
        )
    
    return {"message": f"Incremented answer count for user {current_user.name}"}