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
**Status:** Not Started

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
