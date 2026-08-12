// Backend-for-frontend: proxies the browser contract to the authenticated Spring API.
import cors from 'cors';
import express, { type Request, type Response } from 'express';
import { randomUUID } from 'node:crypto';

const app = express();
const port = Number(process.env.PORT ?? 3000);
const springApiUrl = process.env.SPRING_API_URL ?? 'http://127.0.0.1:8080/api';
const springHealthUrl = process.env.SPRING_HEALTH_URL ?? 'http://127.0.0.1:8080/actuator/health';
const frontendOrigins = process.env.FRONTEND_ORIGIN?.split(',').map((origin) => origin.trim()).filter(Boolean) ?? ['http://127.0.0.1:5173', 'http://localhost:5173'];

app.use(cors({ origin: frontendOrigins }));
app.use(express.json());
app.use((request, response, next) => {
  const correlationId = request.header('x-correlation-id') ?? randomUUID();
  response.setHeader('X-Correlation-Id', correlationId);
  response.on('finish', () => console.info(JSON.stringify({ correlationId, method: request.method, path: request.path, status: response.statusCode })));
  next();
});

function authorization(request: Request) {
  return request.header('authorization');
}

async function springRequest(path: string, request: Request, body?: unknown) {
  const headers = new Headers();
  const token = authorization(request);
  if (token) headers.set('Authorization', token);
  const correlationId = request.header('x-correlation-id');
  if (correlationId) headers.set('X-Correlation-Id', correlationId);
  if (body !== undefined) headers.set('Content-Type', 'application/json');
  return fetch(`${springApiUrl}${path}`, { method: request.method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
}

async function forward(response: Response, upstream: globalThis.Response) {
  const contentType = upstream.headers.get('content-type');
  if (contentType) response.setHeader('Content-Type', contentType);
  const payload = await upstream.text();
  response.status(upstream.status).send(payload);
}

function requireBearerToken(request: Request, response: Response) {
  if (authorization(request)?.startsWith('Bearer ')) return true;
  response.status(401).json({ message: 'Bearer authentication is required' });
  return false;
}

app.post('/api/auth/:action', async (request, response, next) => {
  const action = (request.params as { action?: string }).action;
  if (action !== 'login' && action !== 'register') return response.status(404).json({ message: 'Authentication endpoint not found' });
  try {
    await forward(response, await springRequest(`/auth/${action}`, request, request.body));
  } catch (error) { next(error); }
});

app.get('/health', async (_request, response) => {
  try {
    const upstream = await fetch(springHealthUrl);
    response.status(upstream.ok ? 200 : 503).json({ status: upstream.ok ? 'UP' : 'DOWN', upstream: await upstream.json() });
  } catch {
    response.status(503).json({ status: 'DOWN' });
  }
});

app.get('/api/bootstrap', async (request, response, next) => {
  if (!requireBearerToken(request, response)) return;
  try {
    const [tasksResponse, categoriesResponse] = await Promise.all([springRequest('/tasks', request), springRequest('/categories', request)]);
    if (!tasksResponse.ok) return forward(response, tasksResponse);
    if (!categoriesResponse.ok) return forward(response, categoriesResponse);
    response.json({ tasks: await tasksResponse.json(), categories: await categoriesResponse.json() });
  } catch (error) { next(error); }
});

app.all(['/api/tasks', '/api/tasks/:id'], async (request, response, next) => {
  if (!requireBearerToken(request, response)) return;
  const id = (request.params as { id?: string }).id;
  try {
    const taskPath = id ? `/tasks/${id}` : '/tasks';
    await forward(response, await springRequest(taskPath, request, ['POST', 'PUT'].includes(request.method) ? request.body : undefined));
  } catch (error) { next(error); }
});

app.all(['/api/categories', '/api/categories/:id'], async (request, response, next) => {
  if (!requireBearerToken(request, response)) return;
  const id = (request.params as { id?: string }).id;
  try {
    const categoryPath = id ? `/categories/${id}` : '/categories';
    await forward(response, await springRequest(categoryPath, request, ['POST', 'PUT'].includes(request.method) ? request.body : undefined));
  } catch (error) { next(error); }
});

app.use((error: unknown, _request: Request, response: Response, _next: express.NextFunction) => {
  console.error('BFF request failed', error);
  response.status(502).json({ message: 'Unable to reach the task service' });
});

app.listen(port, () => console.log(`Toodle BFF listening on http://127.0.0.1:${port}`));
