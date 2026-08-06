# EV Fleet and Market Intelligence Platform

A portfolio data platform for analyzing electric-vehicle fleet operations, charging behaviour, operating costs, vehicle performance, and Canadian EV market trends.

The project is designed around a Microsoft Fabric and Power BI target architecture. It currently includes the documented MVP requirements, selected data sources, an 11-entity relational model, a Fabric Warehouse schema, and an automated SQLite-based validation workflow.

## Project Goals

EV fleet data is commonly distributed across vehicle, trip, charging, telemetry, cost, and market systems. This project brings those domains into a consistent analytical model so users can answer questions such as:

- How intensively are fleet vehicles being used?
- How much energy do trips and charging sessions consume?
- Which vehicles, chargers, or locations show performance issues?
- What does it cost to operate the fleet?
- How do fleet results compare across vehicles, locations, and periods?
- How is the broader EV market changing?

## Intended Users

- Fleet managers monitoring vehicles and charging operations
- Operations teams investigating performance and data-quality issues
- Business leaders tracking cost and operational results
- Product teams studying vehicle and user behaviour
- Data analysts and engineers building reporting workflows

## MVP Architecture

```text
Public and synthetic data
          |
          v
Python ingestion and validation
          |
          v
Microsoft Fabric / OneLake
          |
          v
Fabric Warehouse relational model
          |
          v
Power BI semantic model and dashboards
```

The local SQLite workflow validates the relational design while Microsoft Fabric capacity is unavailable. It is a development-time substitute for structural testing, not the intended production platform.

## Data Model

The MVP schema contains 11 related entities covering:

- Fleet operators and fleets
- Vehicle models and individual vehicles
- Trips
- Charging locations, ports, and sessions
- Vehicle telemetry
- Operating costs
- EV market observations

The model separates internal fleet operations from external market data while retaining the keys required for fleet, vehicle, location, and time-based analysis. See [docs/DATA_MODEL.md](docs/DATA_MODEL.md) for entity definitions, relationships, cardinalities, and the entity-relationship diagram.

## Repository Structure

```text
.
|-- docs/
|   |-- DATA_MODEL.md
|   |-- DATA_REQUIREMENTS.md
|   |-- DATA_SOURCES.md
|   |-- LOCAL_SCHEMA_VALIDATION.md
|   |-- PRODUCT_BACKLOG.md
|   `-- PROJECT_LOG.md
|-- scripts/
|   `-- validate_local_schema.py
|-- sql/
|   |-- 01_create_tables.sql
|   `-- 02_create_local_validation_schema.sql
|-- .gitignore
`-- README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- No third-party Python packages are required for local schema validation

### Validate the Schema Locally

From the repository root, run:

```powershell
python scripts/validate_local_schema.py
```

A successful run reports:

```text
[PASS] Creating all expected tables
[PASS] Accepting valid related records
[PASS] Rejecting invalid records
[PASS] Local schema validation completed for 11 tables
```

The validation runs against an in-memory SQLite database and does not create a permanent local database file.

## SQL Implementations

- [`sql/01_create_tables.sql`](sql/01_create_tables.sql) defines the physical schema for Microsoft Fabric Warehouse.
- [`sql/02_create_local_validation_schema.sql`](sql/02_create_local_validation_schema.sql) provides an SQLite-compatible version with enforced relational and data-quality constraints.

The local implementation verifies table creation, valid related records, foreign keys, uniqueness, reporting periods, VIN length, timestamp order, battery percentages, and non-negative costs. Fabric-specific execution still needs to be tested in an active Fabric capacity.

## Documentation

| Document | Purpose |
|---|---|
| [Data requirements](docs/DATA_REQUIREMENTS.md) | Defines MVP data domains, required fields, and business questions |
| [Data sources](docs/DATA_SOURCES.md) | Records public sources, synthetic-data plans, formats, and attribution requirements |
| [Data model](docs/DATA_MODEL.md) | Describes entities, keys, relationships, cardinalities, and the ER diagram |
| [Local validation](docs/LOCAL_SCHEMA_VALIDATION.md) | Explains how to run validation and how SQLite differs from Fabric Warehouse |
| [Product backlog](docs/PRODUCT_BACKLOG.md) | Tracks user stories, priorities, acceptance criteria, and status |
| [Project log](docs/PROJECT_LOG.md) | Summarizes completed work sessions and next steps |

## Current Status

Completed:

- MVP data requirements
- Public and synthetic data-source strategy
- Conceptual relational data model
- Physical schema for 11 Fabric Warehouse tables
- SQLite-compatible local schema
- Automated positive and negative schema tests

Current limitation:

- Fabric-specific schema execution is blocked until Microsoft Fabric capacity is available.

Next planned work:

- Define the Python data-generation and validation pipeline requirements
- Generate representative synthetic fleet-operational data
- Build repeatable ingestion and data-quality checks
- Load validated data into Fabric when capacity becomes available
- Develop the Power BI semantic model and dashboards

## MVP Boundaries

The initial version uses public or synthetic data and scheduled batch processing. It does not include production vehicle connections, control of vehicles or charging stations, live route optimization, predictive maintenance, a public application, or a production-scale deployment.

## Success Criteria

The MVP will be considered successful when:

- Fleet, charging, telemetry, cost, and market data can be stored consistently
- Invalid data is detected before it reaches reporting layers
- The pipeline from source data to the analytical model is repeatable
- Power BI reports answer the documented fleet and market questions
- Architecture, assumptions, validation, and operating steps are clearly documented
