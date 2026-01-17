from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import create_audit_event
from app.core.deps import require_admin_mfa, require_auth
from app.db import get_db
from app.models import Asset, Credential
from app.schemas import AssetCreate, AssetResponse, CredentialCreate
from app.vault import ensure_kv_v2_mount, write_kv2

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=AssetResponse)
def create_asset(
    payload: AssetCreate,
    request: Request,
    user=Depends(require_admin_mfa),
    db: Session = Depends(get_db),
) -> AssetResponse:
    asset = Asset(
        name=payload.name,
        host=payload.host,
        port=payload.port,
        type=payload.type,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    create_audit_event(
        db,
        actor_id=user.id,
        action="asset_create",
        resource_type="asset",
        resource_id=asset.id,
        ip=request.client.host if request.client else None,
    )
    return AssetResponse(
        id=asset.id,
        name=asset.name,
        host=asset.host,
        port=asset.port,
        type=asset.type,
        created_at=asset.created_at,
    )


@router.get("", response_model=list[AssetResponse])
def list_assets(user=Depends(require_auth), db: Session = Depends(get_db)) -> list[AssetResponse]:
    assets = db.query(Asset).all()
    return [
        AssetResponse(
            id=asset.id,
            name=asset.name,
            host=asset.host,
            port=asset.port,
            type=asset.type,
            created_at=asset.created_at,
        )
        for asset in assets
    ]


@router.post("/{asset_id}/credential")
def create_credential(
    asset_id: int,
    payload: CredentialCreate,
    request: Request,
    user=Depends(require_admin_mfa),
    db: Session = Depends(get_db),
) -> dict:
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    ensure_kv_v2_mount()
    vault_path = f"assets/{asset_id}"
    write_kv2(vault_path, {"username": payload.username, "password": payload.password})
    existing = db.query(Credential).filter(Credential.asset_id == asset_id).first()
    if existing:
        existing.vault_path = vault_path
        db.add(existing)
    else:
        credential = Credential(asset_id=asset_id, vault_path=vault_path)
        db.add(credential)
    db.commit()
    create_audit_event(
        db,
        actor_id=user.id,
        action="credential_write",
        resource_type="asset",
        resource_id=asset_id,
        ip=request.client.host if request.client else None,
    )
    return {"vault_path": vault_path}
