from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models import AuditEvent


def create_audit_event(
    db: Session,
    actor_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: str,
    ip: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    event = AuditEvent(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        ip=ip,
        metadata_json=metadata,
    )
    db.add(event)
    db.commit()
