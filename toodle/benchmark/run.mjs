// Reproducible HTTP benchmark for the production-style Toodle stack.
import { mkdir, writeFile } from 'node:fs/promises';
import { performance } from 'node:perf_hooks';

const baseUrl = process.env.BENCHMARK_URL ?? 'http://frontend/api';
const taskCount = Number(process.env.BENCHMARK_TASKS ?? 500);
const concurrency = Number(process.env.BENCHMARK_CONCURRENCY ?? 20);
const durationSeconds = Number(process.env.BENCHMARK_DURATION_SECONDS ?? 30);
const seedConcurrency = Number(process.env.BENCHMARK_SEED_CONCURRENCY ?? 20);
const runId = process.env.BENCHMARK_RUN_ID ?? new Date().toISOString().replace(/\D/g, '').slice(0, 14);
const resultPath = process.env.BENCHMARK_RESULT ?? '/benchmark/results/latest.json';

function percentile(sorted, value) {
  if (!sorted.length) return 0;
  return sorted[Math.min(sorted.length - 1, Math.ceil(value * sorted.length) - 1)];
}

async function api(path, options = {}, token) {
  const started = performance.now();
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Correlation-Id': `benchmark-${crypto.randomUUID()}`,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  const body = response.status === 204 ? undefined : await response.json().catch(() => undefined);
  const latencyMs = performance.now() - started;
  if (!response.ok) throw new Error(`${options.method ?? 'GET'} ${path} returned ${response.status}: ${JSON.stringify(body)}`);
  return { body, latencyMs };
}

async function inBatches(items, batchSize, operation) {
  for (let offset = 0; offset < items.length; offset += batchSize) {
    await Promise.all(items.slice(offset, offset + batchSize).map(operation));
  }
}

const session = (await api('/auth/register', {
  method: 'POST',
  body: JSON.stringify({ name: 'Benchmark User', email: `benchmark-${runId}@toodle.local`, password: 'benchmark-password-2026' }),
})).body;

const colors = ['0', '1', '2', '3', '4', '5', '6', '7'];
const categories = [];
for (let index = 0; index < colors.length; index += 1) {
  categories.push((await api('/categories', {
    method: 'POST',
    body: JSON.stringify({ name: `Benchmark ${index + 1}`, color: colors[index] }),
  }, session.token)).body);
}

const tasks = Array.from({ length: taskCount }, (_, index) => ({
  title: `Benchmark task ${String(index + 1).padStart(5, '0')}`,
  description: `Deterministic seeded task for performance run ${runId}`,
  startDate: `2026-09-${String((index % 28) + 1).padStart(2, '0')}`,
  startTime: `${String(8 + (index % 9)).padStart(2, '0')}:00:00`,
  dueDate: `2026-09-${String((index % 28) + 1).padStart(2, '0')}`,
  dueTime: `${String(8 + (index % 9)).padStart(2, '0')}:30:00`,
  priority: ['LOW', 'MEDIUM', 'HIGH'][index % 3],
  categoryId: categories[index % categories.length].id,
  completed: index % 5 === 0,
}));

const seedStarted = performance.now();
await inBatches(tasks, seedConcurrency, (task) => api('/tasks', { method: 'POST', body: JSON.stringify(task) }, session.token));
const seedSeconds = (performance.now() - seedStarted) / 1000;

for (let index = 0; index < 10; index += 1) await api('/tasks', {}, session.token);

const measurements = [];
const deadline = performance.now() + durationSeconds * 1000;
async function worker(workerId) {
  let requestNumber = workerId;
  while (performance.now() < deadline) {
    const path = requestNumber % 5 === 0 ? '/bootstrap' : '/tasks';
    try {
      const result = await api(path, {}, session.token);
      measurements.push({ path, latencyMs: result.latencyMs, ok: true });
    } catch {
      measurements.push({ path, latencyMs: 0, ok: false });
    }
    requestNumber += concurrency;
  }
}

const measuredStarted = performance.now();
await Promise.all(Array.from({ length: concurrency }, (_, index) => worker(index)));
const measuredSeconds = (performance.now() - measuredStarted) / 1000;

function summarize(items) {
  const successful = items.filter((item) => item.ok);
  const latencies = successful.map((item) => item.latencyMs).sort((a, b) => a - b);
  return {
    requests: items.length,
    successful: successful.length,
    failed: items.length - successful.length,
    requestsPerSecond: Number((successful.length / measuredSeconds).toFixed(2)),
    latencyMs: {
      min: Number((latencies[0] ?? 0).toFixed(2)),
      p50: Number(percentile(latencies, 0.50).toFixed(2)),
      p95: Number(percentile(latencies, 0.95).toFixed(2)),
      p99: Number(percentile(latencies, 0.99).toFixed(2)),
      max: Number((latencies.at(-1) ?? 0).toFixed(2)),
    },
  };
}

const result = {
  generatedAt: new Date().toISOString(),
  configuration: { baseUrl, taskCount, concurrency, durationSeconds, seedConcurrency },
  seed: { tasks: taskCount, categories: categories.length, seconds: Number(seedSeconds.toFixed(2)) },
  overall: summarize(measurements),
  paths: Object.fromEntries(['/tasks', '/bootstrap'].map((path) => [path, summarize(measurements.filter((item) => item.path === path))])),
};

await mkdir(new URL('.', `file://${resultPath}`).pathname, { recursive: true });
await writeFile(resultPath, `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result, null, 2));
