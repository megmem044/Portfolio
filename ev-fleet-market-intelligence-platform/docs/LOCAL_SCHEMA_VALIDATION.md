# Local Schema Validation

## Purpose

Validating the relational database design locally while Microsoft Fabric capacity is unavailable.

## Running the Validation

Running the following command from the project root:

```powershell
python scripts/validate_local_schema.py

```

A successful run should report:

```text
[PASS] Creating all expected tables
[PASS] Accepting valid related records
[PASS] Rejecting invalid records
[PASS] Local schema validation completed for 11 tables
```

## Validation Coverage

- Creating all 11 tables
- Enabling foreign-key enforcement
- Inserting valid related records
- Rejecting missing parent records
- Rejecting duplicate unique values
- Rejecting invalid reporting quarters
- Rejecting incorrectly sized VIN values
- Rejecting invalid trip timestamps
- Rejecting invalid battery percentages
- Rejecting negative costs

## Differences from Microsoft Fabric Warehouse

| Area | SQLite Validation | Fabric Warehouse |
|---|---|---|
| Database location | Running locally in memory | Running in Microsoft Fabric and OneLake |
| Table namespace | Using unqualified table names | Using the `dbo` schema |
| Key constraints | Enforcing primary, foreign and unique keys | Recording keys as `NOT ENFORCED` |
| Validation constraints | Enforcing `CHECK` constraints | Requiring equivalent Python pipeline validation |
| Data types | Using SQLite type affinity | Using Fabric Warehouse T-SQL data types |
| Date and time | Using `DATE` and `DATETIME` declarations | Using `DATE` and `DATETIME2(6)` |
| Constraint definitions | Defining constraints inside `CREATE TABLE` | Adding key constraints with `ALTER TABLE` |
| Database output | Creating no permanent database | Creating persistent Delta-backed Warehouse tables |

## Current Limitation

Local validation confirms the relational structure and data-quality rules, but it does not prove that the Fabric-specific script executes successfully. Fabric execution remains blocked until capacity access is available.