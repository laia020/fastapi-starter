from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_current_user
from app.db.database import get_db
from app.models.user_model import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import RegisterRequest, TokenResponse
from app.schemas.user_schema import UserResponse
from app.services.user_service import UserService


router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
) -> UserService:
    return UserService(UserRepository(db))


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    return service.register_user(payload)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[UserService, Depends(get_user_service)],
) -> TokenResponse:
    user = service.authenticate_user(
        email=form_data.username,
        password=form_data.password,
    )
    token = create_access_token(user)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
