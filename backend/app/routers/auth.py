import jwt

from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.schemas import UserCreate, UserOut, LoginRequest, TokenOut
# from app.security import hash_password, verify_password, create_access_token
from app.security import (
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/auth",tags=["auth"])

@router.post("/signup", response_model = UserOut, status_code = status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "Email already registered",)
    user = User(
        name = payload.name,
        email = payload.email,
        password_hash = hash_password(payload.password),
        role = payload.role,
        company_name = payload.company_name if payload.role == UserRole.recruiter else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid email or password",)
    # token = create_access_token(user.id,user.role.value)
    response.set_cookie(
        key="refresh_token",
        value=create_refresh_token(user.id),
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/auth",
    )
    return {"access_token": create_access_token(user.id, user.role.value)}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh", response_model= TokenOut)
def refresh(refresh_token: str | None = Cookie(default = None), db: Session = Depends(get_db)):
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    if refresh_token is None:
        raise error
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise error
    if payload.get("type") != "refresh":
        raise error

    user = db.get(User, user_id)
    if user is None:
        raise error
    return {"access_token": create_access_token(user.id, user.role.value)}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(key="refresh_token", path="/auth")

# @router.get("/recruiter-check")
# def recruiter_check(user: User = Depends(require_role(UserRole.recruiter))):
#     return {"message": f"Hello recruiter {user.name}"}