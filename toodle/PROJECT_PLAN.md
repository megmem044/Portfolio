# Toodle Project Plan

_Last updated: August 19, 2026_

## Goal

Build a secure and reliable task application that is ready for real users. Keep the current four-part design: React, Express BFF, Spring Boot, and PostgreSQL.

## Current progress

The local application, API contract, database tests, update protection, security tests, accessibility automation, and frontend data handling are complete.

The next major step is cloud deployment.

## Completed

### 1. Shared API contract

- [x] Create OpenAPI JSON from Spring.
- [x] Generate and check BFF TypeScript types.
- [x] Check contract changes in CI.
- [x] Document compatibility rules.

### 2. Real PostgreSQL tests

- [x] Run Spring integration tests with Testcontainers.
- [x] Run Flyway migrations in the test database.
- [x] Test the API and database together.
- [x] Keep small unit tests where a database is unnecessary.

### 3. Safe task updates

- [x] Add a version number to each task.
- [x] Send the version through the API.
- [x] Return `409 Conflict` for an old edit.
- [x] Refresh the frontend and explain how to retry.
- [x] Test two clients editing the same task.

### 4. Security

- [x] Test missing, invalid, and expired tokens.
- [x] Test that users cannot access each other's data.
- [x] Reject malformed requests and blocked fields.
- [x] Check password hashing, token expiry, CORS, validation, and headers.
- [x] Require production secrets from environment variables.

### 5. Accessibility automation

- [x] Run axe checks in component tests.
- [x] Test an important keyboard workflow with Playwright.
- [x] Test labels, dialogs, focus, errors, and keyboard order.
- [ ] Run a manual Lighthouse and WCAG review before release.

### 6. Frontend data handling

- [x] Use TanStack Query for server data.
- [x] Show loading, empty, success, and error states.
- [x] Refresh stale data and handle failed changes safely.
- [x] Keep Redux out unless the project later needs it.

## Next

### 7. Cloud deployment

- [ ] Choose a cloud host and managed PostgreSQL provider.
- [ ] Make GitHub Actions publish images and deploy them.
- [ ] Configure TLS, secrets, CORS, migrations, and health checks.
- [ ] Test login, tasks, persistence, and user separation online.
- [x] Write rollback and recovery instructions.

### 8. Tracing

- [x] Keep one request ID through the browser, BFF, and Spring.
- [ ] Add OpenTelemetry.
- [ ] Record request and database timing.
- [ ] Keep passwords, tokens, and private data out of traces.

### 9. Infrastructure as code

- [ ] Define cloud resources with Terraform.
- [ ] Keep secrets and environment values outside Terraform source files.
- [ ] Document how to create, change, and remove the cloud environment.

## Optional later work

### 10. Live updates

- [ ] Decide whether SSE or WebSockets would improve the application.
- [ ] Update another open tab when a task changes.
- [ ] Test reconnection and duplicate events.

This work is optional and must not delay deployment.

## Keep the project focused

Do not add extra microservices, Redis, Kafka, Kubernetes, another database, machine learning, or Redux without a real product need.

Do not edit old Flyway migrations. Add a new migration for every database change.

## Release check

Before release:

1. Run all backend, BFF, frontend, and Playwright tests.
2. Build all production Docker images.
3. Run the manual Lighthouse and WCAG review.
4. Manually test login, tasks, categories, calendar views, keyboard use, errors, persistence, user separation, and health checks.
5. Confirm the documentation matches the deployed application.

The modernization is complete when all required boxes above are checked and the cloud deployment works.
