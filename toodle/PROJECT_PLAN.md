# Toodle Project Plan

_Last updated: August 23, 2026_

## Goal

Build a secure and reliable task application that is ready for real users. Keep the current four-part design: React, Express BFF, Spring Boot, and PostgreSQL.

## Current progress

The local application, API contract, database tests, update protection, security tests, accessibility review, frontend data handling, tracing, production Docker checks, and local performance benchmark are complete.

The cloud configuration is ready but has not been deployed. The project truthfully claims production-ready configuration, not a live production deployment.

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
- [x] Run a manual Lighthouse and WCAG review before release.

### 6. Frontend data handling

- [x] Use TanStack Query for server data.
- [x] Show loading, empty, success, and error states.
- [x] Refresh stale data and handle failed changes safely.
- [x] Keep Redux out unless the project later needs it.

### 7. Local performance benchmark

- [x] Run the complete Docker/PostgreSQL stack locally.
- [x] Seed 500 tasks and eight categories through the real API path.
- [x] Measure p50, p95, throughput, failures, and concurrent behavior.
- [x] Profile the owner-scoped PostgreSQL query with `EXPLAIN ANALYZE`.
- [x] Save reproducible benchmark code and machine-readable results.
- [x] Use the evidence to optimize trace export instead of guessing.
- [x] Rerun the same workload and record the before/after result.

Measured local result with 20 concurrent clients for 30 seconds: throughput improved from 8.61 to 12.16 requests/second (41.23%), and p95 fell from 5,019 ms to 2,647 ms (47.27%), with zero failed requests. PostgreSQL executed the profiled 500-row query in 3.07 ms.

## Remaining deployment work

### 8. Cloud deployment

- [x] Choose Render and Render PostgreSQL.
- [x] Deploy automatically only after GitHub checks pass.
- [x] Configure TLS, secrets, CORS, migrations, and health checks.
- [ ] Test login, tasks, persistence, and user separation online.
- [x] Write rollback and recovery instructions.

### 9. Tracing

- [x] Keep one request ID through the browser, BFF, and Spring.
- [x] Add OpenTelemetry.
- [x] Record request and database timing.
- [x] Keep passwords, tokens, and private data out of traces.

### 10. Infrastructure as code

- [x] Define Render resources in `render.yaml`.
- [x] Keep secrets outside source files.
- [x] Document how to create, change, and remove the cloud environment.

## Resume version

**Toodle | Full-Stack Task and Calendar Application**
React, TypeScript, TanStack Query, Express, Spring Boot, PostgreSQL, Docker, OpenTelemetry, Playwright, Testcontainers, GitHub Actions, Render

- Built a secure full-stack task and calendar application with JWT authentication, user-owned data, categories, day/week/month views, and conflict-safe task editing.
- Designed a four-part system with a React frontend, Express backend-for-frontend, Spring Boot REST API, and PostgreSQL database managed with Flyway migrations.
- Generated and checked TypeScript API types from Spring OpenAPI output to prevent frontend and backend contract drift in continuous integration.
- Added PostgreSQL integration tests with Testcontainers, security boundary tests, accessible component checks with axe, and keyboard workflow tests with Playwright.
- Added end-to-end request IDs and sampled OpenTelemetry tracing for BFF, API, and database timing while excluding passwords, tokens, and private values.
- Load-tested the production-style Docker stack with 500 seeded tasks and 20 concurrent clients; increased throughput 41% and reduced p95 latency 47% by sampling traces and removing unused telemetry export.
- Prepared production Docker images, health checks, secret-based configuration, rollback instructions, and Render infrastructure as code with deployment gated by GitHub checks.
- Achieved Lighthouse scores of 100 for Accessibility, Best Practices, and final SEO, and corrected responsive mobile and production caching issues found during review.

## Optional later work

### 11. Live updates

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
