# PAM Prototype Architecture

## Components
- Frontend (Vite + React): UI for login, JIT requests, approvals, sessions, and terminal replay.
- Backend (FastAPI): Auth, RBAC, MFA, asset/JIT/session management, audit logging.
- Gateway (FastAPI + Paramiko): WebSocket SSH proxy and recorder.
- Postgres: State + audit data.
- Vault (dev mode): KV v2 storage for privileged credentials.
- Demo SSH target: Linux container reachable on port 2222.

## Flow
1. Admin creates assets and stores credentials in Vault (backend writes to KV v2).
2. User submits JIT request for a role + asset.
3. Admin approves with MFA; backend sets expiry.
4. User starts session; backend issues short-lived gateway token.
5. Gateway validates token, fetches secret from Vault, and proxies SSH over WebSocket.
6. Gateway stores recording log and command log in `/data/recordings`.
7. Backend serves recording for replay.

## Recording Format
- `recordings/session-<id>.log`: JSON lines of `{ts, data}` where `data` is base64-encoded terminal output.
- `recordings/session-<id>.cmd.log`: Best-effort command log based on raw input lines.

## Limitations
- Command parsing is heuristic: input lines are captured when a newline is sent.
- Session end detection relies on WebSocket disconnect or SSH channel close.
