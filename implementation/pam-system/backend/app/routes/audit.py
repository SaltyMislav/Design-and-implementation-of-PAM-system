from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import String, cast, func, or_
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db import get_db
from app.models import AuditEvent
from app.schemas import AuditEventResponse, AuditPageResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditPageResponse)
def list_audit_events(
    user=Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
    resource_type: Optional[str] = Query(default=None),
    sort: str = Query(default="ts_desc"),
) -> AuditPageResponse:
    query = db.query(AuditEvent)

    if action:
        query = query.filter(AuditEvent.action == action)
    if resource_type:
        query = query.filter(AuditEvent.resource_type == resource_type)
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(AuditEvent.action).ilike(term),
                func.lower(AuditEvent.resource_type).ilike(term),
                func.lower(AuditEvent.resource_id).ilike(term),
                func.lower(cast(AuditEvent.actor_id, String)).ilike(term),
                func.lower(cast(AuditEvent.ip, String)).ilike(term),
                func.lower(cast(AuditEvent.metadata_json, String)).ilike(term),
            )
        )

    if sort == "ts_asc":
        query = query.order_by(AuditEvent.ts.asc())
    elif sort == "action_asc":
        query = query.order_by(AuditEvent.action.asc())
    elif sort == "action_desc":
        query = query.order_by(AuditEvent.action.desc())
    elif sort == "resource_asc":
        query = query.order_by(AuditEvent.resource_type.asc())
    elif sort == "resource_desc":
        query = query.order_by(AuditEvent.resource_type.desc())
    else:
        query = query.order_by(AuditEvent.ts.desc())

    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = min(page, total_pages)
    events = (
        query.offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        AuditEventResponse(
            id=event.id,
            actor_id=event.actor_id,
            action=event.action,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            ts=event.ts,
            ip=event.ip,
            metadata_json=event.metadata_json,
        )
        for event in events
    ]

    return AuditPageResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )
