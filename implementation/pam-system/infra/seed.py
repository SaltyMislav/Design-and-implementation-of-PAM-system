import os
import sys

sys.path.append("/app")

import pyotp
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db import SessionLocal, run_migrations
from app.models import Asset, Credential, Role, User, UserRole
from app.vault import ensure_kv_v2_mount, write_kv2

ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "Admin123!")
USER_EMAIL = os.getenv("SEED_USER_EMAIL", "user@example.com")
USER_PASSWORD = os.getenv("SEED_USER_PASSWORD", "User123!")


def get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if not role:
        role = Role(name=name)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


def main() -> None:
    run_migrations()
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=ADMIN_EMAIL,
                password_hash=get_password_hash(ADMIN_PASSWORD),
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        user = db.query(User).filter(User.email == USER_EMAIL).first()
        if not user:
            user = User(
                email=USER_EMAIL,
                password_hash=get_password_hash(USER_PASSWORD),
                is_admin=False,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        sysadmin = get_or_create_role(db, "SysAdmin")
        dba = get_or_create_role(db, "DBA")

        if not db.query(UserRole).filter(UserRole.user_id == user.id, UserRole.role_id == sysadmin.id).first():
            db.add(UserRole(user_id=user.id, role_id=sysadmin.id))
            db.commit()

        asset = db.query(Asset).filter(Asset.name == "Demo SSH").first()
        if not asset:
            asset = Asset(name="Demo SSH", host="ssh-target", port=2222, type="ssh")
            db.add(asset)
            db.commit()
            db.refresh(asset)

        ensure_kv_v2_mount()
        vault_path = f"assets/{asset.id}"
        write_kv2(vault_path, {"username": "demo", "password": "demo123"})

        credential = db.query(Credential).filter(Credential.asset_id == asset.id).first()
        if not credential:
            credential = Credential(asset_id=asset.id, vault_path=vault_path)
            db.add(credential)
            db.commit()

        if not admin.mfa_secret:
            admin.mfa_secret = pyotp.random_base32()
            admin.mfa_enabled = True
            db.add(admin)
            db.commit()

        totp = pyotp.TOTP(admin.mfa_secret)
        print("Seed complete.")
        print(f"Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"User: {USER_EMAIL} / {USER_PASSWORD}")
        print("Admin MFA secret (add to authenticator):")
        print(admin.mfa_secret)
        print("Admin MFA current code:")
        print(totp.now())
    finally:
        db.close()


if __name__ == "__main__":
    main()
