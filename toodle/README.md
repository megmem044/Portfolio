# Toodle

_Last updated: August 15, 2026_

Toodle modernizes a legacy browser task manager into a secure, contract-driven, production-grade multi-tier application. It uses a React/TypeScript frontend, an Express backend-for-frontend (BFF), a secured Spring Boot API, and PostgreSQL.

> Project status: active development. The integrated stack includes a verified automated CI workflow, production container definitions, health monitoring, and deployment-ready architecture. A cloud deployment has not been completed.

## Current architecture

```text
React + TypeScript (frontend, :5173)
                |
                v
Node/Express BFF (bff, :3000)
                |
                v
Spring Boot API (backend, :8080)
                |
                v
PostgreSQL (Docker, host :5433)
```

The active code lives in `frontend/`, `bff/`, and `backend/`. Earlier vanilla web and SwiftUI versions are retained in `legacy/` as migration references and are not part of the active build.

## Implemented

- React and TypeScript task UI with day, week, and month views
- Responsive visual system using the Toodle palette, editorial typography, and code-drawn decorative graphics
- Task search, status filters, categories, and CRUD workflows
- Node/Express BFF, including a composed bootstrap response
- Spring Boot REST endpoints for authentication, tasks, and categories
- PostgreSQL persistence with Flyway migrations
- PostgreSQL integration testing with Testcontainers and production Flyway migrations
- JWT authentication and owner-scoped server-side data access
- Standard API error responses with status, code, message, path, timestamp, and correlation ID
- Optimistic task locking with `409 Conflict` recovery for stale browser edits
- Owner-isolation, authentication, schedule-validation, and CRUD integration coverage
- Tasks and Calendar feature domains composed by the React shell
- GitHub Actions verification for frontend tests/build, BFF tests/type-checking, backend tests, and production image builds
- Production Docker Compose stack with Nginx routing browser `/api` requests to the BFF
- Health endpoints, container health checks, and request correlation IDs

## Roadmap

- Publish an OpenAPI contract from Spring and validate or generate TypeScript types for the BFF.
- Expand security tests for tokens, invalid input, blocked field changes, and owner isolation.
- Add automated accessibility checks with axe-core and browser tests with Playwright.
- Improve frontend loading, caching, stale-data, and error handling.
- Deploy through CI using managed PostgreSQL and secure cloud configuration.
- Add OpenTelemetry tracing across the BFF and Spring API.
- Define stable cloud resources with Terraform.
- Consider simple real-time updates only after the higher-priority work is complete.

The goal is to deepen the current architecture, not make it more distributed. Toodle will not add extra microservices, Redis, Kafka, Python, machine learning, Kubernetes, or another database without a real product need. See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the ordered plan.

## Prerequisites

- Node.js 20 or newer and npm
- Java 17 and Maven 3.9 or newer
- Docker Desktop with Docker Compose

## Run locally

1. Start PostgreSQL:

   ```powershell
   cd backend
   docker compose up -d
   ```

2. Start Spring Boot in a second terminal:

   ```powershell
   cd backend
   mvn spring-boot:run
   ```

3. Start the BFF in a third terminal:

   ```powershell
   cd bff
   npm ci
   npm run dev
   ```

4. Start React in a fourth terminal:

   ```powershell
   cd frontend
   npm ci
   npm run dev
   ```

Open `http://127.0.0.1:5173`.

## API documentation

While the Spring Boot API is running, its OpenAPI contract is available as JSON at
`http://127.0.0.1:8080/v3/api-docs` and as an interactive Swagger page at
`http://127.0.0.1:8080/swagger-ui.html`. Authentication routes are public; task and
category routes use the documented JWT bearer scheme.

The backend contract test exports the verified specification to
`backend/target/openapi.json`. The BFF generates its Spring response types from that
file:

```powershell
cd backend
mvn -s maven-settings.xml -Dtest=OpenApiContractTest test

cd ../bff
npm run generate:api-types
npm run build
```

`npm run build` fails when the checked-in generated types no longer match the latest
exported backend contract.

See [API_COMPATIBILITY.md](API_COMPATIBILITY.md) for the rules that distinguish safe
contract additions from breaking changes and explain when a new API version is needed.

## Run the production-shaped container stack

1. Copy `.env.example` to `.env` and replace the password and JWT secret.
2. Run:

   ```powershell
   docker compose -f compose.production.yaml up --build
   ```

Open `http://127.0.0.1:8088`. Nginx serves the frontend and routes `/api` to the BFF internally.

## Configuration

| Variable | Service | Default | Purpose |
| --- | --- | --- | --- |
| `VITE_API_URL` | frontend | `http://127.0.0.1:3000/api` | Browser-facing BFF base URL |
| `PORT` | bff | `3000` | BFF port |
| `SPRING_API_URL` | bff | `http://127.0.0.1:8080/api` | Spring API base URL |
| `DATABASE_URL` | backend | `jdbc:postgresql://localhost:5433/toodle` | JDBC connection URL |
| `DATABASE_USERNAME` | backend | `toodle` | Database user |
| `DATABASE_PASSWORD` | backend | `toodle` | Database password |
| `JWT_SECRET` | backend | local-only fallback | JWT signing secret; replace outside local development |
| `JWT_EXPIRATION_MINUTES` | backend | `120` | Token lifetime |
| `SPRING_HEALTH_URL` | bff | `http://127.0.0.1:8080/actuator/health` | Upstream health endpoint |
| `FRONTEND_ORIGIN` | bff | local Vite origins | Comma-separated CORS allowlist |

Do not commit real secrets. Local defaults are for development only.

## Observability

- Spring Boot exposes unauthenticated liveness at `/actuator/health/liveness` and database-aware readiness at `/actuator/health/readiness`.
- The BFF exposes `/health`, which reports its Spring API dependency state.
- The BFF and Spring API accept and return `X-Correlation-Id`; when absent, the BFF generates one. Completion logs include that ID, request method/path, and status.
- Docker Compose uses readiness checks so dependent services wait for the API and database.
- The production Spring profile keeps operational logs while suppressing verbose framework and SQL output.

## Backend guarantees

- Missing, invalid, and expired authentication tokens are rejected.
- Task and category access is scoped to the authenticated owner; inaccessible IDs return `404` without revealing another user's data.
- Task schedules reject times without dates and due values before their corresponding start values.
- Category names are trimmed and must be unique per user, ignoring case.
- Deleting a category clears its task associations without deleting the tasks.
- API failures follow one structured error contract and include a correlation ID.

## Verify

```powershell
cd frontend
npm test
npm run build

cd ../bff
npm test
npm run build

cd ../backend
mvn -s maven-settings.xml test
```

The repository includes eight focused frontend component cases, six BFF route/forwarding tests, and 15 backend tests across OpenAPI, PostgreSQL web integration, optimistic locking, and JWT-expiration coverage. The PostgreSQL suite uses the same Maven command run by Toodle CI.

## Repository map

```text
toodle/
|-- frontend/    React/TypeScript client
|-- bff/         Express backend-for-frontend
|-- backend/     Spring Boot API, tests, and database migrations
|-- legacy/      Archived vanilla web and SwiftUI prototypes
|-- README.md
|-- PROJECT_PLAN.md
`-- SOURCE_CODE_GUIDE.md
```

For module responsibilities and request flow, see [SOURCE_CODE_GUIDE.md](SOURCE_CODE_GUIDE.md).
