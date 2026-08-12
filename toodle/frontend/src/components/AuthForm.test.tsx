// Authentication UI contract tests verify login submission and failure feedback.
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthForm } from './AuthForm';
import { authApi } from '../features/tasks/api';

vi.mock('../features/tasks/api', () => ({ authApi: { login: vi.fn(), register: vi.fn(), saveSession: vi.fn() } }));

describe('AuthForm', () => {
  beforeEach(() => vi.clearAllMocks());

  it('logs in, stores the session, and notifies the shell', async () => {
    const user = userEvent.setup();
    const session = { token: 'token', name: 'Meg', email: 'meg@example.com' };
    vi.mocked(authApi.login).mockResolvedValue(session);
    const onAuthenticated = vi.fn();
    render(<AuthForm onAuthenticated={onAuthenticated} />);
    await user.type(screen.getByLabelText('Email'), session.email);
    await user.type(screen.getByLabelText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Sign in' }));
    expect(authApi.login).toHaveBeenCalledWith(session.email, 'password123');
    expect(authApi.saveSession).toHaveBeenCalledWith(session);
    expect(onAuthenticated).toHaveBeenCalledWith(session);
  });

  it('shows an accessible error when login fails', async () => {
    const user = userEvent.setup();
    vi.mocked(authApi.login).mockRejectedValue(new Error('Invalid credentials'));
    render(<AuthForm onAuthenticated={vi.fn()} />);
    await user.type(screen.getByLabelText('Email'), 'meg@example.com');
    await user.type(screen.getByLabelText('Password'), 'password123');
    await user.click(screen.getByRole('button', { name: 'Sign in' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Invalid credentials');
  });
});
