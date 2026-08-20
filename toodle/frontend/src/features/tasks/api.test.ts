import { afterEach, expect, test, vi } from 'vitest';
import { ApiRequestError, taskApi } from './api';

afterEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

test('sends a browser request ID with API calls', async () => {
  vi.spyOn(crypto, 'randomUUID').mockReturnValue('00000000-0000-4000-8000-000000000001');
  const fetchMock = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
    const requestHeaders = new Headers(init?.headers);
    expect(requestHeaders.get('X-Correlation-Id')).toBe('00000000-0000-4000-8000-000000000001');
    return Response.json([]);
  });
  vi.stubGlobal('fetch', fetchMock);

  await taskApi.list();

  expect(fetchMock).toHaveBeenCalledOnce();
});

test('includes the returned request ID in an API error', async () => {
  vi.spyOn(crypto, 'randomUUID').mockReturnValue('00000000-0000-4000-8000-000000000001');
  vi.stubGlobal('fetch', vi.fn(async () => Response.json(
    { code: 'SERVICE_UNAVAILABLE', message: 'Service is unavailable' },
    { status: 503, headers: { 'X-Correlation-Id': 'server-request-456' } },
  )));

  const error = await taskApi.list().catch((caught: unknown) => caught);

  expect(error).toBeInstanceOf(ApiRequestError);
  expect(error).toMatchObject({ status: 503, code: 'SERVICE_UNAVAILABLE', correlationId: 'server-request-456' });
  expect((error as Error).message).toContain('Request ID: server-request-456');
});
