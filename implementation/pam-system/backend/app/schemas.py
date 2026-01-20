from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RegisterRequest(BaseModel):
    email: str
    password: str
    is_admin: Optional[bool] = False


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class MfaSetupResponse(BaseModel):
    secret: str
    otpauth_url: str


class MfaEnableRequest(BaseModel):
    code: str


class AssetCreate(BaseModel):
    name: str
    host: str
    port: int
    type: str = "ssh"


class AssetResponse(BaseModel):
    id: int
    name: str
    host: str
    port: int
    type: str
    created_at: datetime


class CredentialCreate(BaseModel):
    username: str
    password: str


class RoleResponse(BaseModel):
    id: int
    name: str


class JitRequestCreate(BaseModel):
    asset_id: int
    role_id: int
    reason: str
    duration_minutes: int = Field(gt=0)


class JitRequestResponse(BaseModel):
    id: int
    user_id: int
    asset_id: int
    role_id: int
    reason: str
    duration_minutes: int
    status: str
    approved_by: Optional[int]
    created_at: datetime
    expires_at: Optional[datetime]


class SessionStartRequest(BaseModel):
    jit_request_id: int


class SessionResponse(BaseModel):
    id: int
    jit_request_id: int
    started_at: datetime
    ended_at: Optional[datetime]
    recording_path: Optional[str]
    status: str


class AuditEventResponse(BaseModel):
    id: int
    actor_id: Optional[int]
    action: str
    resource_type: str
    resource_id: str
    ts: datetime
    ip: Optional[str]
    metadata_json: Optional[dict]


class CommandLogEntry(BaseModel):
    ts: float
    line: str


class AuditPageResponse(BaseModel):
    items: List[AuditEventResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class RoleListResponse(BaseModel):
    roles: List[RoleResponse]
