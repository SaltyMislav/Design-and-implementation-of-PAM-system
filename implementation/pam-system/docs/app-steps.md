# In-App Demo Steps (After Frontend Loads)

Use this to replicate the full demo flow.

## Prerequisites
1. Start stack:
   ```bash
   cd ~/Design-and-implementation-of-PAM-system/implementation/pam-system
   docker compose up --build
   ```
2. Seed demo data (prints credentials + MFA secret):
   ```bash
   ./infra/seed.sh
   ```

## Demo Flow
1. Login as admin (use seed output credentials).
2. Go to **Admin MFA**:
   - Click **Generate Secret**.
   - Scan the QR (or copy the secret) into an authenticator app.
   - Enter a TOTP code and click **Enable MFA**.
3. (Optional if seeded) Go to **Assets**:
   - Create asset: host `ssh-target`, port `2222`.
   - Store credential: username `demo`, password `demo123`.
4. Logout, login as user (use seed output credentials).
5. Go to **Request Access**:
   - Select asset + role (e.g., SysAdmin), add reason + duration.
   - Submit JIT request.
6. Logout, login as admin.
7. Go to **Approvals**:
   - Enter MFA code.
   - Approve the pending request.
8. Logout, login as user.
9. Go to **Sessions**:
   - Click **Start** on the approved request.
   - Use the web terminal.
10. Close the session, return to **Sessions**:
    - Click **Replay** to view the recording.

## Notes
- If assets or roles are missing, rerun `./infra/seed.sh` and refresh the page.
- Recordings are stored in `/data/recordings` (Docker volume).
