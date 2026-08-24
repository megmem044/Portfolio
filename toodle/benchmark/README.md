# Local performance benchmark

_Last updated: August 23, 2026_

This benchmark runs against the production Docker stack. It creates a dedicated user, eight categories, and a deterministic task dataset through the public HTTP path. It then warms the application and measures a mix of task-list and bootstrap requests under concurrency.

## Run it

From the Toodle folder in PowerShell:

```powershell
$env:POSTGRES_PASSWORD="local-benchmark-password"
$env:JWT_SECRET="local-benchmark-jwt-secret-that-is-long-enough"
docker compose -f compose.production.yaml --profile benchmark run --rm benchmark
docker compose -f compose.production.yaml --profile benchmark run --rm benchmark-db-profile
```

The HTTP report is saved to `benchmark/results/latest.json`. The database command prints PostgreSQL planning time, execution time, buffer use, and whether the owner index was used.

## Recorded comparison

The checked-in [`baseline.json`](results/baseline.json) and [`optimized.json`](results/optimized.json) use the same 500-task, 20-client, 30-second workload. The optimization changed trace export from 100% console sampling to 10% parent-based sampling and disabled unused OTLP metrics/log exporters.

- Throughput: 8.61 to 12.16 requests/second, a 41.23% increase.
- Overall p95: 5,019 ms to 2,647 ms, a 47.27% reduction.
- Failures: zero before and after.
- Profiled PostgreSQL execution time: 3.07 ms for the 500-row owner-scoped join.

To reproduce the original telemetry-heavy mode, set `OTEL_TRACES_SAMPLER_ARG=1`, `OTEL_METRICS_EXPORTER=otlp`, and `OTEL_LOGS_EXPORTER=otlp` before recreating the services. The OTLP connection failures are part of that baseline and should not be used for normal development.

Defaults are 500 tasks, 20 concurrent clients, and 30 measured seconds. Override them when needed:

```powershell
$env:BENCHMARK_TASKS="1000"
$env:BENCHMARK_CONCURRENCY="40"
$env:BENCHMARK_DURATION_SECONDS="60"
docker compose -f compose.production.yaml --profile benchmark run --rm benchmark
```

Use the same task count, concurrency, duration, machine, and Docker resources for before/after comparisons. Run each version at least three times and compare the median p95 and throughput. Do not present a single local run as a universal production capacity claim.
