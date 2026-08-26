# Toodle complete project reference

_Last updated: August 25, 2026_

This is the authoritative reference for Toodle. It explains the product, user use cases, architecture, every maintained project unit, important files, design decisions, tradeoffs, operational procedures, measured results, and future boundaries. `README.md` remains the short entry point; when the two disagree, update both and treat this document as the detailed source of truth.

## 0. Reference identity and evidence labels

This reference describes the Toodle source tree as of August 25, 2026, including the conditional-HTTP and calendar-index changes in the current working tree. It describes source state, not a tagged release or live cloud deployment.

The following labels keep claims precise:

| Label | Meaning |
| --- | --- |
| **IMPLEMENTED** | Present in source/configuration. |
| **TESTED** | Covered by an automated test that asserts the behavior. |
| **MEASURED** | Supported by a recorded benchmark or audit result. |
| **PREPARED** | Configuration or procedure exists but has not been exercised in its final environment. |
| **NOT YET VERIFIED** | Requires an environment or action that has not happened. |
| **PLANNED** | Possible future work, not current behavior. |

Current evidence snapshot:

- **IMPLEMENTED:** full React/BFF/Spring/PostgreSQL stack, security, optimistic locking, conditional HTTP, tracing, accessibility behavior, Docker, and Render configuration.
- **TESTED:** frontend/BFF/Spring behavior, PostgreSQL migrations/ownership, OpenAPI drift, keyboard focus, and production image builds through the documented suite/CI.
- **MEASURED:** local backend benchmark improvement, SQL execution evidence, Lighthouse audit, and calendar lookup-operation reduction.
- **PREPARED:** paid Render topology, secrets, TLS/security headers, health checks, rollback, and recovery procedure.
- **NOT YET VERIFIED:** a real Render deployment, live certificate/redirect/header behavior, managed backup restoration, and live telemetry collection.
- **PLANNED:** further mobile profiling and real-time synchronization only if measured/product needs justify them.

## Toodle in five minutes

### Five ideas

1. React owns presentation and browser state.
2. Express is a browser-specific BFF, not a second business backend.
3. Spring is the authority for authentication, authorization, validation, and business rules.
4. PostgreSQL is the persistent source of truth.
5. OpenAPI synchronizes the Java producer with its TypeScript consumer.

```text
Browser -> React -> Express BFF -> Spring Boot -> PostgreSQL
```

The normal dependency direction is:

```text
React components
      -> frontend API adapter
      -> Express BFF
      -> Spring controllers
      -> Spring services
      -> Spring Data repositories
      -> PostgreSQL
```

Forbidden shortcuts:

```text
React --------X-------> PostgreSQL
BFF ----------X-------> PostgreSQL
Controller ---X-------> repository (business operations go through services)
BFF ----------X-------> duplicate Spring business rules
Repository ---X-------> HTTP status/header concepts
```

### Domain model

```text
User 1 -------- owns -------- * Task
  |                                |
  +---------- owns -------- * Category
                                   |
Category 1 <--- optional ------- * Task
```

- **User:** an authenticated account that owns all private application data.
- **Task:** a user-owned unit of work with content, schedule, completion, priority, optional category, creation time, and concurrency version.
- **Category:** a user-owned name/color label that can organize multiple tasks.
- **Task version:** a number incremented after an update so the server can reject a stale client copy.

### Laws of the application

| ID | Invariant | Protection |
| --- | --- | --- |
| `INV-01` | A user can access only their own tasks. | Owner-scoped repository queries and integration tests. |
| `INV-02` | A task may reference only a category owned by the same user. | Service validation and owner-scoped category lookup. |
| `INV-03` | An old client copy cannot silently overwrite a newer task. | Task version, transactional check/JPA locking, `409`, frontend refresh. |
| `INV-04` | Times require their matching dates; due date/time cannot precede start date/time. | `TaskService.validateSchedule` and HTTP tests. |
| `INV-05` | Clients cannot choose owners or other protected persistence fields. | Request DTOs and strict unknown-field rejection. |
| `INV-06` | Applied Flyway migrations are immutable. | Forward-only migration policy and startup validation. |
| `INV-07` | Spring remains the only business-rule authority. | Layer/dependency rules and thin BFF design. |
| `INV-08` | The BFF preserves required authentication, correlation, cache, and content metadata. | Explicit header allowlists and BFF tests. |
| `INV-09` | Tokens, passwords, bodies, and database values do not enter telemetry. | Capture exclusions and instrumentation configuration. |
| `INV-10` | API changes propagate from Spring to the BFF consumer. | OpenAPI export, generated TypeScript, and CI drift check. |

When changing Toodle, identify the affected invariants before editing code.

## 1. What Toodle is

Toodle is a full-stack task and calendar application and a production-style engineering portfolio project. An end user can create an account, keep private tasks and categories, search and filter work, mark tasks complete, and see scheduled work in day, week, or month views.

The system is intentionally deeper than CRUD. It demonstrates a React browser client, an Express backend-for-frontend (BFF), a Spring Boot domain API, PostgreSQL persistence, an OpenAPI contract, authentication and authorization, concurrency control, HTTP caching, accessibility, observability, containerization, CI, deployment preparation, and measured performance work.

Current status: the complete production-style stack has run locally. The Render infrastructure definition is prepared, but paid cloud resources have not been created. Toodle is deployment-ready, not currently deployed to production.

## 2. End-user use cases

### Account and privacy

- Register with a name, email, and password.
- Sign in and out using a stateless JWT session.
- See only tasks and categories owned by the signed-in account.
- Receive understandable authentication and request errors without leaking another user's data.

### Task planning

- Create, view, edit, complete, and delete a task.
- Add optional descriptions, start and due dates, start and due times, priorities, and categories.
- Reject impossible schedules, such as a due date before the start date.
- Detect an edit made from an older browser copy and refresh instead of silently overwriting newer work.

### Organization and discovery

- Create color-coded categories and prevent duplicate category names for one owner.
- Remove a category without deleting its tasks.
- Search task titles and descriptions.
- Filter all, active, or completed tasks.
- Review total, active, and completed statistics.

### Calendar work

- View tasks as a focused day list.
- Place scheduled tasks into hourly cells in a seven-day week.
- Review due tasks in a month grid.
- Navigate by day, week, or month and create a task from a selected date/time.

### Reliability and accessibility

- See loading, empty, retry, validation, conflict, and network-failure states.
- Use labeled controls and keyboard workflows, including closing a dialog with Escape and restoring focus.
- Include a request ID in visible failures so an operation can be correlated with service logs.

## 3. System shape and request flow

```text
Browser
  React + TypeScript + TanStack Query
      |
      | HTTPS / JSON / Authorization: Bearer / X-Correlation-Id
      v
Express BFF
  browser-facing routes, aggregation, protocol forwarding
      |
      | private service HTTP
      v
Spring Boot API
  authentication, validation, ownership, business rules
      |
      | JPA / JDBC
      v
PostgreSQL
  users, categories, tasks, versions
```

Render terminates TLS at the public edge. The browser talks to a stable BFF boundary, the BFF forwards or composes requests, Spring remains the business and authorization source of truth, and PostgreSQL remains the persistent source of truth.

The separation is deliberate:

- Presentation and browser state stay in React.
- Browser-specific aggregation and upstream adaptation stay in Express.
- Security, validation, and business rules stay in Spring services.
- Data access stays in repositories and schema changes stay in Flyway.

The cost is operational complexity: three application processes and a database must be built, tested, configured, and observed. The benefit is that each boundary demonstrates a distinct responsibility and can evolve or be tested independently.

## 4. Critical system behavior

### Login and protected requests

```text
Login form -> frontend api.ts -> BFF -> AuthController -> AuthService
                                                      -> UserRepository
                                                      -> BCrypt comparison
                                                      -> JwtService
JWT + display identity <- frontend <- BFF <- AuthResponse
browser stores JWT and display identity in localStorage
```

For a protected request:

```text
Browser sends Authorization: Bearer <JWT>
  -> BFF requires/preserves bearer token
  -> JwtAuthenticationFilter validates signature and expiry
  -> Spring Security establishes the principal
  -> CurrentUserService resolves the persisted user
  -> service/repository performs an owner-scoped operation
```

Missing, invalid, or expired authentication stops before domain work. Login failure issues no token. Cross-owner identifiers behave as missing resources rather than revealing that another user's object exists.

### Editing a task successfully

```text
TaskForm / completion control
  -> PUT task JSON including version=4
  -> frontend api.ts adds bearer token + correlation ID
  -> BFF forwards method, token, ID, content type, and body
  -> TaskController validates the DTO
  -> TaskService resolves current user
       -> owner-scoped task lookup
       -> compare client version
       -> validate schedule
       -> owner-scope optional category
       -> update entity and flush transaction
  -> PostgreSQL persists the update; version becomes 5
  -> TaskResponse crosses Spring -> BFF -> React cache
```

### Optimistic-lock conflict

```text
Initial database task: version 7

Browser A reads 7                 Browser B reads 7
Browser A saves 7
database becomes 8
                                  Browser B tries to save 7
                                  -> version mismatch / optimistic failure
                                  -> 409 Conflict; no overwrite
                                  -> BFF preserves error
                                  -> React refetches bootstrap
                                  -> user reviews current version and retries
```

Optimistic locking was chosen because simultaneous edits are expected to be uncommon, no database lock must survive an HTTP think-time gap, and versioned requests fit stateless HTTP naturally. The cost is explicit client conflict handling and the possibility that a user must repeat an edit. Pessimistic locking would add lock duration, timeout, and availability problems for little current benefit.

### Conditional task-list read

```text
First request
GET /api/tasks
  -> query + serialize signed-in user's tasks
  -> 200 OK, ETag: "abc123", private revalidation policy
  -> browser may retain the representation

Later request
GET /api/tasks
If-None-Match: "abc123"
  -> BFF forwards validator
  -> Spring queries, serializes, and hashes current representation
  -> hash equal? yes: 304, no body
                 no: 200, new JSON + new ETag
```

This reduces transferred bytes when data is unchanged. It currently does not avoid the database query or JSON serialization required to compute the hash.

### Bootstrap read

```text
React useQuery -> GET /api/bootstrap -> BFF
                                     -> GET Spring /tasks      --+
                                     -> GET Spring /categories --+ in parallel
                                     -> combine both JSON results
                                     -> React stores one BootstrapResponse
```

The aggregate simplifies browser startup. If either dependency read fails, the whole bootstrap fails; partial initial state is intentionally not presented.

## 5. Repository map

| Unit | Purpose | Standout feature |
| --- | --- | --- |
| `frontend/` | Browser UI and client state | Accessible calendar UI with indexed task projection |
| `bff/` | Browser-facing API | Typed OpenAPI consumption and bootstrap aggregation |
| `backend/` | Domain API | Owner-scoped security and optimistic locking |
| `backend/.../db/migration/` | Database history | Repeatable, immutable Flyway evolution |
| `benchmark/` | Performance investigation | Reproducible HTTP load plus SQL-plan evidence |
| `.github/workflows/toodle-ci.yml` | CI pipeline | Cross-layer contract and container verification |
| `docs` content in this file | Design and operations knowledge | One maintained source of truth |
| root configuration | Local/production orchestration | Health-ordered four-service stack and Render blueprint |

Generated dependencies (`node_modules/`, `.m2/`), build output (`dist/`, `target/`), and the generated OpenAPI TypeScript file are not hand-maintained architecture units.

## 6. Documentation unit

| File | Purpose |
| --- | --- |
| `README.md` | Concise public entry point: product summary, use cases, architecture, key engineering aspects, setup, verification, endpoints, and resume summary. |
| `PROJECT_REFERENCE.md` | Authoritative technical reference: complete unit/file map, principles, rationale, tradeoffs, operations, evidence, limitations, and project history. |

The project intentionally keeps only these two Markdown documents. The previous project plan, source guide, API compatibility note, two deployment notes, benchmark README, and web-fundamentals note repeated overlapping context and made it unclear which document was current. Their unique material has been migrated here.

This strategy gives readers a short path and a complete path while reducing documentation drift. Its drawback is that this reference is long and must be updated whenever responsibilities, commands, metrics, or policies change. Use headings and file tables for navigation; do not create another topic-specific Markdown file unless that content has a genuinely independent lifecycle that cannot remain clear here.

Standout feature: documentation mirrors the architecture while remaining a single source of truth, including honest implementation drawbacks rather than only feature claims.

## 7. Frontend unit

### Responsibility and design

`frontend/` is a React and TypeScript single-page application built with Vite. TanStack Query owns remote bootstrap data and refresh behavior; local React state owns view selection, search/filter input, open dialogs, and the current editing operation. The `tasks` and `calendar` folders are feature boundaries inside one deployable application, not independently deployed micro-frontends.

### Files

| File or folder | Implementation |
| --- | --- |
| `src/main.tsx` | Browser entry point; mounts React and imports global styles. |
| `src/app/App.tsx` | Application shell; coordinates session restoration, TanStack Query bootstrap state, navigation, filters, modal state, mutations, optimistic-lock conflict refresh, and focus restoration. |
| `src/app/App.test.tsx` | Integrated application behavior tests. |
| `src/components/AuthForm.tsx` | Registration/login form, session persistence, validation, submission, and error UI. |
| `src/components/AuthForm.test.tsx` | Authentication success and failure behavior. |
| `src/components/TaskForm.tsx` | Create/edit dialog with schedule, priority, and category controls. |
| `src/components/TaskForm.test.tsx` | Task creation/editing behavior and validation. |
| `src/components/TaskCard.tsx` | Reusable task summary with completion, edit, and delete actions. |
| `src/components/CategoryPicker.tsx` | Category selection and inline category creation. |
| `src/components/StatsPanel.tsx` | Total, active, and completed task summary. |
| `src/components/accessibility.test.tsx` | axe-based detectable accessibility checks. |
| `src/features/tasks/types.ts` | Client domain types for tasks, categories, drafts, filters, and calendar views. |
| `src/features/tasks/api.ts` | Only browser HTTP adapter; attaches JWT and correlation ID, maps request shapes, handles structured errors, and clears invalid sessions. |
| `src/features/tasks/api.test.ts` | Correlation-ID and structured-error client tests. |
| `src/features/tasks/taskUtils.ts` | Pure date, schedule, matching, filtering, and sorting functions. |
| `src/mfe/tasks/TasksMfe.tsx` | Task statistics, status filters, and search controls. |
| `src/mfe/calendar/CalendarMfe.tsx` | Calendar navigation and composition of day/week/month views. |
| `src/mfe/calendar/CalendarMfe.test.tsx` | View-aware period navigation tests. |
| `src/views/DayView.tsx` | Day task list and contextual empty states. |
| `src/views/WeekView.tsx` | Seven-day/hour grid; memoizes a date/hour task index for constant-time cell lookup. |
| `src/views/MonthView.tsx` | Month grid; memoizes a due-date task index and caps visible tags per day. |
| `src/styles.css` | Product palette, typography, responsive layouts, states, dialogs, calendar grids, and CSS illustrations. |
| `src/test/setup.ts` | Shared Vitest/Testing Library browser-test setup. |
| `src/vite-env.d.ts` | Vite-provided browser and environment-variable type declarations. |
| `e2e/accessibility.spec.ts` | Playwright keyboard and focus workflow. |
| `public/icons/icon.svg` | Product favicon/source icon. |
| `public/robots.txt` | Search-crawler policy. |
| `index.html` | HTML shell, metadata, icons, and external font/icon resources. |
| `nginx.conf` | Production static server, SPA fallback, BFF proxy, forwarded headers, and immutable hashed-asset caching. |
| `vite.config.ts` | Vite build/development configuration. |
| `vitest.config.ts` | Vitest browser-like test configuration. |
| `playwright.config.ts` | End-to-end browser configuration. |
| `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json` | Shared, browser, and tooling TypeScript boundaries. |
| `package.json`, `package-lock.json` | Reproducible Node dependencies and frontend scripts. |
| `Dockerfile` | Multi-stage production build served by Nginx. |

### Principles, choices, advantages, and drawbacks

- **Component composition:** views and reusable controls have clear UI ownership. This improves focused testing, but `App.tsx` is still a large coordinator and would need further extraction if workflows grow.
- **TanStack Query instead of Redux:** server data already has cache/refetch semantics, while UI state is small. This avoids duplicate global-state machinery, but client mutations currently update the aggregated bootstrap cache manually.
- **Single API adapter:** token, correlation, mapping, and error behavior are consistent. The drawback is that one adapter can become broad as endpoints grow.
- **Browser token storage:** `localStorage` makes a stateless portfolio deployment simple. It is accessible to JavaScript, so XSS prevention and CSP are important; a production system with stronger session requirements should evaluate secure, HttpOnly cookies and CSRF protection.
- **Accessible native controls:** semantic buttons, labels, dialogs, Escape handling, and focus restoration improve keyboard behavior. Automated checks cannot replace manual assistive-technology review.
- **Memoized task indexes:** week projection changed from 168 scans of the task list to one index plus 168 lookups; month projection changed from up to 42 scans to one index plus cell lookups. With 500 tasks that is approximately 84,000 to 668 week operations and 21,000 to 542 month operations, excluding DOM creation. The index uses additional memory and rebuilds whenever the task-array identity changes.

Standout feature: the frontend combines a polished calendar workflow with explicit accessibility and a measured data-projection optimization without adding unjustified virtualization complexity.

## 8. BFF unit

### Responsibility and design

`bff/` is a Node.js/Express backend-for-frontend. It gives the browser one stable API origin, requires bearer authentication on protected routes, forwards task/category operations, combines tasks and categories in `/api/bootstrap`, and maps Spring unavailability to a stable `502`.

It does not own persistence, validation rules, or authorization decisions. Those remain in Spring to prevent duplicated business behavior.

### Files

| File | Implementation |
| --- | --- |
| `src/app.ts` | Testable Express factory; CORS, browser security headers, correlation IDs, request logging, health, bootstrap aggregation, protected proxy routes, conditional-header forwarding, upstream response forwarding, and stable network errors. |
| `src/app.test.ts` | Health, private-address resolution, bootstrap, authentication forwarding, correlation IDs, conditional GET/cache headers, security headers, upstream errors, and network failure tests. |
| `src/server.ts` | Process entry point and configured HTTP listener. |
| `src/instrumentation.ts` | OpenTelemetry initialization before application modules load. |
| `src/generated/spring-api.ts` | Generated TypeScript representation of Spring's OpenAPI contract; never edited manually. |
| `package.json`, `package-lock.json` | Express/OpenTelemetry dependencies and dev, test, type-check, and contract-generation scripts. |
| `tsconfig.json` | Strict TypeScript configuration. |
| `Dockerfile` | Production BFF image. |

### Principles, choices, advantages, and drawbacks

- **Backend-for-frontend pattern:** simplifies the browser and creates a place for UI-specific composition. It adds a network hop and another service to operate.
- **Thin proxy boundary:** avoids two sources of business truth. It also means the BFF depends strongly on Spring availability and contract stability.
- **Parallel bootstrap composition:** tasks and categories load concurrently, reducing browser coordination. A partial upstream failure fails the aggregate response rather than returning partial data.
- **Generated contract types:** Spring changes become visible during the BFF build. Generated types protect compile-time structure but do not replace runtime integration tests.
- **Protocol preservation:** `If-None-Match`, `ETag`, `Cache-Control`, `Vary`, content type, authorization, and correlation IDs survive the hop. Maintaining an explicit allowlist avoids blindly forwarding unsafe headers but requires updates when new protocol metadata is added.

Standout feature: the BFF is both an independently testable adapter and a checked consumer of the Spring-generated contract.

## 9. Spring Boot application unit

### Responsibility and layers

`backend/` is a Java 17 Spring Boot application. Controllers define HTTP, services own business transactions and current-user rules, repositories own database access, entities represent persistence, DTOs protect the public contract, and security/exception packages implement cross-cutting boundaries.

### Entry and configuration

| File | Implementation |
| --- | --- |
| `ToodleApplication.java` | Spring Boot application entry point. |
| `config/OpenApiConfig.java` | API metadata and bearer-auth OpenAPI scheme. |
| `pom.xml` | Spring Boot, Security, JPA, validation, Actuator, Flyway, PostgreSQL, JWT, OpenTelemetry, OpenAPI, H2, and Testcontainers dependencies plus Java/build configuration. |
| `maven-settings.xml` | Project-local Maven repository location for constrained environments. |
| `application.yml` | Shared port, Jackson strictness, datasource/JPA, JWT, telemetry privacy/sampling, health exposure, application info, and correlation-aware logging. |
| `application-production.yml` | Production datasource/secrets, reduced log noise, and reverse-proxy forwarded-header handling. |
| `Dockerfile` | Multi-stage Spring production image. |
| `compose.yaml` | Local PostgreSQL 16 service, persistence volume, port, and health check. |

### Controllers and HTTP contract

| File | Implementation |
| --- | --- |
| `controller/AuthController.java` | Public registration and login routes and created/success statuses. |
| `controller/TaskController.java` | Authenticated task CRUD, validation, strong SHA-256 list ETags, private revalidation policy, `Vary: Authorization`, and conditional `304` handling. |
| `controller/CategoryController.java` | Authenticated category CRUD. |

`GET /api/tasks` uses a representation ETag. A browser may retain the response because it is `private`, but `no-cache, must-revalidate` requires validation before reuse. `If-None-Match` returns a bodyless `304` when the signed-in user's representation is unchanged. Mutations and authentication responses do not receive this cache policy.

### Services

| File | Implementation |
| --- | --- |
| `service/AuthService.java` | Normalizes identity, rejects duplicate email, hashes passwords, verifies credentials, and issues JWT responses. |
| `service/CurrentUserService.java` | Resolves the authenticated principal to the persisted user. |
| `service/TaskService.java` | Owner-scoped task operations, schedule validation, category ownership validation, entity mapping, and optimistic-lock conflict behavior. |
| `service/CategoryService.java` | Owner-scoped categories, normalized/case-insensitive uniqueness, updates, and safe deletion that clears task associations. |

### Repositories

| File | Implementation |
| --- | --- |
| `repository/UserRepository.java` | Email identity lookups and duplicate detection. |
| `repository/TaskRepository.java` | Owner-scoped task lists/lookups and category association operations. |
| `repository/CategoryRepository.java` | Owner-scoped category lists/lookups and case-insensitive name checks. |

Owner identity is part of repository queries rather than a post-query filter. This provides defense in depth and prevents accidentally returning another user's entity from a broad lookup.

### Models

| File | Implementation |
| --- | --- |
| `model/AppUser.java` | User identity, BCrypt hash, creation timestamp, and owned relationships. |
| `model/Category.java` | Owner-scoped category name/color entity. |
| `model/Task.java` | Task schedule/content, category, owner, creation time, completion state, and JPA version. |
| `model/Priority.java` | Valid priority values and representation mapping. |

### DTOs

| File | Implementation |
| --- | --- |
| `dto/RegisterRequest.java` | Validated registration input. |
| `dto/LoginRequest.java` | Validated credential input. |
| `dto/AuthResponse.java` | Token and display identity response. |
| `dto/TaskRequest.java` | Validated writable task fields and client version. |
| `dto/TaskResponse.java` | Stable task representation, including normalized priority/category/version fields. |
| `dto/CategoryRequest.java` | Validated category name/color input. |
| `dto/CategoryResponse.java` | Stable category representation. |

DTO separation prevents clients from setting protected entity fields such as owner IDs and allows persistence details to change without automatically changing JSON.

### Security and errors

| File | Implementation |
| --- | --- |
| `security/SecurityConfig.java` | Stateless Spring Security chain, public/protected route rules, CORS, BCrypt, JSON authentication/authorization errors, HSTS, CSP, framing, and content-type headers. |
| `security/JwtService.java` | HMAC token creation, expiration, signing, parsing, and subject validation. |
| `security/JwtAuthenticationFilter.java` | Bearer extraction, token validation, principal installation, and invalid-token behavior. |
| `security/CorrelationIdFilter.java` | Validates or generates request IDs, attaches logging context, returns the header, and records request summaries. |
| `exception/ApiError.java` | Stable error envelope with status, code, message, path, timestamp, and correlation ID. |
| `exception/ApiExceptionHandler.java` | Maps validation, malformed JSON, conflicts, missing resources, and other failures to HTTP responses. |
| `exception/ResourceNotFoundException.java` | Domain signal for absent or inaccessible owner-scoped resources. |

### Principles, choices, advantages, and drawbacks

- **Layered architecture:** controllers stay protocol-focused and services stay domain-focused. More classes and mapping code are required than in a small CRUD application.
- **Stateless JWT:** horizontally scalable authentication without server sessions. Revocation is not immediate, and browser storage requires careful XSS mitigation.
- **Owner-scoped access:** strong tenant isolation and non-enumerating `404` behavior. Every new query must preserve the owner condition.
- **Optimistic locking:** prevents lost updates without long database locks. Clients must carry versions and handle `409 Conflict` explicitly.
- **Strict JSON DTOs:** unknown/protected fields fail rather than being ignored. This improves security and catches mistakes, but makes additive client experimentation less forgiving.
- **Representation hashing:** a correct validator changes whenever returned JSON changes. It requires serializing the list to calculate the digest, so it saves transfer bandwidth rather than database/query/serialization CPU; a database aggregate version could be evaluated at much larger scale.
- **Platform TLS termination:** certificates and cryptography stay with the deployment edge. Correct forwarded-header trust and edge configuration become operational requirements.

Standout feature: security, concurrency, HTTP semantics, and data ownership are enforced together through real HTTP integration tests rather than existing only as framework configuration.

### Security and threat model

**Assets:** password hashes, JWTs, private tasks/categories, user identities, database credentials, JWT signing material, and deployment secrets.

| Threat | Primary protection | Residual consideration |
| --- | --- | --- |
| User A accesses User B's record | Owner-scoped repositories and same-owner category validation | Every new query must preserve owner scope. |
| JWT tampering or expired-token reuse | HMAC signature and expiry validation in Spring Security | Stateless tokens cannot be immediately revoked without adding server state. |
| Password disclosure | BCrypt hashes; passwords never enter responses/traces | Credential strength/rate limiting would need further production policy. |
| XSS steals browser token | React escaping, strict DTO boundaries, CSP/security headers | JWT is in `localStorage` and remains readable by successful injected JavaScript. |
| SQL injection | Spring Data/JPA parameter binding | Native/dynamic queries must continue using parameters. |
| CORS mistaken for authorization | Exact allowed origins plus real JWT authorization | Non-browser clients ignore CORS; authorization must never depend on it. |
| Mass assignment | Explicit request DTOs and unknown-field rejection | New writable fields require deliberate DTO review. |
| Malformed/hostile JSON | validation, strict Jackson parsing, stable errors | Request-size/rate limits belong at the production edge. |
| Secret leakage | environment/managed secrets and Git ignores | Rotation and access-control procedures must be exercised after deployment. |
| Sensitive telemetry | explicit capture exclusions and sanitized JDBC instrumentation | Collector/exporter configuration must be reviewed in the live environment. |

Security is defense in depth: CORS and headers reduce browser attack surface, while authentication plus owner-scoped authorization protects the data. A `404` for a cross-owner identifier intentionally avoids confirming that the resource exists.

## 10. Database and migration unit

### Current entity relationship model

```text
app_user
  id (PK)
  name
  email (unique)
  password_hash
  created_at
      | 1
      +------------------< task.owner_id *
      |                      task
      |                      id (PK)
      |                      owner_id (FK)
      |                      category_id (nullable FK)
      |                      title / description
      |                      start_date / start_time
      |                      due_date / due_time
      |                      priority / completed
      |                      created_at / version
      |
      +------------------< category.owner_id *
                             category
                             id (PK)
                             owner_id (FK)
                             name / color
                                  | 1
                                  +------------< task.category_id *
```

- One user owns many tasks.
- One user owns many categories.
- One category can organize many tasks.
- One task belongs to zero or one category.
- Deleting a user cascades to owned tasks/categories; deleting a category clears the task association rather than deleting the task.

### Files and schema evolution

| File | Implementation |
| --- | --- |
| `V1__create_task_schema.sql` | Creates category/task tables, schedules, priority/completion fields, category foreign key, and category/date indexes. |
| `V2__create_user_schema.sql` | Creates users, adds user ownership to tasks/categories, cascading user deletion, and owner indexes. |
| `V3__add_task_version.sql` | Adds the non-null version used by JPA optimistic locking. |

Flyway treats migration bytes as permanent history. Never edit an applied migration; add the next numbered migration. A previous checksum failure caused by comment edits demonstrated why this rule matters.

Advantages include reproducible environments, reviewable schema changes, startup validation, and the ability for Testcontainers to exercise the production schema history. Drawbacks include the need for backward-compatible rollout design and corrective forward migrations rather than rewriting history.

Standout feature: persistence evolution and application concurrency control are joined through the V3 version column and a tested stale-client workflow.

## 11. Tests unit

### Files and coverage

| File | Coverage |
| --- | --- |
| `backend/src/test/java/com/toodle/TaskControllerTest.java` | Real PostgreSQL/Flyway HTTP integration: auth, CRUD, owner isolation, validation, categories, security headers, correlation IDs, optimistic locking, ETags, cache policy, and `304`. |
| `backend/src/test/java/com/toodle/JwtServiceTest.java` | Token expiration behavior. |
| `backend/src/test/java/com/toodle/OpenApiContractTest.java` | Exports the live Spring OpenAPI document for downstream type checks. |
| `backend/src/test/resources/application.yml` | Isolated test configuration and telemetry suppression. |
| `bff/src/app.test.ts` | Express route, forwarding, aggregation, security-header, caching, and failure tests using injected fetch. |
| `frontend/src/**/*.test.ts(x)` | Component, application, navigation, client API, and accessibility tests. |
| `frontend/e2e/accessibility.spec.ts` | Real Chromium keyboard/focus workflow. |

The suite contains 20 backend tests, 11 BFF tests, 14 frontend component tests, and one Playwright workflow.

Testing uses the smallest appropriate boundary: pure/component tests for UI behavior, injected upstream fetch for the BFF, MockMvc plus PostgreSQL Testcontainers for Spring, contract export for cross-service compatibility, and Playwright for browser focus behavior.

The main drawback is runtime and environment cost: Docker is required for backend integration tests and Chromium is required for E2E. This is intentional because H2-only or mocked tests cannot prove PostgreSQL migrations and complete browser behavior.

### Guarantee-to-test traceability

`Yes` means that layer has a focused assertion for the behavior; `Path` means it participates in a larger integration test; `—` means the claim is not tested at that layer.

| Guarantee | Frontend | BFF | Spring HTTP | PostgreSQL | Browser E2E |
| --- | :---: | :---: | :---: | :---: | :---: |
| Login/error behavior | Yes | Path | Yes | Path | Path |
| Owner isolation | — | Path | Yes | Yes | — |
| Schedule validation | Yes | Path | Yes | Path | — |
| Stale-write recovery/no overwrite | Yes | Path | Yes | Yes | — |
| Correlation IDs | Yes | Yes | Yes | — | — |
| Conditional task caching | — | Yes | Yes | Path | — |
| OpenAPI consumer compatibility | — | Yes | Yes | — | — |
| Keyboard dialog/focus behavior | Yes | — | — | — | Yes |
| Security headers and CORS | — | Yes | Yes | — | — |
| Flyway/JPA compatibility | — | — | Yes | Yes | — |

This table is more important than raw test count: it identifies which architectural claims are proven and where a future change needs coverage.

Standout feature: tests cover not only happy-path CRUD but architectural properties—ownership, contract compatibility, conditional HTTP, stale writes, request correlation, and keyboard focus.

## 12. HTTP and API contract unit

Spring's generated OpenAPI document is the source of truth. `OpenApiContractTest` writes `backend/target/openapi.json`; `npm run generate:api-types` generates `bff/src/generated/spring-api.ts`; `npm run check:api-types` fails when the committed generated type no longer matches.

```text
Spring controller + DTO
        -> generated OpenAPI
        -> backend/target/openapi.json
        -> openapi-typescript
        -> bff/src/generated/spring-api.ts
        -> BFF type checking

Java DTO changes without regenerated TypeScript
        -> CI exports the new contract
        -> generated-file difference detected
        -> build fails until consumer and generated type agree
```

Compatible v1 changes include new endpoints, optional fields/parameters, new error responses, or relaxed validation that preserves meaning. Breaking changes include removing/renaming endpoints or fields, changing types/meaning/auth/statuses, making optional input required, or strengthening validation against previously valid requests.

A breaking change requires a new route such as `/api/v2` and a migration window. Every contract change must include the Spring controller/DTO and tests, OpenAPI export, regenerated BFF types, consumer updates, and passing CI. Never hand-edit the generated file.

Advantage: compile-time drift detection across Java and TypeScript. Drawback: generation order matters and semantic compatibility still needs human review. Standout feature: the producer owns the contract while CI verifies the consumer.

### Toodle status-code dictionary

| Code | Meaning in Toodle |
| ---: | --- |
| `200` | Successful read, login, or update with a representation. |
| `201` | Registration, task, or category created. |
| `204` | Delete succeeded and intentionally has no body. |
| `304` | The authenticated cached task representation is still current; reuse its body. |
| `400` | JSON is malformed/unsupported or validated application input is invalid. |
| `401` | Authentication is absent, invalid, expired, or login credentials fail. |
| `403` | An authenticated principal is not permitted by the security policy. |
| `404` | Resource is absent or deliberately indistinguishable because it belongs to another user. |
| `409` | Duplicate/state/concurrency conflict, including a stale task version. |
| `502` | The BFF could not reach Spring. |
| `503` | A service or dependency is not ready/healthy. |

`401` asks for valid authentication; `403` means the known principal is forbidden; `404` avoids exposing existence across owner boundaries; `409` means authentication and targeting succeeded but current state conflicts with the requested change.

## 13. CI unit

The Toodle workflow is stored at repository level in `.github/workflows/toodle-ci.yml`, one directory above this project folder. It runs only when Toodle or its workflow changes.

The single verification job:

1. Checks out source and installs Node 24 and Java 17 with dependency caching.
2. Installs, tests, and builds the frontend.
3. Installs Chromium and runs keyboard E2E tests.
4. Runs Maven tests and exports OpenAPI.
5. Installs/tests the BFF and checks generated API types.
6. Builds production Docker images with CI-only secrets.

Using one ordered job guarantees the backend contract exists before the BFF check. It is simpler and makes the cross-layer dependency explicit, but offers less parallelism than separate jobs. Container builds catch Dockerfile/config drift after language-level tests.

`.github/copilot-instructions.md` inside Toodle records contributor architecture, ownership, security, comment, and verification rules. It is guidance, not executable CI.

Standout feature: CI verifies source, browser behavior, real PostgreSQL behavior, cross-language contract consistency, and deployable images in one gate.

## 14. Benchmark and scripts unit

| File | Implementation |
| --- | --- |
| `benchmark/run.mjs` | Creates a dedicated user, seeds eight categories and deterministic tasks through public HTTP, warms the stack, applies concurrent load, calculates latency/throughput/failures, and writes JSON. |
| `benchmark/db-profile.sql` | Runs `EXPLAIN ANALYZE` for the 500-row owner-scoped task join and reports planning, execution, buffers, rows, and plan/index behavior. |
| `benchmark/results/baseline.json` | Recorded telemetry-heavy baseline. |
| `benchmark/results/optimized.json` | Recorded sampled-telemetry result under the same workload. |

Default workload: 500 tasks, 20 concurrent clients, 30 measured seconds. Baseline throughput was 8.61 requests/second with 5,019 ms p95 and zero failures. PostgreSQL executed the profiled query in 3.07 ms, pointing away from the query plan. Changing trace export from 100% to 10% parent-based sampling and disabling unused OTLP metrics/log export produced 12.16 requests/second and 2,647 ms p95 with zero failures: 41.23% higher throughput and 47.27% lower p95 on the test machine.

Run from the Toodle folder:

```powershell
$env:POSTGRES_PASSWORD="local-benchmark-password"
$env:JWT_SECRET="local-benchmark-jwt-secret-that-is-long-enough"
docker compose -f compose.production.yaml --profile benchmark run --rm benchmark
docker compose -f compose.production.yaml --profile benchmark run --rm benchmark-db-profile
```

Optional workload variables are `BENCHMARK_TASKS`, `BENCHMARK_CONCURRENCY`, `BENCHMARK_DURATION_SECONDS`, and `BENCHMARK_SEED_CONCURRENCY`. Compare versions on the same machine/resources, run at least three repetitions, and compare median results. Local evidence is not universal production capacity.

Advantages: reproducibility, real public HTTP, database evidence, and committed before/after results. Drawbacks: local hardware/Docker noise and a deliberately narrow read-heavy workload. Standout feature: SQL evidence ruled out an intuitive database diagnosis before telemetry was optimized.

## 15. Infrastructure and deployment unit

### Files

| File | Implementation |
| --- | --- |
| `compose.production.yaml` | PostgreSQL, Spring, BFF, frontend, health-ordered dependencies, persistent data, telemetry configuration, benchmark profiles, and public port 8088. |
| `render.yaml` | Managed PostgreSQL, private Spring, public BFF, static frontend, environment/secrets, health checks, checks-pass deployment gating, TLS-facing URLs, and frontend security headers. |
| `.env.example` | Non-secret names/example values required by local production Compose. |
| `.dockerignore` | Excludes dependencies, build products, secrets, and irrelevant content from Docker contexts. |
| `.gitignore` | Excludes dependencies, Maven caches, builds, coverage, secrets, logs, editors, and transient benchmark output. |

Each application folder also owns its Dockerfile because build knowledge belongs beside the runtime it packages.

### Runtime topologies

Development:

```text
Browser -> localhost:5173 Vite/React
        -> localhost:3000 Express BFF
        -> localhost:8080 Spring
        -> localhost:5433 PostgreSQL container
```

Production-style Compose:

```text
Browser -> :8088 Nginx/frontend container
        -> BFF container
        -> Spring container
        -> PostgreSQL container + persistent volume
```

**PREPARED — NOT YET DEPLOYED OR VERIFIED:**

```text
Internet -> HTTPS/TLS at Render edge
         -> Render static frontend
         -> public Render BFF
         -> private Render Spring service
         -> managed PostgreSQL
```

### Local production-style run

Create `.env` from `.env.example`, replace sample secrets, then run:

```powershell
docker compose -f compose.production.yaml up --build
```

Open `http://127.0.0.1:8088`.

### Cloud deployment status and procedure

`render.yaml` is prepared for paid resources: managed PostgreSQL, private Spring, public BFF, and static frontend. To deploy, connect Render to `megmem044/Portfolio`, create a Blueprint using `toodle/render.yaml`, review pricing, and apply it. Do not claim production deployment until the resources exist and the checks below pass.

### TLS and security boundary

The deployment platform terminates TLS and is expected to redirect HTTP to HTTPS. Spring uses `server.forward-headers-strategy: framework` so the external scheme is understood behind the proxy. Frontend, BFF, and Spring responses define HSTS, content-type, framing, and boundary-appropriate CSP policies. HSTS is effective only after a valid HTTPS response.

The JWT is sent in `Authorization`, not a cookie, so cookie attributes do not currently apply. A cookie-based design must use `Secure`, `HttpOnly`, intentional `SameSite`, and CSRF protection.

### Release and smoke checks

1. Back up PostgreSQL and record current immutable image tags.
2. Require a passing Toodle CI workflow.
3. Deploy database connectivity/Spring, wait for readiness, then BFF/frontend.
4. Verify HTTP-to-HTTPS redirects and valid certificates.
5. Register two users and test login/logout, task/category CRUD, completion, persistence after restart, owner isolation, invalid/expired tokens, cache revalidation, and correlation IDs.
6. Confirm HSTS/CSP/security headers and production tracing without sensitive values.
7. Run Lighthouse and manual WCAG review.

### Rollback and recovery

On application failure, retain logs/request IDs and redeploy previous frontend/BFF/backend image tags. Do not automatically roll back the database; migrations must remain compatible with the previous application during rollout.

Use encrypted managed backups and point-in-time recovery. Restore into an isolated database, validate Flyway history, counts, login, ownership, and recent records, then switch the backend. Rotate `JWT_SECRET` after exposure (signing users out) and rotate database credentials after exposure. Document provider retention, RPO, RTO, restore commands, and ownership before launch.

Advantages: immutable containers, private networking, managed secrets/database, health ordering, and infrastructure as code. Drawbacks: paid resources, four-service operational overhead, provider-specific TLS/network behavior, and an as-yet unverified live environment. Standout feature: deployment claims are deliberately separated from deployment preparation.

### Failure-mode and recovery matrix

| Failure | User-visible result | System behavior | Recovery |
| --- | --- | --- | --- |
| Invalid credentials | Login error | No JWT issued | Correct credentials and retry. |
| Missing/expired/invalid JWT | Authentication error; session cleared by client on protected failure | Request rejected before domain work | Sign in again. |
| Cross-owner task/category ID | Not found | Owner-scoped query returns no entity | No recovery; use an owned resource. |
| Invalid schedule/body | Validation error | No persistence | Correct fields/body. |
| Duplicate user/category | Conflict message | Existing state preserved | Choose unique value. |
| Stale task edit | Conflict and refreshed task list | `409`; newer data is not overwritten | Review current task and repeat edit. |
| Spring unreachable | Stable service error | BFF returns `502` | Restore Spring/network, then retry. |
| PostgreSQL unavailable | Application unavailable/readiness failure | Spring cannot serve data and readiness fails | Restore/fail over database and verify data. |
| BFF unavailable | Browser API failure | Browser cannot reach server boundary | Restart/roll back BFF. |
| OpenAPI drift | CI/build failure | Inconsistent producer/consumer cannot merge | Regenerate types and update consumer/tests. |
| Failed Flyway migration | Spring startup/readiness failure | Flyway stops unsafe schema startup | Add/fix a forward migration; do not rewrite applied history. |
| Bad release | Failed smoke checks | Traffic should not remain on release | Roll back application images, retain DB migration compatibility. |
| Exposed signing/database secret | Security incident | Trust boundary compromised | Rotate secret/credentials and redeploy; JWT rotation signs users out. |

## 16. Observability unit

The browser creates `X-Correlation-Id`; Express validates or replaces it and logs method/path/status; Spring carries it into MDC logs and response errors. OpenTelemetry covers BFF HTTP, Spring MVC, and JDBC spans with parent-based 10% production sampling.

```text
Browser generates correlation ID
  -> Express validates ID, logs request, forwards ID
  -> Spring puts ID in MDC and response/error envelope
  -> Spring MVC and JDBC spans remain linked by trace context
  -> PostgreSQL operation is visible as a database span

User reports request ID abc-123
  -> search BFF logs for abc-123
  -> follow Spring log/span
  -> inspect associated JDBC span and response status
```

Authorization, passwords, tokens, bodies, database values, and request/response headers are excluded from trace capture. BFF `/health` reports Spring dependency health; Spring Actuator exposes liveness/readiness/info with database readiness.

Advantages: one failure can be followed across layers and sampling controls cost. Drawbacks: logs/traces still need a real collector and retention/query system in production, and sampling can omit individual traces. Standout feature: the performance benchmark measured and corrected observability overhead instead of treating telemetry as free.

## 17. Web fundamentals

### HTTP

- Correct status semantics include `201`, `204`, `304`, `400`, `401`, `403`, `404`, `409`, `502`, and `503`.
- Safe task-list reads use `ETag`/`If-None-Match`; authenticated representations use private revalidation, while Vite-hashed assets use long-lived public immutable caching.
- CORS allows configured browser origins; it is not used as authentication.
- Content negotiation remains JSON at the API boundaries.

### DOM and browser rendering

React maps domain state into semantic DOM. The calendar investigation found CPU work before DOM creation, so indexed data lookup was chosen over list virtualization. Virtualization remains deferred because month cells cap visible tags, week cells distribute tasks, and virtualization would complicate keyboard/accessibility behavior without current evidence that node count is the bottleneck.

To validate on consistent hardware, load 500 tasks, record day/week/month changes with React DevTools Profiler, and compare commit duration, scripting time, and rendered nodes. Operation counts prove the algorithmic reduction; browser profiling measures actual device impact.

### SSL/TLS and web servers

Nginx serves the built SPA and proxies local production API calls. Render serves the cloud static site and terminates TLS at the edge. Express and Spring trust only their configured deployment path and preserve relevant forwarded scheme/protocol behavior. Application code does not implement TLS cryptography.

## 18. Architecture decision records

These lightweight ADRs preserve decisions that should not be reversed accidentally.

| ADR | Context and decision | Alternative rejected | Consequence and reconsideration trigger |
| --- | --- | --- | --- |
| `ADR-001` Express BFF | Browser needs one stable boundary and an aggregated bootstrap; use a thin Express layer. | React calls Spring directly. | Adds a hop/service. Reconsider if it permanently provides no browser-specific value. |
| `ADR-002` Spring business authority | Keep validation, ownership, and domain rules exclusively in Spring services. | Duplicate rules in React/BFF. | One trustworthy rule set; client still duplicates friendly pre-validation. Do not reconsider without redefining service ownership. |
| `ADR-003` Optimistic locking | Concurrent edits are uncommon and HTTP is stateless; use task versions and `409`. | Long-lived pessimistic database locks or last-write-wins. | Clients handle conflicts. Reconsider for truly high-contention, transactional collaborative editing. |
| `ADR-004` Generated OpenAPI types | Java produces the contract; generate/check TypeScript in BFF CI. | Hand-maintained duplicate interfaces. | Generation order and committed output must stay current. Reconsider only if the contract authority/toolchain changes. |
| `ADR-005` Stateless JWT | Portfolio deployment benefits from session-free service instances. | Server-side session store/cookie. | Simple scaling but weak immediate revocation and localStorage XSS exposure. Reconsider for stronger session control. |
| `ADR-006` Owner filtering in repositories | Tenant separation must exist at data access, not after retrieval. | Fetch by ID then compare in controllers. | Safer non-enumerating access; every new query needs owner scope. |
| `ADR-007` Representation ETags | Demonstrate correct authenticated revalidation and reduce repeated payloads. | Always transfer `200` JSON or introduce a server cache. | Query/serialization still occur. Reconsider for aggregate-version validators at larger scale. |
| `ADR-008` 10% trace sampling | Full console telemetry dominated the measured workload. | Export every trace. | Lower overhead with incomplete trace coverage. Reconsider with collector capacity, error-based sampling, or different SLOs. |
| `ADR-009` PostgreSQL Testcontainers | Schema/JPA correctness must match production database behavior. | H2-only or mocked integration. | Slower tests and Docker requirement; retain while PostgreSQL is production storage. |
| `ADR-010` One React application | Feature boundaries help organization but do not need independent deployment. | Runtime micro-frontends. | Simpler build/runtime and shared state. Reconsider only with independently owned/released teams. |

### Why certain technologies are absent

| Technology/pattern | Why it is not used now | Reconsider when |
| --- | --- | --- |
| Redux | TanStack Query owns server state and local React state is small. Another state model would duplicate responsibility. | Complex cross-feature client-only state becomes difficult to coordinate. |
| WebSockets/SSE | Current workflows tolerate explicit refetch and do not require live collaboration. | Cross-device/tab real-time updates become a product requirement. |
| Redis | No measured cache/session/rate-limiting bottleneck requires distributed state. | Profiling identifies a workload it solves with clear invalidation semantics. |
| Kafka/message broker | Operations are synchronous and no durable asynchronous workflow exists. | Independent consumers, durable events, or asynchronous processing become real requirements. |
| Kubernetes | Four small services do not justify cluster/orchestration overhead. | Scale, availability, or organizational deployment needs exceed managed services/Compose. |
| Virtualized calendar DOM | Investigation found repeated lookup CPU first; fixed grids and capped month tags do not yet prove node pressure. | Browser profiling shows DOM nodes/paint—not lookup work—are the bottleneck. |

## 19. Safe-change guide

### Add a task field

1. Decide whether the field is persisted, writable, readable, cache-representation-relevant, and sensitive.
2. Add a new Flyway migration; never edit V1–V3.
3. Update `Task`, `TaskRequest` if writable, `TaskResponse` if readable, and `TaskService` mapping/rules.
4. Update Spring integration tests and export OpenAPI.
5. Regenerate BFF types; change BFF only if composition/protocol behavior changes.
6. Update frontend `Task`/`TaskDraft`, request mapping, form/display, and focused tests.
7. Run backend -> BFF -> frontend/E2E -> container verification in dependency order.
8. Update this reference and README if the field changes a key user or engineering capability.

### Add or change an endpoint

```text
controller + DTO
  -> service/repository and migration if needed
  -> Spring HTTP/integration test
  -> OpenAPI export
  -> generated BFF type
  -> BFF route/aggregation + test
  -> frontend api.ts
  -> UI behavior + tests
  -> CI + documentation
```

Before changing an existing endpoint, classify the change using the compatibility policy. A breaking change needs versioning/migration, not a silent v1 replacement.

### Change authentication or owner behavior

Trace `SecurityConfig` -> `JwtAuthenticationFilter`/`JwtService` -> `CurrentUserService` -> service -> repository. Re-run missing/invalid/expired-token and two-user isolation tests. Review CORS, browser session clearing, error statuses, OpenAPI security requirements, telemetry exclusions, and `INV-01`, `INV-02`, `INV-05`, and `INV-09`.

### Change caching or proxy headers

Update Spring response/request semantics and BFF request/response allowlists together. Assert `200`, validator change, `304` empty body, private cache policy, `Vary`, and CORS-exposed headers. Review whether the data is authenticated or safe for shared storage.

### Change-impact matrix

| Change | Java | DB | Flyway | OpenAPI | BFF | React | Tests/docs |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Add persisted task field | Yes | Yes | Yes | Yes | Maybe | Yes | Yes |
| Add category endpoint | Yes | Maybe | Maybe | Yes | Yes | Yes | Yes |
| Change JWT claim/session behavior | Yes | Maybe | Maybe | Yes | Maybe | Yes | Yes |
| Change cache policy/header | Yes | No | No | Maybe | Yes | Maybe | Yes |
| Change correlation header | Yes | No | No | Maybe | Yes | Yes | Yes |
| Change database constraint | Yes | Yes | Yes | Maybe | Maybe | Maybe | Yes |
| Change BFF bootstrap shape | Maybe | No | No | Maybe | Yes | Yes | Yes |
| Change calendar rendering only | No | No | No | No | No | Yes | Yes |

## 20. Key project aspects and interview material

### Resume heading

**Toodle | Full-Stack Task and Calendar Platform**

**Technologies:** React, TypeScript, TanStack Query, Express, Spring Boot, Spring Security, PostgreSQL, Flyway, Docker, OpenAPI, OpenTelemetry, Testcontainers, Playwright, Vitest, GitHub Actions, Render

### Strong points

- Designed a four-layer task/calendar platform with React, Express BFF, Spring Boot, and PostgreSQL, supporting JWT authentication, user-owned data, categories, search, filters, and day/week/month scheduling.
- Prevented lost updates with JPA optimistic locking and tested `409 Conflict` recovery rather than overwriting newer data.
- Generated TypeScript API types from Spring OpenAPI and enforced consumer compatibility in CI.
- Proved tenant isolation with owner-scoped queries and real PostgreSQL HTTP integration tests.
- Implemented conditional authenticated reads using strong ETags, `If-None-Match`, `304`, private cache-control, and BFF protocol preservation.
- Defined the modern TLS boundary with edge termination, forwarded-protocol handling, HSTS, CSP, content-type, and framing protections.
- Reduced 500-task calendar projection work from 84,000 to roughly 668 week operations and 21,000 to roughly 542 month operations using memoized indexes.
- Added end-to-end request IDs and sampled OpenTelemetry across Express, Spring MVC, and JDBC while excluding sensitive data.
- Built a reproducible load benchmark and used SQL profiling to rule out the database, improving local throughput 41.23% and p95 47.27% through telemetry changes.
- Automated accessibility checks and keyboard focus workflows, fixed a manually discovered mobile defect, and recorded Lighthouse scores of 100 for Accessibility, Best Practices, and SEO.
- Prepared health-ordered Docker deployment, Render infrastructure as code, secrets, and release/rollback/recovery procedures without claiming an unperformed deployment.

### Concise resume version

- Built a secure React/Express/Spring Boot/PostgreSQL task platform with JWT ownership, optimistic locking, conditional HTTP caching, generated OpenAPI types, Testcontainers, and OpenTelemetry.
- Load-tested 500 tasks with 20 concurrent clients and improved local throughput 41% while reducing p95 latency 47% through evidence-led telemetry optimization.
- Prepared Docker/Render infrastructure, CI container gates, and accessibility automation with 100 Lighthouse Accessibility and Best Practices scores.

## 21. Development and verification

Requirements: Node.js 20+, npm, Java 17, Maven 3.9+, and Docker Desktop.

Development:

```powershell
cd backend
docker compose up -d
mvn spring-boot:run

cd ../bff
npm ci
npm run dev

cd ../frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`.

Full verification order:

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

Backend tests run first because they export `backend/target/openapi.json` for the BFF contract check. When Spring runs, OpenAPI is at `/v3/api-docs`, Swagger UI at `/swagger-ui.html`, and readiness at `/actuator/health/readiness`.

## 22. Maintenance rules and known limitations

### Rules

- Keep browser HTTP in `frontend/src/features/tasks/api.ts`.
- Keep UI aggregation/adaptation in the BFF.
- Keep authorization, validation, and business rules in Spring services.
- Keep owner conditions in every task/category repository operation.
- Add migrations; never alter applied migration bytes.
- Regenerate—not manually edit—the BFF OpenAPI types.
- Never commit secrets, dependencies, caches, or build output.
- Add focused comments for security boundaries and non-obvious mapping/calculations, not syntax narration.
- Measure a performance problem before introducing infrastructure or complexity.

### Current limitations and future work

- The cloud environment is not yet deployed or smoke-tested.
- JWTs have no immediate server-side revocation and are held in browser storage.
- The BFF bootstrap fails as a whole if either upstream read fails.
- ETag generation still queries and serializes tasks before deciding `304`.
- The architecture has operational overhead for a single-user-scale task product.
- Mobile Lighthouse Performance was 67 under simulation; external fonts/icons and unused CSS/JavaScript remain candidates for measurement.
- Browser commit-time profiling for the indexed calendar should be repeated on controlled hardware.
- Cross-tab live updates via SSE/WebSockets should be added only if product need justifies persistent connections.
- Repeat load tests on stable hardware across multiple runs before making broader capacity claims.

Do not add Redis, Kafka, Kubernetes, another database, machine learning, Redux, or virtualization merely to expand the technology list. Each addition must solve a measured product or operational problem.

## Appendix A. Endpoint catalogue

Browser calls use the BFF `/api` origin; protected BFF routes forward to corresponding Spring `/api` routes unless noted.

| Method and path | Auth | Success | Purpose |
| --- | :---: | --- | --- |
| `POST /api/auth/register` | No | `201` | Create a user and return JWT/display identity. |
| `POST /api/auth/login` | No | `200` | Verify credentials and return JWT/display identity. |
| `GET /api/bootstrap` | Yes | `200` | BFF-only parallel aggregation of tasks and categories. |
| `GET /api/tasks` | Yes | `200`/`304` | List owner's tasks with private conditional caching. |
| `GET /api/tasks/{id}` | Yes | `200` | Read one owner-scoped task (Spring route; BFF proxy supports it). |
| `POST /api/tasks` | Yes | `201` | Create a task. |
| `PUT /api/tasks/{id}` | Yes | `200` | Update task with client version; may return `409`. |
| `DELETE /api/tasks/{id}` | Yes | `204` | Delete an owned task. |
| `GET /api/categories` | Yes | `200` | List owner's categories. |
| `POST /api/categories` | Yes | `201` | Create a category. |
| `PUT /api/categories/{id}` | Yes | `200` | Update an owned category. |
| `DELETE /api/categories/{id}` | Yes | `204` | Delete category and clear task associations. |
| `GET /health` | No | `200`/`503` | BFF dependency-health summary. |
| `GET /actuator/health/readiness` | No | `200`/`503` | Spring readiness including database. |
| `GET /v3/api-docs` | No | `200` | Generated OpenAPI document. |
| `GET /swagger-ui.html` | No | `200` | Interactive API documentation entry. |

## Appendix B. Glossary

| Term | Toodle meaning |
| --- | --- |
| BFF | Browser-specific Express server between React and Spring. |
| Bootstrap | Combined initial task/category response produced by the BFF. |
| Owner scope | Restricting task/category queries to the authenticated user. |
| Optimistic lock | Version-based rejection of an update made from a stale copy. |
| ETag | Identifier/hash for one HTTP representation. |
| Conditional GET | Request carrying `If-None-Match` to ask whether cached data remains current. |
| Correlation ID | Request identifier carried across browser, BFF, Spring, errors, and logs. |
| Contract drift | Spring HTTP shape changes without its generated BFF consumer being updated. |
| DTO | Explicit request/response data type separating HTTP fields from persistence entities. |
| Flyway | Ordered database migration and schema-history tool. |
| Liveness | Whether the service process is alive. |
| Readiness | Whether the service and required dependencies can serve traffic now. |
| MDC | Logging context used by Spring to attach the correlation ID. |
| CSP | Browser Content Security Policy restricting allowed content origins/actions. |
| TLS termination | Edge platform handles HTTPS certificates/encryption before forwarding internally. |
| p95 | Latency below which 95% of measured requests completed. |
