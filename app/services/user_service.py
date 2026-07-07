import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.security import get_password_hash, verify_password
from app.models.user_model import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import RegisterRequest


logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def register_user(self, payload: RegisterRequest) -> User:
        email = str(payload.email).lower()

        if self.repository.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists.",
            )

        user = User(
            name=payload.name,
            email=email,
            hashed_password=get_password_hash(payload.password),
        )

        try:
            created_user = self.repository.create(user)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists.",
            ) from exc

        logger.info(
            "user_registered",
            extra={"user_id": created_user.id, "email": created_user.email},
        )
        return created_user

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.repository.get_by_email(email.lower())

        if not user or not verify_password(password, user.hashed_password):
            logger.info("login_failed", extra={"email": email.lower()})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user.",
            )

        logger.info("login_success", extra={"user_id": user.id})
        return user
