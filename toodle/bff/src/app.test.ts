// BFF contract tests cover health, aggregation, forwarding, and upstream failures.
import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';
import type { AddressInfo } from 'node:net';
import type { Server } from 'node:http';
import { createApp } from './app.js';

const servers: Server[] = [];

afterEach(() => Promise.all(servers.splice(0).map((server) => new Promise<void>((resolve, reject) => server.close((error) => error ? reject(error) : resolve())))));

async function request(fetchFromUpstream: typeof fetch, path: string, init?: RequestInit) {
  const server = createApp({ fetch: fetchFromUpstream }).listen(0);
  servers.push(server);
  await new Promise<void>((resolve) => server.once('listening', resolve));
  const { port } = server.address() as AddressInfo;
  return fetch(`http://127.0.0.1:${port}${path}`, init);
}

test('health reports the Spring dependency state', async () => {
  const response = await request(async () => Response.json({ status: 'UP' }), '/health');
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { status: 'UP', upstream: { status: 'UP' } });
});

test('health returns 503 when Spring cannot be reached', async () => {
  const response = await request(async () => { throw new Error('offline'); }, '/health');
  assert.equal(response.status, 503);
  assert.deepEqual(await response.json(), { status: 'DOWN' });
});

test('bootstrap composes tasks and categories and forwards authentication', async () => {
  const calls: Array<{ url: string; authorization: string | null }> = [];
  const upstream: typeof fetch = async (input, init) => {
    const url = String(input);
    calls.push({ url, authorization: new Headers(init?.headers).get('authorization') });
    return Response.json(url.endsWith('/tasks') ? [{ id: 'task-1' }] : [{ id: 'category-1' }]);
  };
  const response = await request(upstream, '/api/bootstrap', { headers: { Authorization: 'Bearer test-token' } });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { tasks: [{ id: 'task-1' }], categories: [{ id: 'category-1' }] });
  assert.deepEqual(calls.map(({ authorization }) => authorization), ['Bearer test-token', 'Bearer test-token']);
});

test('generated correlation ID is returned and forwarded to Spring', async () => {
  let forwardedId: string | null = null;
  const upstream: typeof fetch = async (_input, init) => {
    forwardedId = new Headers(init?.headers).get('x-correlation-id');
    return Response.json([]);
  };
  const response = await request(upstream, '/api/tasks', { headers: { Authorization: 'Bearer test-token' } });
  assert.match(response.headers.get('x-correlation-id') ?? '', /^[0-9a-f-]{36}$/);
  assert.equal(forwardedId, response.headers.get('x-correlation-id'));
});

test('Spring error status and body pass through the BFF', async () => {
  const upstream: typeof fetch = async () => Response.json({ code: 'TASK_NOT_FOUND', message: 'Task not found' }, { status: 404 });
  const response = await request(upstream, '/api/tasks/missing', { headers: { Authorization: 'Bearer test-token' } });
  assert.equal(response.status, 404);
  assert.deepEqual(await response.json(), { code: 'TASK_NOT_FOUND', message: 'Task not found' });
});

test('network failures become a stable 502 response', async () => {
  const response = await request(async () => { throw new Error('offline'); }, '/api/tasks', { headers: { Authorization: 'Bearer test-token' } });
  assert.equal(response.status, 502);
  assert.deepEqual(await response.json(), { message: 'Unable to reach the task service' });
});
