# Product Backlog

## PB-001 — Defining MVP Data Requirements

**Priority:** Must Have
**Status:** Completed

### User Story

As a data analyst, I want the required EV fleet and market data clearly defined so that I can design the database and data pipeline around real reporting needs.

### Acceptance Criteria (Specific criteria that must be met before the backlog item can be considered complete)

- The main data areas are identified, including:
  - Vehicles
  - Fleet operators
  - Trips
  - Charging sessions
  - Charging locations
  - Vehicle or battery telemetry
  - Operating costs
  - EV market data
- Each data area has a simple description.
- Important fields needed from each data area are listed.
- The source of each dataset is identified as public, synthetic, or not yet selected.
- The business questions each data area will help answer are documented.
- No database tables or pipeline code are created as part of this backlog item.

## PB-002 — Selecting MVP Data Sources

**Priority:** Must Have
**Status:** Completed

### User Story

As a data analyst, I want to select suitable data sources so that the platform can use accessible, relevant, and reliable EV fleet and market data.

### Acceptance Criteria

- Identifying a proposed source for every MVP data area
- Recording whether each source is public or synthetic
- Providing a link or generation method for each source
- Confirming that each source contains the required fields or suitable alternatives
- Recording the file format, such as CSV, JSON, or API response
- Confirming that the data can be used legally in a public portfolio project
- Documenting any missing data that will need to be generated synthetically
- Avoiding building data pipelines during this backlog item

## PB-003 — Designing the MVP Relational Data Model

**Priority:** Must Have  
**Status:** Completed

### User Story

As a data engineer, I want to design a relational data model so that fleet, vehicle, trip, charging, telemetry, cost, and market data can be stored consistently and connected for analysis.

### Acceptance Criteria

- Identifying the required entities from the approved data requirements
- Defining a primary key for every entity
- Defining the important attributes belonging to each entity
- Defining the relationships between entities
- Recording the expected one-to-one, one-to-many, or many-to-many relationships
- Identifying the foreign keys needed for connecting related entities
- Separating operational fleet data from external market data where appropriate
- Creating a readable entity-relationship diagram
- Documenting the design without creating physical SQL tables

## PB-004 — Designing the Physical SQL Schema

**Priority:** Must Have
**Status:** Blocked — Fabric capacity unavailable

### User Story

As a data engineer, I want to translate the approved relational data model into a physical SQL schema so that the platform has consistent and enforceable table structures.

### Acceptance Criteria

- Creating one SQL table definition for every approved entity
- Selecting Microsoft Fabric Warehouse-compatible data types
- Defining primary-key constraints
- Defining foreign-key relationships where supported
- Defining required and optional columns
- Adding appropriate uniqueness constraints
- Adding validation constraints where supported
- Following consistent table and column naming conventions
- Creating tables in the correct dependency order
- Documenting any Microsoft Fabric Warehouse limitations
- Keeping schema creation separate from data loading
- Validating the SQL script without loading project data


## PB-005 — Creating Local Schema Validation

**Priority:** Must Have
**Status:** Completed

### User Story

As a data engineer, I want to validate the relational schema locally so that table structures, keys, and relationships can be tested while Fabric capacity is unavailable.

### Acceptance Criteria

- Creating a SQLite-compatible version of the approved schema
- Creating all 11 entity tables
- Enabling foreign-key enforcement
- Preserving required and optional columns
- Preserving primary, foreign, and uniqueness constraints
- Documenting differences between SQLite and Fabric Warehouse
- Creating an automated Python validation script
- Confirming that all tables are created successfully
- Testing valid and invalid relationship records
- Avoiding loading production or external project data
