from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import create_audit_event
from app.core.deps import require_admin_mfa, require_auth
from app.db import get_db
from app.models import JitRequest, User
from app.schemas import JitRequestCreate, JitRequestResponse

router = APIRouter(prefix="/jit-requests", tags=["jit"])


@router.post("", response_model=JitRequestResponse)
def create_jit_request(
    payload: JitRequestCreate,
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> JitRequestResponse:
    jit = JitRequest(
        user_id=user.id,
        asset_id=payload.asset_id,
        role_id=payload.role_id,
        reason=payload.reason,
        duration_minutes=payload.duration_minutes,
        status="PENDING",
    )
    db.add(jit)
    db.commit()
    db.refresh(jit)
    create_audit_event(
        db,
        actor_id=user.id,
        action="jit_request",
        resource_type="jit_request",
        resource_id=jit.id,
        ip=request.client.host if request.client else None,
    )
    return JitRequestResponse(
        id=jit.id,
        user_id=jit.user_id,
        asset_id=jit.asset_id,
        role_id=jit.role_id,
        reason=jit.reason,
        duration_minutes=jit.duration_minutes,
        status=jit.status,
        approved_by=jit.approved_by,
        created_at=jit.created_at,
        expires_at=jit.expires_at,
    )


@router.get("", response_model=list[JitRequestResponse])
def list_jit_requests(user: User = Depends(require_auth), db: Session = Depends(get_db)) -> list[JitRequestResponse]:
    query = db.query(JitRequest)
    if not user.is_admin:
        query = query.filter(JitRequest.user_id == user.id)
    jit_requests = query.order_by(JitRequest.created_at.desc()).all()
    return [
        JitRequestResponse(
            id=jit.id,
            user_id=jit.user_id,
            asset_id=jit.asset_id,
            role_id=jit.role_id,
            reason=jit.reason,
            duration_minutes=jit.duration_minutes,
            status=jit.status,
            approved_by=jit.approved_by,
            created_at=jit.created_at,
            expires_at=jit.expires_at,
        )
        for jit in jit_requests
    ]


@router.post("/{jit_id}/approve", response_model=JitRequestResponse)
def approve_jit_request(
    jit_id: int,
    request: Request,
    user: User = Depends(require_admin_mfa),
    db: Session = Depends(get_db),
) -> JitRequestResponse:
    jit = db.query(JitRequest).filter(JitRequest.id == jit_id).first()
    if not jit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="JIT request not found")
    if jit.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="JIT request already processed")
    jit.status = "APPROVED"
    jit.approved_by = user.id
    jit.expires_at = datetime.utcnow() + timedelta(minutes=jit.duration_minutes)
    db.add(jit)
    db.commit()
    create_audit_event(
        db,
        actor_id=user.id,
        action="jit_approve",
        resource_type="jit_request",
        resource_id=jit.id,
        ip=request.client.host if request.client else None,
    )
    return JitRequestResponse(
        id=jit.id,
        user_id=jit.user_id,
        asset_id=jit.asset_id,
        role_id=jit.role_id,
        reason=jit.reason,
        duration_minutes=jit.duration_minutes,
        status=jit.status,
        approved_by=jit.approved_by,
        created_at=jit.created_at,
        expires_at=jit.expires_at,
    )


@router.post("/{jit_id}/deny", response_model=JitRequestResponse)
def deny_jit_request(
    jit_id: int,
    request: Request,
    user: User = Depends(require_admin_mfa),
    db: Session = Depends(get_db),
) -> JitRequestResponse:
    jit = db.query(JitRequest).filter(JitRequest.id == jit_id).first()
    if not jit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="JIT request not found")
    if jit.status != "PENDING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="JIT request already processed")
    jit.status = "DENIED"
    jit.approved_by = user.id
    db.add(jit)
    db.commit()
    create_audit_event(
        db,
        actor_id=user.id,
        action="jit_deny",
        resource_type="jit_request",
        resource_id=jit.id,
        ip=request.client.host if request.client else None,
    )
    return JitRequestResponse(
        id=jit.id,
        user_id=jit.user_id,
        asset_id=jit.asset_id,
        role_id=jit.role_id,
        reason=jit.reason,
        duration_minutes=jit.duration_minutes,
        status=jit.status,
        approved_by=jit.approved_by,
        created_at=jit.created_at,
        expires_at=jit.expires_at,
    )
