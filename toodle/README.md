# Toodle

Toodle is a secure full-stack task and calendar platform built with React, TypeScript, Express, Spring Boot, and PostgreSQL. It supports user-owned tasks and categories, search and filtering, day/week/month scheduling, conflict-safe editing, accessibility, tracing, conditional HTTP requests, and production-style deployment.

The project is deployment-ready but is not currently deployed to paid cloud infrastructure.

For the complete explanation of every project unit and file—including architecture, design rationale, advantages, drawbacks, API rules, migrations, tests, CI, benchmark evidence, deployment, recovery, and future limitations—read [PROJECT_REFERENCE.md](PROJECT_REFERENCE.md).

## What users can do

- Register, sign in, and keep tasks/categories isolated from other accounts.
- Create, edit, complete, search, filter, and delete tasks.
- Add schedules, priorities, descriptions, and color-coded categories.
- Navigate day, week, and month calendar views.
- Avoid lost work when two clients edit the same task.
- Use keyboard-accessible forms and receive clear loading, retry, validation, and error states.

## Architecture

```text
React + TypeScript + TanStack Query
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

- `frontend/` owns browser presentation, remote query state, and accessible interactions.
- `bff/` owns the browser-facing API, upstream forwarding, and bootstrap aggregation.
- `backend/` owns authentication, authorization, validation, business rules, and persistence.
- `benchmark/` owns reproducible HTTP-load and database-plan investigations.
- `render.yaml` and `compose.production.yaml` define cloud and local production-style infrastructure.
- The repository-level `.github/workflows/toodle-ci.yml` verifies every layer and production image.

## Key engineering aspects

- **Security:** BCrypt password hashing, signed JWTs, stateless Spring Security, strict DTOs, owner-scoped repository queries, CORS, HSTS, CSP, framing, and content-type protections.
- **Concurrency:** JPA optimistic locking returns `409 Conflict` when an older task copy would overwrite newer work; the frontend refreshes instead of losing data.
- **HTTP fundamentals:** authenticated task reads use strong SHA-256 ETags, `If-None-Match`, bodyless `304 Not Modified`, `private, no-cache, must-revalidate`, and `Vary: Authorization` through both Express and Spring.
- **API compatibility:** Spring exports OpenAPI, the BFF consumes generated TypeScript types, and CI detects contract drift.
- **Real database testing:** Testcontainers runs HTTP integration tests against PostgreSQL with the complete Flyway history.
- **Accessibility:** Testing Library, axe, Playwright keyboard workflows, semantic controls, Escape handling, and focus restoration.
- **Observability:** browser-to-database correlation IDs and sampled OpenTelemetry across Express, Spring MVC, and JDBC without capturing tokens, passwords, bodies, or database values.
- **DOM performance:** memoized calendar indexes reduce 500-task projection work from 84,000 to roughly 668 week operations and from 21,000 to roughly 542 month operations.
- **Measured backend performance:** a 500-task, 20-client benchmark used PostgreSQL profiling to rule out the query; telemetry changes improved local throughput 41.23% and reduced p95 latency 47.27% with zero failures.
- **Deployment discipline:** health-ordered Docker services, managed-secret configuration, Render infrastructure as code, TLS termination assumptions, and documented smoke, rollback, backup, and recovery procedures.

## Technology

React, TypeScript, Vite, TanStack Query, Express, Java 17, Spring Boot, Spring Security, Spring Data JPA, PostgreSQL, Flyway, OpenAPI, OpenTelemetry, Docker, Testcontainers, Vitest, Testing Library, axe, Playwright, GitHub Actions, Nginx, and Render.

## Local development

Requirements: Node.js 20+, npm, Java 17, Maven 3.9+, and Docker Desktop.

Start PostgreSQL and Spring:

```powershell
cd backend
docker compose up -d
mvn spring-boot:run
```

Start the BFF in a second terminal:

```powershell
cd bff
npm ci
npm run dev
```

Start the frontend in a third terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`.

## Production-style local stack

Copy `.env.example` to `.env`, replace its sample secrets, then run:

```powershell
docker compose -f compose.production.yaml up --build
```

Open `http://127.0.0.1:8088`.

## Verification

Run the backend first because it exports the OpenAPI document consumed by the BFF check:

```powershell
cd backend
mvn -s maven-settings.xml test

cd ../bff
npm ci
npm test
npm run build

cd ../frontend
npm ci
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

The suite contains 20 backend tests, 11 BFF tests, 14 frontend component tests, and one Playwright workflow. Docker Desktop is required for PostgreSQL Testcontainers.

## API and health endpoints

When Spring is running:

- OpenAPI: `http://127.0.0.1:8080/v3/api-docs`
- Swagger UI: `http://127.0.0.1:8080/swagger-ui.html`
- Readiness: `http://127.0.0.1:8080/actuator/health/readiness`

The BFF health endpoint is `http://127.0.0.1:3000/health`.

## Resume-ready summary

**Toodle | Full-Stack Task and Calendar Platform**

- Built a secure React/Express/Spring Boot/PostgreSQL task platform with JWT ownership, optimistic locking, conditional HTTP caching, generated OpenAPI types, Testcontainers, and OpenTelemetry.
- Load-tested 500 seeded tasks with 20 concurrent clients and improved local throughput 41% while reducing p95 latency 47% through evidence-led telemetry optimization.
- Prepared Docker/Render infrastructure, CI container gates, and accessibility automation with 100 Lighthouse Accessibility and Best Practices scores.

See [PROJECT_REFERENCE.md](PROJECT_REFERENCE.md) for the full project story, detailed file map, tradeoffs, operational instructions, and interview material.
