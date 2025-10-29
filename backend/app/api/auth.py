# Authentication API routes
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user_schema import UserCreate, UserResponse
from app.services import user_service
from app.core.security import create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: UserCreate):
    """新規ユーザー登録"""
    # ユーザー名の重複チェック
    existing_user = await user_service.get_by_username(payload.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = await user_service.create_user(payload)
    return user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """ログイン"""
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """現在のユーザー情報取得"""
    return current_user
