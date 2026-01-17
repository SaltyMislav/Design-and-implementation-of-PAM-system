# Running the PAM Prototype

This repo contains thesis materials plus a runnable PAM MVP under `implementation/pam-system`.

## Quick Start (WSL2 + Docker Desktop)
1. Open WSL Ubuntu and clone/run the repo from your WSL home (not `/mnt/c`).
2. Start the stack:
   ```bash
   cd ~/Design-and-implementation-of-PAM-system/implementation/pam-system
   cp .env.example .env
   docker compose up --build
   ```
3. Seed demo data in another WSL terminal:
   ```bash
   cd ~/Design-and-implementation-of-PAM-system/implementation/pam-system
   ./infra/seed.sh
   ```
4. Open:
   - Frontend: http://localhost:5173
   - Backend docs: http://localhost:8000/docs
   - Vault UI: http://localhost:8200

For full Windows-specific setup details and the demo walkthrough, see `implementation/pam-system/README.md`.
