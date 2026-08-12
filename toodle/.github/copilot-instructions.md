# Toodle contributor instructions

Toodle is being modernized from a browser-only prototype into a full-stack application.

## Active stack

- `frontend/`: React, TypeScript, and Vite
- `bff/`: Node.js and Express backend-for-frontend
- `backend/`: Java 17, Spring Boot, Spring Security, JPA, Flyway, and PostgreSQL
- `legacy/`: reference prototypes only; do not add active features here

Preserve the existing product behavior and visual design while improving architecture. Keep browser requests in the frontend API adapter, UI-specific aggregation in the BFF, business/authorization rules in Spring services, and persistence in repositories/Flyway migrations.

All task and category access must remain scoped to the authenticated owner. Do not commit secrets, dependencies, caches, or build output. Add focused comments for security boundaries, mapping logic, and non-obvious calendar calculations; avoid comments that restate syntax.

Before submitting changes, run the frontend and BFF TypeScript builds and the backend Maven tests described in the root README.
