import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.security import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid or expired token", headers = {"WWW-Authenticate": "Bearer"} ,)

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except(jwt.PyJWTError, KeyError, ValueError):
        raise credentials_error

    if payload.get("type")!="access":
        raise credentials_error
    
    user = db.get(User, user_id)
    if user is None:
        raise credentials_error
    return user

def require_role(*allowed_roles: UserRole):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to do this",)
        return current_user
    return checker

