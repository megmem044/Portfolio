# MVP Relational Data Model

## Purpose

Defining how the platform’s data will be organized into related entities before creating physical SQL tables.

## Entity Inventory

### Fleet Operator

Representing an organization operating one or more EV fleets.

**Primary Key:** `fleet_operator_id`

### Fleet

Representing a group of electric vehicles managed by a fleet operator.

**Primary Key:** `fleet_id`

### Vehicle Model

Representing the manufacturer specifications shared by vehicles of the same model, such as battery capacity, range, and energy-consumption rating.

**Primary Key:** `vehicle_model_id`

### Vehicle

Representing an individual electric vehicle assigned to a fleet.

**Primary Key:** `vehicle_id`

### Trip

Representing a journey completed by a vehicle.

**Primary Key:** `trip_id`

### Charging Location

Representing a physical station where vehicles can be charged.

**Primary Key:** `charging_location_id`

### Charging Session

Representing an occasion when a vehicle is charged at a charging location.

**Primary Key:** `charging_session_id`

### Telemetry Reading

Representing a time-based sensor reading collected from a vehicle during operation.

**Primary Key:** `telemetry_reading_id`

### Operating Cost

Representing a charging, maintenance, repair, insurance, or other expense associated with a vehicle.

**Primary Key:** `operating_cost_id`

### EV Market Registration

Representing aggregated EV registration figures for a reporting period and Canadian geography.

**Primary Key:** `market_registration_id`
