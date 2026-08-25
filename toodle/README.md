# Toodle

_Last updated: August 24, 2026_

Toodle is a full-stack task and calendar application for organizing day-to-day work without losing sight of when it needs to happen. Users can create an account, group tasks into categories, search and filter their work, and move between day, week, and month views.

The project started as a task manager and grew into a production-style engineering exercise. It now includes user isolation, conflict-safe editing, a checked API contract, real PostgreSQL integration tests, distributed tracing, accessibility automation, containerized deployment configuration, and a reproducible performance benchmark.

## What the application does

- Registers and authenticates users with signed JWTs and hashed passwords.
- Keeps every user's tasks and categories private.
- Creates, edits, completes, searches, filters, and deletes tasks.
- Organizes tasks into categories and calendar views.
- Detects stale edits instead of silently overwriting newer changes.
- Shows clear loading, empty, retry, validation, and error states.
- Carries one request ID from the browser through the BFF and Spring API.

## Architecture

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

The code is divided into three application folders:

- `frontend/` contains the React interface, TanStack Query data layer, calendar views, component tests, and Playwright workflow.
- `bff/` contains the browser-facing Express API, request composition, correlation-ID handling, and OpenTelemetry setup.
- `backend/` contains Spring Security, business rules, REST controllers, JPA persistence, Flyway migrations, and PostgreSQL integration tests.

The BFF gives the browser one stable API boundary and forwards authenticated work to Spring. Spring remains the source of truth for validation, ownership, and persistence.

## Engineering decisions

### Checked API contract

The backend generates an OpenAPI document during testing. The BFF generates TypeScript types from that document and checks them during its build. GitHub Actions runs the same workflow, so an incompatible Spring response cannot quietly drift away from the TypeScript contract. The compatibility rules are documented in [API_COMPATIBILITY.md](API_COMPATIBILITY.md).

### Real database testing

Testcontainers starts PostgreSQL for integration tests and runs the real Flyway migration history before exercising the API. This checks the schema, JPA mappings, ownership rules, and HTTP behavior against the same database engine used by the production configuration.

Applied Flyway migrations are treated as permanent history. New database changes must use a new migration rather than editing an existing file and breaking its checksum.

### Conflict-safe updates

Tasks carry an optimistic-lock version. If two tabs read the same task and one saves first, the second receives `409 Conflict` instead of overwriting the newer change. The frontend refreshes the data and explains how to retry with the latest version.

### Security boundaries

Spring Security validates JWTs and protects task and category routes. Repository queries include the authenticated owner, and integration tests prove that one account cannot read or modify another account's records. Production secrets come from environment variables and are never committed.

### Accessible interaction

Testing Library and axe check the authentication form and task dialog. Playwright verifies a keyboard user can sign in, open the task dialog, close it with Escape, and return focus to the original button.

A Lighthouse and WCAG review also uncovered a mobile layout problem that automated scores did not explain. After the responsive fix, the focused audit scored 100 for Accessibility, Best Practices, and SEO. Desktop Performance measured 96; simulated mobile Performance measured 67 and remains an honest area for future improvement.

### Tracing and request IDs

The browser creates a correlation ID for each request. Express validates and forwards it, Spring includes it in structured logs, and failed browser requests display it for troubleshooting.

OpenTelemetry traces HTTP work across the BFF and Spring API and records JDBC timing. Production-style tracing uses 10% parent-based sampling. Authorization headers, passwords, tokens, request bodies, and database parameter values are not added to traces.

## Measured performance work

The benchmark under [`benchmark/`](benchmark/README.md) runs against the production-style Docker stack. It creates a dedicated account, seeds eight categories and 500 tasks through the real HTTP path, warms the application, and sends task-list and bootstrap traffic from 20 concurrent clients for 30 measured seconds.

The first run showed 5,019 ms p95 latency and 8.61 requests per second. PostgreSQL completed the profiled 500-row owner query in 3.07 ms, which pointed away from the database plan and toward full-volume console telemetry export.

After changing tracing to 10% parent-based sampling and disabling unused OTLP metrics and log exporters, the same workload produced:

| Measurement | Baseline | Optimized | Change |
| --- | ---: | ---: | ---: |
| Throughput | 8.61 req/s | 12.16 req/s | 41.23% higher |
| Overall p95 | 5,019 ms | 2,647 ms | 47.27% lower |
| Failed requests | 0 | 0 | No regression |

The runner, SQL profile, and baseline/optimized JSON reports are committed with the project. These results describe one controlled local machine, not guaranteed production capacity.

## Project status

The complete production-style stack has been built and run locally with healthy frontend, BFF, backend, and PostgreSQL containers. Automated tests, accessibility review, tracing, benchmark tooling, health checks, and deployment documentation are complete.

`render.yaml` is ready to create a managed PostgreSQL database, private Spring service, public BFF, and static frontend. No paid Render resources have been created, so this project is deployment-ready but not deployed to production. See [DEPLOYMENT.md](DEPLOYMENT.md) for the final provider-specific step and [PROJECT_PLAN.md](PROJECT_PLAN.md) for the full implementation record.

## Requirements

- Node.js 20 or newer
- npm
- Java 17
- Maven 3.9 or newer
- Docker Desktop

## Run the development stack

Start each part in its own PowerShell terminal.

First, start PostgreSQL:

```powershell
cd backend
docker compose up -d
```

Start Spring:

```powershell
cd backend
mvn spring-boot:run
```

Start the BFF:

```powershell
cd bff
npm ci
npm run dev
```

Start the frontend:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`.

## Run the production-style stack

Create a local `.env` from `.env.example`, replace the sample secrets, and run:

```powershell
docker compose -f compose.production.yaml up --build
```

Open `http://127.0.0.1:8088`. The production-style stack requires `POSTGRES_PASSWORD` and `JWT_SECRET`. Do not commit real secret values.

## Run the tests

Docker Desktop must be running. Run the backend first because its tests create `backend/target/openapi.json`, which the BFF contract check needs.

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

The verified suite contains 19 backend tests, 9 BFF tests, 12 frontend component tests, and 1 Playwright browser workflow.

## API documentation

When Spring is running:

- OpenAPI JSON: `http://127.0.0.1:8080/v3/api-docs`
- Swagger UI: `http://127.0.0.1:8080/swagger-ui.html`

The provider-neutral release, rollback, backup, and database recovery runbook is in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Configuration reference

| Variable | Used by | Purpose |
| --- | --- | --- |
| `VITE_API_URL` | Frontend | Browser-facing BFF URL |
| `SPRING_API_URL` | BFF | Spring API URL |
| `SPRING_HEALTH_URL` | BFF | Spring health URL |
| `SPRING_HOSTPORT` | BFF | Render private Spring host and port |
| `FRONTEND_ORIGIN` | BFF | Allowed browser origins |
| `DATABASE_URL` | Backend | PostgreSQL connection URL |
| `DATABASE_USERNAME` | Backend | PostgreSQL user |
| `DATABASE_PASSWORD` | Backend | PostgreSQL password |
| `JWT_SECRET` | Backend | Token signing secret |
| `JWT_EXPIRATION_MINUTES` | Backend | Login token lifetime |
| `OTEL_SDK_DISABLED` | Backend and BFF | Turns OpenTelemetry off or on |
| `OTEL_SERVICE_NAME` | Backend and BFF | Names the service in each trace |
| `OTEL_TRACES_EXPORTER` | Backend and BFF | Chooses where traces are sent |
| `OTEL_TRACES_SAMPLER_ARG` | Backend and BFF | Sets the fraction of root traces retained |
| `OTEL_METRICS_EXPORTER` | Backend and BFF | Disables or selects metrics export |
| `OTEL_LOGS_EXPORTER` | Backend and BFF | Disables or selects telemetry log export |

For a guided code tour, see [SOURCE_CODE_GUIDE.md](SOURCE_CODE_GUIDE.md).
