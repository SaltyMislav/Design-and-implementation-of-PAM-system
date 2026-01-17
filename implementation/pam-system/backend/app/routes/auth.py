from typing import Any

import pyotp
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core import security
from app.core.audit import create_audit_event
from app.core.config import settings
from app.core.deps import get_current_user, require_admin
from app.db import get_db
from app.models import Role, User
from app.schemas import (
    LoginRequest,
    MfaEnableRequest,
    MfaSetupResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_payload(db: Session, user: User) -> dict[str, Any]:
    roles = db.query(Role.name).join(Role.users).filter(User.id == user.id).all()
    role_names = [role.name for role in roles]
    return {
        "id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "mfa_enabled": user.mfa_enabled,
        "roles": role_names,
    }


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    is_admin = payload.is_admin if settings.ALLOW_ADMIN_REGISTRATION else False
    user = User(
        email=payload.email,
        password_hash=security.get_password_hash(payload.password),
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = security.create_access_token(str(user.id))
    refresh_token = security.create_refresh_token(str(user.id))
    create_audit_event(
        db,
        actor_id=user.id,
        action="register",
        resource_type="user",
        resource_id=user.id,
        ip=request.client.host if request.client else None,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=_user_payload(db, user),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not security.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = security.create_access_token(str(user.id))
    refresh_token = security.create_refresh_token(str(user.id))
    create_audit_event(
        db,
        actor_id=user.id,
        action="login",
        resource_type="user",
        resource_id=user.id,
        ip=request.client.host if request.client else None,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=_user_payload(db, user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        claims = security.decode_refresh_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if claims.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user = db.query(User).filter(User.id == int(claims.get("sub", 0))).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    access_token = security.create_access_token(str(user.id))
    refresh_token = security.create_refresh_token(str(user.id))
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=_user_payload(db, user),
    )


@router.post("/mfa/setup", response_model=MfaSetupResponse)
def mfa_setup(
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> MfaSetupResponse:
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    user.mfa_enabled = False
    db.add(user)
    db.commit()
    totp = pyotp.TOTP(secret)
    otpauth_url = totp.provisioning_uri(name=user.email, issuer_name="PAM Demo")
    return MfaSetupResponse(secret=secret, otpauth_url=otpauth_url)


@router.post("/mfa/enable")
def mfa_enable(
    payload: MfaEnableRequest,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    request: Request = None,
) -> dict:
    if not user.mfa_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not initialized")
    totp = pyotp.TOTP(user.mfa_secret)
    if not totp.verify(payload.code, valid_window=1):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA code")
    user.mfa_enabled = True
    db.add(user)
    db.commit()
    create_audit_event(
        db,
        actor_id=user.id,
        action="mfa_enable",
        resource_type="user",
        resource_id=user.id,
        ip=request.client.host if request and request.client else None,
    )
    return {"status": "enabled"}
