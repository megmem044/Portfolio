# Project Work Log

This log records the changes made during each project work session and the goal for the following session.

---

## Session 001 — 2026-08-04

### Files Changed

- `README.md` — Explaining the project vision, intended users, MVP scope, assumptions, and success outcomes.
- `docs/PROJECT_LOG.md` — Creating the project work log.
- `docs/PRODUCT_BACKLOG.md` — Adding and completing PB-001 and PB-002.
- `docs/DATA_REQUIREMENTS.md` — Defining the required data areas, fields, business questions, and source types.
- `docs/DATA_SOURCES.md` — Selecting public and synthetic data sources, documenting generation methods, and recording attribution requirements.

### Steps Implemented

- Defining the MVP data requirements.
- Identifying eight required data areas.
- Documenting important fields and business questions.
- Selecting public, synthetic, and combined data sources.
- Adding links to official public datasets.
- Documenting synthetic-data generation methods.
- Confirming portfolio-use and attribution requirements.
- Completing PB-001 and PB-002.

### Goal for Next Session

Creating the conceptual relational data model for the MVP.

---

## Session 002 — 2026-08-04

### Files Changed

- `docs/DATA_MODEL.md` — Defining entities, attributes, primary keys, foreign keys, relationships, cardinalities, market-data separation, and the entity-relationship diagram.
- `docs/PRODUCT_BACKLOG.md` — Adding and completing PB-003.
- `docs/PROJECT_LOG.md` — Recording the completed relational-modelling work.

### Steps Implemented

- Identifying the required relational entities.
- Defining primary keys and attributes.
- Adding the Charging Port entity.
- Defining foreign keys and entity relationships.
- Recording relationship cardinalities.
- Separating operational data from external market data.
- Creating the entity-relationship diagram.
- Completing PB-003.

### Goal for Next Session

Designing the physical SQL database schema.

---

## Session 003 — 2026-08-05

### Files Changed

- `docs/PRODUCT_BACKLOG.md` — Recording PB-004 as blocked and completing PB-005.
- `docs/LOCAL_SCHEMA_VALIDATION.md` — Documenting local validation and differences from Fabric Warehouse.
- `sql/01_create_tables.sql` — Completing the Microsoft Fabric Warehouse physical schema.
- `sql/02_create_local_validation_schema.sql` — Creating the SQLite-compatible validation schema.
- `scripts/validate_local_schema.py` — Automating local schema and constraint validation.
- `.gitignore` — Excluding generated Python cache files.
- `docs/PROJECT_LOG.md` — Recording the physical-schema and local-validation work.

### Steps Implemented

- Designing all 11 Fabric Warehouse tables.
- Defining physical data types, nullability, keys, and constraints.
- Recording Fabric capacity access as an external blocker.
- Creating an enforced SQLite version of the relational schema.
- Adding local data-quality constraints.
- Automating valid and invalid record tests.
- Validating all 11 tables and their relationships successfully.
- Completing PB-005.

### Goal for Next Session

Defining the Python data-generation and validation pipeline requirements.

---
