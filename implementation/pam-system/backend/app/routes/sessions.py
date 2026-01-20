import json
import os
from collections import deque
from datetime import datetime

from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.audit import create_audit_event
from app.core.config import settings
from app.core.deps import require_auth
from app.core.security import create_gateway_token
from app.db import get_db
from app.models import Asset, Credential, JitRequest, Role, Session as SessionModel, User
from app.schemas import CommandLogEntry, SessionResponse, SessionStartRequest
from app.ws import manager

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _user_role_names(db: Session, user: User) -> set[str]:
    roles = db.query(Role.name).join(Role.users).filter(User.id == user.id).all()
    return {role.name for role in roles}


@router.post("/start")
async def start_session(
    payload: SessionStartRequest,
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> dict:
    jit = db.query(JitRequest).filter(JitRequest.id == payload.jit_request_id).first()
    if not jit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="JIT request not found")
    if jit.status != "APPROVED":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="JIT request not approved")
    if jit.expires_at and jit.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="JIT request expired")
    if not user.is_admin and jit.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your JIT request")
    role = db.query(Role).filter(Role.id == jit.role_id).first()
    if role and role.name not in _user_role_names(db, user) and not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing required role")
    asset = db.query(Asset).filter(Asset.id == jit.asset_id).first()
    credential = db.query(Credential).filter(Credential.asset_id == jit.asset_id).first()
    if not asset or not credential:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Asset or credential missing")
    session = SessionModel(
        jit_request_id=jit.id,
        status="ACTIVE",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    session.recording_path = f"recordings/session-{session.id}.log"
    db.add(session)
    db.commit()

    token_payload = {
        "session_id": session.id,
        "recording_path": session.recording_path,
        "vault_path": credential.vault_path,
        "asset_host": asset.host,
        "asset_port": asset.port,
        "user_id": user.id,
    }
    session_token = create_gateway_token(token_payload)
    create_audit_event(
        db,
        actor_id=user.id,
        action="session_start",
        resource_type="session",
        resource_id=session.id,
        ip=request.client.host if request.client else None,
    )
    create_audit_event(
        db,
        actor_id=user.id,
        action="vault_access",
        resource_type="credential",
        resource_id=credential.id,
        ip=request.client.host if request.client else None,
        metadata={"vault_path": credential.vault_path},
    )
    await manager.broadcast({"type": "session_started", "session_id": session.id})
    return {
        "session_id": session.id,
        "session_token": session_token,
        "websocket_url": settings.GATEWAY_PUBLIC_WS_URL,
    }


@router.get("", response_model=list[SessionResponse])
def list_sessions(user: User = Depends(require_auth), db: Session = Depends(get_db)) -> list[SessionResponse]:
    query = db.query(SessionModel)
    if not user.is_admin:
        query = query.join(JitRequest).filter(JitRequest.user_id == user.id)
    sessions = query.order_by(SessionModel.started_at.desc()).all()
    return [
        SessionResponse(
            id=session.id,
            jit_request_id=session.jit_request_id,
            started_at=session.started_at,
            ended_at=session.ended_at,
            recording_path=session.recording_path,
            status=session.status,
        )
        for session in sessions
    ]


@router.get("/{session_id}/recording")
def get_recording(
    session_id: int,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> Response:
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if not user.is_admin:
        jit = db.query(JitRequest).filter(JitRequest.id == session.jit_request_id).first()
        if not jit or jit.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if not session.recording_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not available")
    file_path = os.path.join("/data", session.recording_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording file missing")
    return FileResponse(file_path, media_type="text/plain")


@router.get("/{session_id}/commands", response_model=list[CommandLogEntry])
def get_command_log(
    session_id: int,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
    limit: int = Query(200, ge=1, le=1000),
) -> list[CommandLogEntry]:
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if not user.is_admin:
        jit = db.query(JitRequest).filter(JitRequest.id == session.jit_request_id).first()
        if not jit or jit.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    recording_name = os.path.basename(session.recording_path or "")
    if recording_name.endswith(".log"):
        base_name = recording_name[:-4]
    else:
        base_name = f"session-{session.id}"
    cmd_path = os.path.join("/data/recordings", f"{base_name}.cmd.log")
    if not os.path.exists(cmd_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Command log not available")
    entries = deque(maxlen=limit)
    with open(cmd_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "ts" in payload and "line" in payload:
                entries.append(CommandLogEntry(ts=payload["ts"], line=payload["line"]))
    return list(entries)


@router.post("/{session_id}/end")
async def end_session(
    session_id: int,
    request: Request,
    db: Session = Depends(get_db),
    x_gateway_api_key: str | None = Header(default=None, alias="X-Gateway-Api-Key"),
) -> dict:
    if x_gateway_api_key != settings.GATEWAY_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    session.status = "ENDED"
    session.ended_at = datetime.utcnow()
    db.add(session)
    db.commit()
    create_audit_event(
        db,
        actor_id=None,
        action="session_end",
        resource_type="session",
        resource_id=session.id,
        ip=request.client.host if request.client else None,
    )
    await manager.broadcast({"type": "session_ended", "session_id": session.id})
    return {"status": "ended"}
