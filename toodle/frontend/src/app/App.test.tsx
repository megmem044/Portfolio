// Application conflict test verifies stale task updates refresh the visible server state.
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import { App } from './App';
import type { Task } from '../features/tasks/types';

function dateKey(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

const task = (title: string, version: number): Task => ({
  id: 'task-1',
  title,
  description: '',
  startDate: dateKey(new Date()),
  startTime: '',
  dueDate: dateKey(new Date()),
  dueTime: '',
  priority: 'medium',
  isCompleted: false,
  categoryId: null,
  categoryColor: null,
  createdAt: new Date().toISOString(),
  version,
});

beforeEach(() => {
  localStorage.setItem('toodle_auth_token', 'test-token');
  localStorage.setItem('currentUser', JSON.stringify({ name: 'Test User', email: 'test@example.com' }));
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.restoreAllMocks();
});

test('refreshes tasks and explains how to retry after a stale update', async () => {
  let bootstrapCalls = 0;
  vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith('/bootstrap')) {
      bootstrapCalls += 1;
      return Response.json({
        tasks: [bootstrapCalls === 1 ? task('Shared task', 0) : task('Updated elsewhere', 1)],
        categories: [],
      });
    }
    if (url.endsWith('/tasks/task-1') && init?.method === 'PUT') {
      return Response.json({ code: 'RESOURCE_CONFLICT', message: 'This task changed since you opened it.' }, { status: 409 });
    }
    throw new Error(`Unexpected request: ${url}`);
  }));

  render(<App />);
  await userEvent.click(await screen.findByRole('button', { name: 'Mark Shared task complete' }));

  expect(await screen.findByRole('alert')).toHaveTextContent('Your task list was refreshed. Reopen it and try again.');
  expect(await screen.findByText('Updated elsewhere')).toBeInTheDocument();
  expect(bootstrapCalls).toBe(2);
});
