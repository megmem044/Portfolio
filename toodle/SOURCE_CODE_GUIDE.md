# Toodle source code guide

This guide describes the repository at its current modernization phase. It separates production-path code from retained prototypes and records the main ownership boundaries for future contributors.

## Request flow

```text
frontend/src
  -> HTTP /api
bff/src/server.ts
  -> authenticated proxy/composed responses
backend/src/main/java/com/toodle
  -> controllers -> services -> repositories
backend/src/main/resources/db/migration
  -> PostgreSQL schema
```

The browser stores the JWT and basic display identity. Tasks, categories, users, and authorization decisions are owned by the server.

## Frontend

`frontend/` is the active React/TypeScript client built by Vite.

- `src/main.tsx` is the browser entry point and loads the shared design stylesheet.
- `src/app/App.tsx` is the current application shell. It coordinates authentication, remote state, filters, calendar navigation, and modal workflows.
- `src/components/` contains reusable UI controls: authentication, task cards/forms, categories, and statistics.
- `src/mfe/tasks/` owns task statistics, filtering, and search as a feature boundary.
- `src/mfe/calendar/` owns calendar navigation and composes the day, week, and month views.
- `src/views/` contains day, week, and month calendar projections.
- `src/features/tasks/types.ts` defines the client domain contracts.
- `src/features/tasks/api.ts` is the only browser HTTP boundary. It attaches the bearer token and maps domain objects to API requests.
- `src/features/tasks/taskUtils.ts` contains pure date, filtering, matching, and sorting helpers.
- `src/features/tasks/storage.ts` contains legacy local-storage helpers. It is not the active task source of truth and can be removed once migration compatibility is no longer required.
- `src/styles.css` is the original Toodle design system promoted from the vanilla prototype.
- `public/icons/` contains static assets copied directly into the Vite build.

Keep network logic in `api.ts`, pure transformations in utilities, and view-specific markup in components/views. `App.tsx` remains the shell and shared-state owner. The Tasks and Calendar boundaries are composed modules within one Vite application, not independently deployed micro-frontends.

## Backend-for-frontend

`bff/src/server.ts` is the active Express BFF.

Responsibilities:

- expose the browser-facing `/api` contract;
- require bearer authentication for protected routes;
- forward authentication, task, and category operations to Spring;
- compose tasks and categories into `/api/bootstrap`;
- translate an unavailable upstream service into a `502` response.

It should not own database persistence or duplicate Spring business rules. Future frontend-specific aggregation belongs here.

## Spring Boot API

`backend/src/main/java/com/toodle/` follows conventional Spring layers:

- `controller/` defines REST routes and response status codes;
- `service/` owns business operations and applies the current user boundary;
- `repository/` defines Spring Data queries, including owner-scoped lookups;
- `model/` contains JPA entities and the priority enum;
- `dto/` defines validated request and stable response records;
- `security/` configures stateless Spring Security, JWT creation, and request authentication;
- `exception/` converts domain and validation failures into API responses.

`CurrentUserService` resolves the authenticated identity. Services and repositories must continue using owner-scoped operations so one account cannot access another account's tasks or categories.

## Persistence

PostgreSQL is defined for local development in `backend/compose.yaml`. Flyway migrations in `backend/src/main/resources/db/migration/` are the schema history:

- `V1__create_task_schema.sql` creates the original task/category tables;
- `V2__create_user_schema.sql` adds users and ownership relationships.

Never edit an applied migration for a new schema change. Add the next numbered migration instead.

## Tests

`backend/src/test/java/com/toodle/TaskControllerTest.java` exercises registration, authentication requirements, and task/category CRUD through the HTTP layer with an H2 test database.

Current test gaps are frontend component/unit coverage and BFF route coverage. Those belong to the next CI-focused phase; the README does not claim they already exist.

## Legacy code

`legacy/web/` is the original vanilla JavaScript PWA and `legacy/ios/` is the SwiftUI prototype. Neither directory is part of the active build. They are retained to show product history and support behavior comparisons during modernization. See `legacy/README.md`.

## Commenting convention

Authored source files should start with a short comment that states their responsibility when the filename and framework structure are not already sufficient. Add inline comments for security boundaries, non-obvious date calculations, protocol mapping, and intentional compatibility behavior.

Avoid comments that merely restate syntax. JSON manifests, lockfiles, generated output, compiled classes, and third-party dependencies should not receive comments.

## Git hygiene

The repository commits source, lockfiles, configuration, migrations, tests, and documentation. `.gitignore` excludes dependency trees, local Maven caches, build output, logs, editor state, and environment files. Never force-add ignored generated files or secrets.

## Current phase and next boundaries

Implemented now: React/TypeScript migration, Tasks and Calendar feature boundaries, a Node/Express BFF, Spring Boot REST persistence, PostgreSQL, JWT authentication and authorization, Docker packaging, health monitoring, correlation IDs, and initial GitHub Actions CI.

The immediate priorities are backend hardening, broader automated testing, consistent error responses, and CI verification. Cloud deployment remains optional and must not be presented as completed until the application has genuinely been deployed and tested.
