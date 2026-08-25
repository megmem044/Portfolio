# Toodle Project Plan and Implementation Record

_Last updated: August 24, 2026_

## Project purpose

Toodle was built as a secure task and calendar application that demonstrates more than basic create, read, update, and delete operations. The project follows a real production-style structure with a React frontend, an Express backend-for-frontend (BFF), a Spring Boot API, and PostgreSQL.

Users can create an account, organize tasks into categories, mark work complete, and view schedules by day, week, or month. Each user's information is private, older edits cannot silently overwrite newer work, and failures are handled clearly in the interface.

## Current status

The complete application runs locally using production Docker images. The API contract, PostgreSQL integration, security boundaries, accessibility, tracing, health checks, infrastructure configuration, and performance benchmark have been implemented and tested.

Render configuration is prepared in `render.yaml`, but no paid Render resources have been created. The project should be described as deployment-ready, not as deployed to production.

## Implementation process

### 1. Establishing the system architecture

The project was organized into four clear parts:

- React and TypeScript provide the browser interface.
- Express acts as the BFF and gives the browser one stable API boundary.
- Spring Boot owns authentication, validation, business rules, and persistence.
- PostgreSQL stores users, categories, tasks, ownership, and task versions.

This separation keeps browser concerns out of the main API and allows each layer to be tested independently. The BFF also combines task and category data into a bootstrap response so the browser does not need to coordinate every backend call itself.

### 2. Building the API contract

Spring was made the source of truth for the HTTP contract. The backend generates an OpenAPI document during testing, and the BFF generates TypeScript types from that document.

The BFF build checks the generated types instead of silently accepting contract changes. GitHub Actions runs the same check, which catches incompatible request or response changes before they reach the main branch. Compatibility expectations are documented in `API_COMPATIBILITY.md`.

### 3. Adding PostgreSQL and schema history

PostgreSQL replaced temporary application storage. Flyway migrations create the task, category, user, ownership, and optimistic-locking fields in a repeatable order.

Testcontainers starts a real PostgreSQL container for integration tests. This verifies that Flyway migrations, JPA mappings, constraints, and HTTP behavior work together against the same database engine used by the production configuration.

An important lesson from this work was that applied Flyway migrations must never be edited. Earlier header comments changed migration checksums and caused validation failures against an existing local database. The original migration bytes were restored, and the project now clearly requires a new migration for every future schema change.

### 4. Preventing lost task updates

A version column was added to tasks using JPA optimistic locking. The frontend sends the version it last read when updating a task.

If another browser or tab has already changed the task, Spring returns `409 Conflict` instead of overwriting the newer data. The frontend refreshes the task list and explains that the user should review the latest version before trying again. Integration tests reproduce two clients editing the same task.

### 5. Securing users and data

Registration and login use hashed passwords and signed JWTs. Spring Security keeps the API stateless, validates tokens, and protects task and category routes.

Repositories and services always include the authenticated owner in their queries. Tests confirm that one user cannot read, update, or delete another user's information. The suite also covers missing, malformed, invalid, and expired tokens; duplicate accounts and categories; unknown request fields; invalid schedules; CORS; and security headers.

Development defaults are kept separate from production configuration. Production database credentials and the JWT signing secret must come from environment variables and are never stored in source control.

### 6. Developing the frontend experience

The frontend was implemented with React and TypeScript. TanStack Query owns server data, caching, refreshes, retries, and mutation state. Redux was intentionally not added because the current application does not need another global state system.

The interface includes authentication, task and category management, search, filters, statistics, and day/week/month calendar views. It handles loading, empty, success, stale-update, and network-error states. Forms trim values, validate schedules, and preserve clear labels and error messages.

The browser creates a correlation ID for every API request. The BFF validates or replaces it, forwards it to Spring, and returns it in the response. When a request fails, the visible error includes the request ID so the same operation can be found in service logs.

### 7. Testing accessibility and responsive behavior

Vitest, Testing Library, and axe test the authentication form and task dialog for detectable accessibility problems. Playwright covers an important keyboard workflow: signing in, opening the task dialog, closing it with Escape, and returning focus to the original button.

A manual Lighthouse and WCAG review found a responsive CSS ordering problem that pushed the authentication form partly off a narrow screen. The mobile layout was corrected and checked again. A valid `robots.txt`, production asset caching, and an IPv4 Docker health check were also added during this review.

The final focused Lighthouse results were 100 for Accessibility, Best Practices, and SEO. Desktop Performance measured 96. Mobile Performance measured 67 under Lighthouse's simulated mobile throttling and remains a possible area for later improvement.

### 8. Adding tracing and operational visibility

OpenTelemetry was added to the Express BFF and Spring API. Traces cover browser-facing HTTP work, BFF-to-Spring calls, Spring request handling, and JDBC database timing.

Trace configuration avoids request bodies, authorization headers, passwords, tokens, and database parameter values. Production-like tracing uses parent-based sampling so connected BFF and Spring spans keep the same trace decision.

Health endpoints are available for the BFF and Spring readiness checks. Structured request logs include the correlation ID, method, path, and status so failures can be followed across services.

### 9. Preparing production-style deployment

Dockerfiles build the frontend, BFF, and backend. `compose.production.yaml` starts PostgreSQL and all application services with health-based startup ordering. The full local stack was verified with all four containers healthy.

`render.yaml` describes a managed PostgreSQL database, private Spring service, public BFF, static frontend, HTTPS, secrets, CORS, and deployments gated by passing GitHub checks. `DEPLOYMENT.md` explains the final Render steps, while `docs/DEPLOYMENT.md` covers provider-neutral release, rollback, backup, and recovery practices.

The actual Render deployment remains intentionally incomplete because it creates paid resources. After deployment, the live application still needs manual checks for registration, login, task persistence, user separation, health endpoints, and rollback readiness.

### 10. Measuring and improving performance

A reproducible benchmark was added under `benchmark/`. It starts the production-style Docker/PostgreSQL system, creates a dedicated user, seeds eight categories and 500 tasks through the real HTTP path, warms the application, and sends a mix of task-list and bootstrap requests from 20 concurrent clients for 30 measured seconds.

The benchmark records request count, failures, throughput, and min, p50, p95, p99, and maximum latency. A separate PostgreSQL `EXPLAIN ANALYZE` script records planning time, execution time, buffer use, row count, and the database plan.

The baseline sustained 8.61 requests per second with 5,019 ms p95 latency and zero failures. PostgreSQL executed the profiled 500-row owner-scoped query in 3.07 ms, showing that the database query was not the main bottleneck. Full-volume console trace export and unused OTLP metrics/log export created the larger measured cost.

Tracing was changed from 100% console sampling to 10% parent-based sampling, and unused OTLP metrics and log exporters were disabled. Under the same workload, throughput increased to 12.16 requests per second and p95 decreased to 2,647 ms, with zero failures. This was a 41.23% throughput increase and a 47.27% p95 reduction on the local benchmark machine.

The runner, instructions, SQL profile, and baseline/optimized JSON reports are committed so the result can be reproduced and challenged. These local numbers are engineering evidence, not a claim about universal production capacity.

## Key Aspects of the Project

### Resume-ready project heading

**Toodle | Full-Stack Task and Calendar Platform**

**Technologies:** React, TypeScript, TanStack Query, Express, Spring Boot, Spring Security, PostgreSQL, Flyway, Docker, OpenTelemetry, Testcontainers, Playwright, Vitest, GitHub Actions, Render

### Strong resume points

- Designed and built a four-layer task and calendar platform with a React frontend, Express BFF, Spring Boot API, and PostgreSQL database, supporting JWT authentication, user-owned data, categories, search, filters, and day/week/month scheduling.
- Prevented lost updates with JPA optimistic locking and `409 Conflict` handling, including a tested two-client workflow that refreshes stale frontend data instead of overwriting newer changes.
- Generated TypeScript API types from Spring OpenAPI output and enforced contract compatibility in GitHub Actions, reducing the risk of frontend/backend integration drift.
- Secured task and category operations with password hashing, JWT validation, owner-scoped repositories, strict request validation, environment-based secrets, and tests proving users cannot access each other's data.
- Built real PostgreSQL integration coverage with Testcontainers and Flyway, validating schema migrations, JPA behavior, security rules, and HTTP endpoints against a containerized database.
- Added end-to-end correlation IDs and sampled OpenTelemetry traces across Express, Spring MVC, and JDBC while excluding authorization headers, passwords, tokens, request bodies, and database values.
- Created a reproducible Docker load benchmark with 500 seeded tasks and 20 concurrent clients; used PostgreSQL profiling to rule out the database query, then increased throughput 41.23% and reduced p95 latency 47.27% by optimizing telemetry export.
- Automated accessibility checks with axe and Playwright, achieved Lighthouse scores of 100 for Accessibility, Best Practices, and final SEO, and corrected a mobile layout defect discovered during visual review.
- Prepared production Docker images, health-based service startup, secret-driven configuration, Render infrastructure as code, and documented release, rollback, backup, and recovery procedures without falsely claiming a live deployment.

### Short resume version

- Built a secure React/Express/Spring Boot/PostgreSQL task platform with JWT ownership boundaries, optimistic locking, generated OpenAPI types, Testcontainers integration tests, and OpenTelemetry tracing.
- Load-tested 500 seeded tasks with 20 concurrent clients and improved local throughput 41% while reducing p95 latency 47% through measured telemetry optimization.
- Prepared production Docker images, health checks, GitHub Actions gates, Render infrastructure as code, and accessibility automation with 100 Lighthouse Accessibility and Best Practices scores.

## Remaining work

### Required before claiming a live deployment

- [ ] Create and approve the paid Render Blueprint resources.
- [ ] Confirm the live frontend, BFF, Spring API, and managed PostgreSQL services are healthy.
- [ ] Test registration, login, task/category operations, persistence after restart, and user separation online.
- [ ] Confirm production trace output, HTTPS, CORS, secrets, rollback, and recovery settings.

### Optional future work

- Improve mobile performance by reviewing external font/icon loading and reducing unused frontend JavaScript and CSS.
- Decide whether Server-Sent Events or WebSockets would provide enough user value to justify live cross-tab task updates.
- Repeat performance tests on controlled hardware and multiple runs before making broader capacity claims.

Optional work should follow a measured product need. Redis, Kafka, Kubernetes, another database, machine learning, or Redux should not be added only to increase the technology list.
