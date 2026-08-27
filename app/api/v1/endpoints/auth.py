from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.core.security import create_access_token
from app.crud.crud_user import user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.schemas.token import Token

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    response_description="Returns the newly created user profile (without password).",
)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db),
):
    """
    User Registration:
    1. Validates that email is unique.
    2. Hashes password using bcrypt.
    3. Persists new user in MySQL.
    4. Returns serialized user profile.
    """
    existing_user = user_crud.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    user = user_crud.create(db, obj_in=user_in)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login for Access Token (Form or Swagger)",
    response_description="Returns Bearer JWT access token upon successful authentication.",
)
def login_for_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token login, used by Swagger UI:
    - `username` contains the user's email address.
    - `password` contains the plaintext password.
    """
    user = user_crud.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account.",
        )

    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    }


@router.post(
    "/login/json",
    response_model=Token,
    summary="Login for Access Token (JSON Body)",
    response_description="Returns Bearer JWT access token upon successful authentication.",
)
def login_with_json(
    login_data: UserLogin,
    db: Session = Depends(deps.get_db),
):
    """
    JSON-based login endpoint for frontend/mobile clients sending JSON payloads.
    """
    user = user_crud.authenticate(db, email=login_data.email, password=login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account.",
        )

    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    }


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
    response_description="Returns profile information for the authenticated user.",
)
def get_me(
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Protected Endpoint:
    - Decodes JWT token in Authorization header.
    - Validates user existence and active status.
    - Returns current user details.
    """
    return current_user
