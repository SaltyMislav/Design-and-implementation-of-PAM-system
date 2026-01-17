from typing import Callable, List

import pyotp
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db import get_db
from app.models import Role, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _get_user_roles(db: Session, user: User) -> List[str]:
    roles = db.query(Role.name).join(Role.users).filter(User.id == user.id).all()
    return [role.name for role in roles]


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_auth(user: User = Depends(get_current_user)) -> User:
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user


def require_role(role_name: str) -> Callable:
    def _require_role(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        roles = _get_user_roles(db, user)
        if role_name not in roles and not user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing role")
        return user

    return _require_role


def require_admin_mfa(
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    x_mfa_totp: str | None = Header(default=None, alias="X-MFA-TOTP"),
) -> User:
    if not user.mfa_enabled or not user.mfa_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MFA not enabled")
    if not x_mfa_totp:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MFA code required")
    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(x_mfa_totp, valid_window=1):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid MFA code")
    return user
