// Authentication form shown before the application shell.
import { useState } from 'react';
import { authApi, type AuthSession } from '../features/tasks/api';

interface AuthFormProps {
  onAuthenticated: (session: AuthSession) => void;
}

export function AuthForm({ onAuthenticated }: AuthFormProps) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string>();
  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const session = isRegistering ? await authApi.register(name, email, password) : await authApi.login(email, password);
      authApi.saveSession(session);
      onAuthenticated(session);
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'Unable to authenticate'); }
  };
  return <main className="app-container"><header className="app-header"><h1>Toodle</h1></header><div className="modal-overlay show"><form onSubmit={submit} className="modal" aria-label="Authentication form"><div className="modal-header"><h2>{isRegistering ? 'Create account' : 'Welcome back'}</h2></div><div className="modal-content">
    {isRegistering && <div className="form-group"><label htmlFor="name">Name</label><input id="name" value={name} onChange={(event) => setName(event.target.value)} required /></div>}
    <div className="form-group"><label htmlFor="email">Email</label><input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></div>
    <div className="form-group"><label htmlFor="password">Password</label><input id="password" type="password" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required /></div>
    {error && <p role="alert">{error}</p>}
    <div className="form-actions"><button className="btn btn-primary" type="submit">{isRegistering ? 'Create account' : 'Sign in'}</button></div>
    <button className="header-btn" type="button" onClick={() => { setIsRegistering((current) => !current); setError(undefined); }}>{isRegistering ? 'I already have an account' : 'Create account'}</button>
  </div></form></div></main>;
}
