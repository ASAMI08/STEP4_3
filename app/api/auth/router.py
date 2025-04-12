from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

from app.core.security import verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from app.api.users.models import UserModel
from app.api.users.schemas import Token, UserCreate

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def authenticate_user(username: str, password: str):
    user = UserModel.get_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 最終ログイン時間を更新
    UserModel.update_last_login(user.user_id)        
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    # 既存ユーザーチェック
    existing_user = UserModel.get_by_username(user.name)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    # パスワード処理
    password_to_store = get_password_hash(user.password)
    
    user_id = UserModel.create(user, password_to_store)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during registration"
        )
        
    return {"user_id": user_id, "message": "User successfully registered"}

@router.get("/validate-token")
async def validate_token(token: str = Depends(oauth2_scheme)):
    from app.core.dependencies import get_current_user
    current_user = await get_current_user(token)
    return {"valid": True, "username": current_user.name}