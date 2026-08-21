# Toodle

_Last updated: August 20, 2026 (release review complete)_

Toodle is a task and calendar application. Users can create an account, organize tasks, and view their work by day, week, or month.

## Project status

The application works locally, has automated tests, passed its accessibility review, and is ready for a Render deployment. No cloud resources have been created yet.

Completed work includes:

- A React and TypeScript frontend.
- An Express BFF between the browser and Spring.
- A Spring Boot API with PostgreSQL and Flyway migrations.
- JWT login and data protection between users.
- A checked OpenAPI contract and generated BFF types.
- PostgreSQL integration tests with Testcontainers.
- Protection against two browser tabs overwriting the same task.
- Automated security and accessibility tests.
- TanStack Query loading, retry, cache, and error handling.
- OpenTelemetry request and database tracing across the BFF and Spring API.
- Lighthouse scores of 100 for Accessibility, Best Practices, and final SEO.
- Docker production images and GitHub Actions checks.
- A Render Blueprint for private PostgreSQL, Spring, the BFF, HTTPS, and the static frontend.

The only required step left is creating the paid Render resources and testing the live application. See [DEPLOYMENT.md](DEPLOYMENT.md) for that step and [PROJECT_PLAN.md](PROJECT_PLAN.md) for the release checklist.

## How it works

```text
React frontend
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

The active application is in these folders:

```text
frontend/   Browser interface
bff/        Browser-facing API layer
backend/    Spring API and database code
```

## Requirements

- Node.js 20 or newer
- npm
- Java 17
- Maven 3.9 or newer
- Docker Desktop

## Run locally

1. Start PostgreSQL:

   ```powershell
   cd backend
   docker compose up -d
   ```

2. Start Spring in a new terminal:

   ```powershell
   cd backend
   mvn spring-boot:run
   ```

3. Start the BFF in a new terminal:

   ```powershell
   cd bff
   npm ci
   npm run dev
   ```

4. Start the frontend in a new terminal:

   ```powershell
   cd frontend
   npm ci
   npm run dev
   ```

Open `http://127.0.0.1:5173`.

## Run tests

Docker Desktop must be running. Run the backend first because it creates the OpenAPI file checked by the BFF.

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

The test suite currently has 18 backend tests, 7 BFF tests, 12 frontend component tests, and 1 Playwright browser test.

## API documentation

When Spring is running:

- OpenAPI JSON: `http://127.0.0.1:8080/v3/api-docs`
- Swagger UI: `http://127.0.0.1:8080/swagger-ui.html`

The backend test writes the checked contract to `backend/target/openapi.json`. The BFF build compares its generated TypeScript types with that file. Compatibility rules are in [API_COMPATIBILITY.md](API_COMPATIBILITY.md).

Provider-neutral release, rollback, and database recovery steps are in
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Production-style Docker stack

Create a local `.env` from `.env.example`, replace its sample secrets, then run:

```powershell
docker compose -f compose.production.yaml up --build
```

Open `http://127.0.0.1:8088`.

Production requires `POSTGRES_PASSWORD` and `JWT_SECRET`. Do not commit real secrets.

## Main configuration

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
| `OTEL_TRACES_EXPORTER` | Backend and BFF | Chooses where trace records are sent |

## Important behavior

- Missing, invalid, and expired tokens return `401`.
- A user cannot read or change another user's data.
- Unknown request fields are rejected.
- Old task edits return `409` instead of overwriting newer work.
- Request errors use one JSON format and include a correlation ID.
- OpenTelemetry records BFF, Spring request, and database timing in production logs.
- Trace settings do not capture authorization headers, request bodies, or database values.
- Loading, empty, error, retry, and stale-data states are handled in the frontend.

For a guided code tour, see [SOURCE_CODE_GUIDE.md](SOURCE_CODE_GUIDE.md).
