# Toodle Deployment

_Last updated: August 20, 2026_

## Prepared environment

`render.yaml` defines the complete Render environment:

- A private Spring Boot service.
- A public Express BFF.
- A static React site with HTTPS and security headers.
- A private managed PostgreSQL 16 database.
- A generated JWT signing secret.
- Health checks and deployment only after GitHub checks pass.

The blueprint uses paid resources so the application and database do not expire or sleep. Review Render's price estimate before approving it.

## Final deployment step

Do not perform this step until you are ready to create billable resources.

1. Sign in to Render and connect the GitHub account that can read `megmem044/Portfolio`.
2. Create a new Blueprint.
3. Select the `Portfolio` repository and `main` branch.
4. Set the Blueprint path to `toodle/render.yaml`.
5. Review the listed prices and resource names.
6. Click **Apply**.

Render will create the database first, then Spring, the BFF, and the frontend. Flyway runs the database migrations when Spring starts.

## Checks after deployment

1. Open `https://toodle-web-megmem044.onrender.com`.
2. Register two different accounts.
3. Create, edit, complete, and delete tasks and categories.
4. Confirm one account cannot access the other account's data.
5. Restart the services and confirm tasks remain in PostgreSQL.
6. Check `https://toodle-bff-megmem044.onrender.com/health` returns `200` with `UP`.
7. Run Lighthouse and complete the manual WCAG review.

## Rollback

1. Open the failed service in Render.
2. Choose **Rollback** and select the previous successful deploy.
3. Check the BFF health endpoint and the main task workflow.

Flyway migrations must remain backward compatible with the previous application release. If a migration needs correction, add a new migration instead of changing a migration that already ran.

## Recovery

- Application failure: roll back the affected service.
- Database failure: use Render PostgreSQL recovery tools or restore a backup.
- Exposed JWT secret: generate a new `JWT_SECRET`; existing sessions will be signed out.
- Exposed database password: rotate the database credentials and redeploy Spring.

Deleting the Blueprint does not delete its resources automatically. Remove services and the database separately in Render when tearing the environment down.
