// Typed client boundary for authentication and task/category requests sent through the Node BFF.
import type { Category, Task, TaskDraft } from './types';

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:3000/api';
const tokenKey = 'toodle_auth_token';

export interface AuthSession {
  token: string;
  name: string;
  email: string;
}

export interface BootstrapResponse {
  tasks: Task[];
  categories: Category[];
}

export class ApiRequestError extends Error {
  constructor(public readonly status: number, public readonly code: string | undefined, message: string, public readonly correlationId?: string) {
    super(correlationId ? `${message} (Request ID: ${correlationId})` : message);
    this.name = 'ApiRequestError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem(tokenKey);
  const correlationId = crypto.randomUUID();
  const response = await fetch(`${apiUrl}${path}`, { headers: { 'Content-Type': 'application/json', 'X-Correlation-Id': correlationId, ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options?.headers }, ...options });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ message: 'Request failed' }));
    // An invalid or expired token must not leave the client in a false signed-in state.
    if (response.status === 401 || response.status === 403) authApi.logout();
    throw new ApiRequestError(response.status, body.code, body.message ?? 'Request failed', response.headers.get('X-Correlation-Id') ?? correlationId);
  }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}

export const authApi = {
  login: (email: string, password: string) => request<AuthSession>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  register: (name: string, email: string, password: string) => request<AuthSession>('/auth/register', { method: 'POST', body: JSON.stringify({ name, email, password }) }),
  getSession: () => {
    const token = localStorage.getItem(tokenKey);
    const user = localStorage.getItem('currentUser');
    if (!token || !user) return null;
    try {
      return { token, ...JSON.parse(user) as Omit<AuthSession, 'token'> };
    } catch {
      // Clear partial/corrupt browser state rather than crashing during the first render.
      localStorage.removeItem(tokenKey);
      localStorage.removeItem('currentUser');
      return null;
    }
  },
  saveSession: (session: AuthSession) => {
    localStorage.setItem(tokenKey, session.token);
    localStorage.setItem('currentUser', JSON.stringify({ name: session.name, email: session.email }));
  },
  logout: () => { localStorage.removeItem(tokenKey); localStorage.removeItem('currentUser'); },
};

function taskRequest(task: Task | TaskDraft) {
  return {
    title: task.title,
    description: task.description,
    startDate: task.startDate || null,
    startTime: task.startTime || null,
    dueDate: task.dueDate || null,
    dueTime: task.dueTime || null,
    priority: task.priority.toUpperCase(),
    categoryId: task.categoryId,
    completed: 'isCompleted' in task ? task.isCompleted : false,
    ...('version' in task ? { version: task.version } : {}),
  };
}

export const taskApi = {
  list: () => request<Task[]>('/tasks'),
  create: (draft: TaskDraft) => request<Task>('/tasks', { method: 'POST', body: JSON.stringify(taskRequest(draft)) }),
  update: (task: Task) => request<Task>(`/tasks/${task.id}`, { method: 'PUT', body: JSON.stringify(taskRequest(task)) }),
  delete: (id: string) => request<void>(`/tasks/${id}`, { method: 'DELETE' }),
};

export const categoryApi = {
  list: () => request<Category[]>('/categories'),
  create: (name: string, color: string) => request<Category>('/categories', { method: 'POST', body: JSON.stringify({ name, color }) }),
  delete: (id: string) => request<void>(`/categories/${id}`, { method: 'DELETE' }),
};

export const bffApi = {
  bootstrap: () => request<BootstrapResponse>('/bootstrap'),
};
