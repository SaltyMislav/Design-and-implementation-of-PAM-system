# Testing Notes

## Manual smoke test
1. `docker compose up --build`
2. Run seed script to create demo users and assets.
3. Login as admin and verify assets list and approvals queue.
4. Login as user, request JIT access, then approve as admin.
5. Start session, run a few commands, disconnect.
6. Replay session from Sessions page.

## Known gaps
- No automated tests included for this MVP.
- Recording playback is best-effort and depends on client timing.
