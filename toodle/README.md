# Toodle

Toodle is an in-progress modernization of a browser-only task manager into a maintainable full-stack application. The current phase connects a React/TypeScript frontend to a Node.js backend-for-frontend (BFF), a secured Spring Boot API, and PostgreSQL.

> Project status: active development. The integrated local stack exists; automated CI/CD, Azure deployment, monitoring, and a micro-frontend split are planned and are not represented as complete.

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

## Roadmap

- Add frontend and BFF automated tests
- Add GitHub Actions type-check, test, and build jobs
- Add service health checks and structured observability
- Containerize and deploy the stack to Azure
- Evaluate a two-domain Tasks/Calendar micro-frontend split after the monolithic React app is stable

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

Do not commit real secrets. Local defaults are for development only.

## Verify

```powershell
cd frontend
npm run build

cd ../bff
npm run build

cd ../backend
mvn test
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
