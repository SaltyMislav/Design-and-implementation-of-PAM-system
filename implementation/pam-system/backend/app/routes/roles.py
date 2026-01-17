from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_auth
from app.db import get_db
from app.models import Role
from app.schemas import RoleResponse

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RoleResponse])
def list_roles(user=Depends(require_auth), db: Session = Depends(get_db)) -> list[RoleResponse]:
    roles = db.query(Role).order_by(Role.name).all()
    return [RoleResponse(id=role.id, name=role.name) for role in roles]
