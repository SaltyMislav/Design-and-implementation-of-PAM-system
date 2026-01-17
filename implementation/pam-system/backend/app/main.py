from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import SessionLocal, run_migrations
from app.models import JitRequest
from app.routes import assets, audit, auth, jit, roles, sessions

app = FastAPI(title="PAM Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(jit.router)
app.include_router(sessions.router)
app.include_router(audit.router)
app.include_router(roles.router)

scheduler = BackgroundScheduler()


def expire_jit_requests() -> None:
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        expired = (
            db.query(JitRequest)
            .filter(JitRequest.status == "APPROVED")
            .filter(JitRequest.expires_at.isnot(None))
            .filter(JitRequest.expires_at < now)
            .all()
        )
        for jit_request in expired:
            jit_request.status = "EXPIRED"
            db.add(jit_request)
        if expired:
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    run_migrations()
    scheduler.add_job(expire_jit_requests, "interval", minutes=1)
    scheduler.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    scheduler.shutdown()
