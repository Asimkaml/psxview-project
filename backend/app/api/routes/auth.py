from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenPair, UserCreate, UserRead
from app.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair)
def register(data: UserCreate, db: Session = Depends(get_db)) -> TokenPair:
    service = AuthService(db)
    user, access_token, refresh_token = service.register(data)
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.from_orm(user),
    )


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    service = AuthService(db)
    user, access_token, refresh_token = service.login(
        email=payload.email, password=payload.password
    )
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.from_orm(user),
    )


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)) -> UserRead:
    return UserRead.from_orm(current_user)
