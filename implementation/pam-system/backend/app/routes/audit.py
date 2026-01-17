from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db import get_db
from app.models import AuditEvent
from app.schemas import AuditEventResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditEventResponse])
def list_audit_events(user=Depends(require_admin), db: Session = Depends(get_db)) -> list[AuditEventResponse]:
    events = db.query(AuditEvent).order_by(AuditEvent.ts.desc()).limit(200).all()
    return [
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
