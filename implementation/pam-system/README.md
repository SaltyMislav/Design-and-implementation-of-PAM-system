# PAM Prototype (Windows + WSL2)

This is a self-contained PAM MVP running in Linux containers with Docker Desktop + WSL2. All commands are intended to be run from **WSL Ubuntu**.

## Running on Windows (WSL2 + Docker Desktop)

### 1) Enable WSL2
1. Open PowerShell as Administrator.
2. Run:
   ```powershell
   wsl --install
   ```
3. Reboot if prompted, then open Ubuntu from the Start menu.

### 2) Install Docker Desktop
1. Download and install Docker Desktop from https://www.docker.com/products/docker-desktop
2. In Docker Desktop: Settings -> Resources -> WSL Integration -> enable your Ubuntu distro.
3. Restart Docker Desktop.

### 3) Clone inside WSL (not /mnt/c)
```bash
cd ~
# example path; use your existing repo location if already cloned in WSL
cd ~/Design-and-implementation-of-PAM-system/implementation/pam-system
```

### 4) Run
```bash
cd implementation/pam-system
cp .env.example .env
# update secrets in .env if desired

docker compose up --build
```

Open:
- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs
- Vault UI (dev): http://localhost:8200

### Common Windows Troubleshooting
- **Line endings**: keep LF endings. This repo includes `.gitattributes` to enforce LF.
- **Permissions**: run everything inside WSL; avoid `/mnt/c` mounts.
- **Port conflicts**: edit `docker-compose.yml` to change host ports (e.g., `5173:5173`).
- **WSL integration**: ensure Docker Desktop -> Settings -> Resources -> WSL Integration is enabled.

## Demo Script (Seed + Walkthrough)
1. Start services:
   ```bash
   docker compose up --build
   ```
2. Seed demo data (admin + user + roles + asset + Vault credential):
   ```bash
   ./infra/seed.sh
   ```
3. Login as admin (from seed output) and verify MFA secret.
4. Login as user and submit a JIT request.
5. Login as admin, approve the request (MFA required).
6. Login as user, start session, run a few commands.
7. View replay from the Sessions list.

## Services
- `frontend`: React + Vite UI
- `backend`: FastAPI API service
- `gateway`: WebSocket SSH proxy + recorder
- `postgres`: data store
- `vault`: dev mode KV v2 secrets
- `ssh-target`: demo SSH host on port 2222

## Notes
- Admin MFA is required for asset/credential management and JIT approvals.
- Session recording is JSON lines with base64 output in `/data/recordings` (shared volume).
- Command log is best-effort based on input line breaks.
