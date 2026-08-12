# Toodle

Toodle is an in-progress modernization of a browser-only task manager into a maintainable full-stack application. The current phase connects a React/TypeScript frontend to a Node.js backend-for-frontend (BFF), a secured Spring Boot API, and PostgreSQL.

> Project status: active development. The integrated stack includes automated CI verification, production container definitions, health monitoring, and deployment-ready architecture. A cloud deployment has not yet been completed.

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
- Task search, status filters, categories, and CRUD workflows
- Node/Express BFF, including a composed bootstrap response
- Spring Boot REST endpoints for authentication, tasks, and categories
- PostgreSQL persistence with Flyway migrations
- JWT authentication and owner-scoped server-side data access
- Spring integration tests for core authenticated API workflows
- Tasks and Calendar feature domains composed by the React shell
- GitHub Actions verification for frontend, BFF, backend, and production image builds
- Production Docker Compose stack with Nginx routing browser `/api` requests to the BFF
- Health endpoints, container health checks, and request correlation IDs

## Roadmap

- Add frontend and BFF automated tests
- Expand backend authentication, authorization, and validation tests
- Standardize API error responses
- Separate readiness and liveness checks
- Verify the complete GitHub Actions workflow
- Consider cloud deployment after the local and CI workflows are stable

The goal is architectural modernization, not expanding the product with unrelated features.

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

- Spring Boot exposes unauthenticated liveness at `/actuator/health` and `/actuator/health/liveness`.
- The BFF exposes `/health`, which reports its Spring API dependency state.
- The BFF and Spring API accept and return `X-Correlation-Id`; when absent, the BFF generates one. Completion logs include that ID, request method/path, and status.
- Docker Compose uses these endpoints as health checks so dependent services wait for readiness.

## Verify

```powershell
cd frontend
npm run build

cd ../bff
npm run build

cd ../backend
mvn -s maven-settings.xml test
```

## Repository map

```text
toodle/
|-- frontend/    React/TypeScript client
|-- bff/         Express backend-for-frontend
|-- backend/     Spring Boot API, tests, and database migrations
|-- legacy/      Archived vanilla web and SwiftUI prototypes
|-- README.md
`-- SOURCE_CODE_GUIDE.md
```

For module responsibilities and request flow, see [SOURCE_CODE_GUIDE.md](SOURCE_CODE_GUIDE.md).
