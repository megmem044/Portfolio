# Toodle project plan

_Last updated: August 15, 2026_

## Engineering goal

Modernize a legacy browser task manager into a secure, contract-driven, production-grade multi-tier application.

Toodle will keep its current architecture:

```text
React + TypeScript
        |
        v
Express BFF
        |
        v
Spring Boot API
        |
        v
PostgreSQL
```

The goal is to make this architecture reliable and well tested, not to add more services or unnecessary technology.

## What Toodle should demonstrate

- Strong Java and Spring Boot development.
- Clear API contracts between services.
- Secure authentication and owner-based authorization.
- Safe database migrations and concurrency handling.
- Accessible, responsive React interfaces.
- Testing with real infrastructure.
- Useful logging, tracing, CI, and cloud deployment.

## Current status

Already implemented:

- React and TypeScript frontend with day, week, and month views.
- Task and category CRUD, search, filters, and statistics.
- Express BFF between the browser and Spring API.
- Spring controllers, services, repositories, DTOs, validation, security, and JPA.
- PostgreSQL persistence with Flyway migrations.
- JWT authentication and owner-scoped data access.
- Structured API errors, health checks, and correlation IDs.
- Frontend, BFF, backend, and container checks in GitHub Actions.
- A production-shaped Docker Compose stack.

Not yet completed:

- OpenAPI contract and generated or validated TypeScript types.
- Testcontainers-based PostgreSQL integration tests.
- Optimistic locking and user-friendly conflict handling.
- Automated accessibility checks.
- Dedicated frontend server-state management.
- Cloud deployment, distributed tracing, and infrastructure as code.

## Priorities

### 1. Add an OpenAPI contract

- [ ] Generate an OpenAPI specification from Spring Boot.
- [ ] Use it to validate or generate TypeScript types for the BFF.
- [ ] Add a CI check that catches breaking API changes.
- [ ] Document API versioning and compatibility rules.

Result: Spring, the BFF, and the frontend share a clear, checked contract.

### 2. Test with real PostgreSQL

- [ ] Add Testcontainers to the Spring integration tests.
- [ ] Run Flyway migrations in the test container.
- [ ] Test database constraints, repositories, services, and controllers together.
- [ ] Keep small unit tests where a database is not needed.

Result: integration tests use the same database engine as production.

### 3. Prevent silent task overwrites

- [ ] Add a JPA `@Version` field to tasks through a new Flyway migration.
- [ ] Include the version in task API requests and responses.
- [ ] Return `409 Conflict` when an old copy of a task is saved.
- [ ] Show a clear refresh-and-retry message in the frontend.
- [ ] Test two clients updating the same task.

Result: an older edit cannot silently overwrite a newer one.

### 4. Strengthen security tests

- [ ] Verify missing, invalid, and expired tokens return `401`.
- [ ] Verify users cannot access another user's tasks or categories.
- [ ] Verify malformed payloads and blocked field changes are rejected.
- [ ] Review password hashing, token expiry, CORS, validation, and security headers.
- [ ] Confirm secrets come from environment variables in production.

Result: authentication and owner-based authorization are clearly tested.

### 5. Automate accessibility checks

- [ ] Add axe-core checks to component tests.
- [ ] Add Playwright tests for the most important browser workflows.
- [ ] Test labels, dialogs, focus behavior, keyboard navigation, form errors, and tab order.
- [ ] Run a manual Lighthouse and WCAG review before release.

Result: accessibility problems are caught during development and CI.

### 6. Improve frontend data handling

- [ ] Add a server-state library such as TanStack Query if it simplifies the current code.
- [ ] Define loading, empty, success, and error states for API requests.
- [ ] Handle cache refresh and failed updates safely.
- [ ] Do not add Redux unless the application develops a real need for it.

Result: the UI handles slow, stale, and failed requests clearly.

### 7. Deploy the application

- [ ] Choose cloud hosting and a managed PostgreSQL service.
- [ ] Use GitHub Actions to test, build, publish images, and deploy.
- [ ] Configure TLS, secrets, CORS, migrations, and health checks.
- [ ] Test registration, login, CRUD, persistence, and owner isolation after deployment.
- [ ] Document rollback and recovery steps.

Result: Toodle becomes a tested, production-style deployed application.

### 8. Add cross-service tracing

- [ ] Keep the same request identity through the browser, BFF, and Spring API.
- [ ] Add OpenTelemetry tracing.
- [ ] Record useful request and database timing information.
- [ ] Confirm sensitive values are not included in traces.

Result: slow or failed requests can be followed across service boundaries.

### 9. Add infrastructure as code

- [ ] Define the selected cloud resources with Terraform.
- [ ] Keep environment-specific values and secrets outside the Terraform source.
- [ ] Document setup, changes, and teardown.

Result: the cloud environment can be reviewed and recreated consistently.

### 10. Consider real-time updates later

- [ ] After the higher priorities are complete, evaluate SSE or WebSockets.
- [ ] If useful, update another open tab when the same user changes a task.
- [ ] Test reconnect and duplicate-event behavior.

This is optional and should not delay the main modernization work.

## Scope limits

Do not add these technologies unless a real requirement appears:

- More Spring microservices.
- Redis or Kafka.
- A Python service or machine-learning features.
- Kubernetes.
- Another database.
- Redux only for resume value.

The code in `legacy/` remains reference material and is not part of the active build. Existing Flyway migrations must not be edited; database changes require a new migration.

## Release checklist

```powershell
cd frontend
npm ci
npm test
npm run build

cd ../bff
npm ci
npm test
npm run build

cd ../backend
mvn -s maven-settings.xml test

cd ..
docker compose -f compose.production.yaml build
```

Before a release, manually verify authentication, task and category workflows, calendar views, keyboard use, error recovery, persistence after restart, owner isolation, and service health checks.

## Definition of done

The modernization is complete when:

- The API contract is checked in CI.
- Spring integration tests run against PostgreSQL with Testcontainers.
- Conflicting task updates return `409` and are handled in the UI.
- Security and owner isolation have strong automated coverage.
- Important user workflows pass automated accessibility checks.
- All automated and manual release checks pass.
- Documentation matches the real system.
- Any cloud deployment claim is backed by a working, tested deployment.
