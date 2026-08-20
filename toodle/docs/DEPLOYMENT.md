# Toodle deployment and recovery runbook

This runbook is provider-neutral. Use a container host that supports four services
(frontend, BFF, backend, and PostgreSQL), HTTPS, private service networking,
persistent storage, health checks, and secret injection. Prefer managed PostgreSQL
over running the database container in production.

## Required configuration

Store these values in the host's secret manager, never in Git:

- `DATABASE_URL`, `DATABASE_USERNAME`, and `DATABASE_PASSWORD` for Spring;
- `JWT_SECRET`, generated randomly and long enough for HMAC-SHA-256;
- `SPRING_API_URL` and `SPRING_HEALTH_URL` on the private network;
- `FRONTEND_ORIGIN`, set to the public HTTPS origin;
- `VITE_API_URL`, normally `/api` when the frontend proxies to the BFF.

Restrict PostgreSQL to the backend's private network. Only the frontend HTTPS port
should be public. Configure the BFF to accept only the exact production frontend
origin.

## Release procedure

1. Create an encrypted PostgreSQL backup and record the current image tags.
2. Let the Toodle GitHub Actions workflow test the proposed commit.
3. Build immutable images tagged with the Git commit SHA.
4. Deploy PostgreSQL connectivity and the backend first. Flyway applies new
   migrations when Spring starts.
5. Wait for the backend readiness check, then deploy the BFF and frontend.
6. Keep the previous image tags available until verification is complete.
7. Run the smoke checks below before sending user traffic to the release.

Never edit an applied Flyway migration. Database changes require a new migration
that remains compatible with the previous application version during rollout.

## Smoke checks

- HTTPS redirects and certificates work without warnings.
- Backend and BFF health endpoints report healthy.
- A new user can register, sign in, and sign out.
- A user can create, edit, complete, and delete a task and category.
- Tasks remain after restarting application containers.
- One user cannot read or modify another user's records.
- Invalid and expired tokens return `401`.
- Responses include `X-Correlation-Id`; an error's request ID can be found in BFF
  and Spring logs.

## Application rollback

If smoke checks fail, stop routing new traffic to the release and retain its logs.
Redeploy the previously recorded frontend, BFF, and backend image tags. Do not roll
back the database merely because application images were rolled back; migrations
must be designed so the previous application remains usable during the release.

After rollback, repeat health, login, persistence, and user-isolation checks. Record
the failed commit SHA and request IDs before investigating.

## Database recovery

Configure automated encrypted backups and point-in-time recovery with retention
appropriate for the data. Test restoration into an isolated database before launch
and periodically afterward.

For a real recovery, place the application in maintenance mode, preserve the
damaged database, and restore into a new database instance. Validate Flyway history,
row counts, login, task ownership, and recent records before changing the backend's
database connection. Keep the old instance until the recovery is accepted.

Document the provider-specific backup command, restore command, retention period,
recovery-point objective, recovery-time objective, and responsible person before
production launch.
