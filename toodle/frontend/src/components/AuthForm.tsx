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
  return <main className="auth-page">
    <section className="auth-story" aria-label="Toodle introduction">
      <div className="brand-lockup auth-brand"><span className="brand-mark" aria-hidden="true"><span /></span><h1>Toodle</h1></div>
      <div className="auth-shapes" aria-hidden="true"><span className="auth-star" /><span className="auth-arch" /><span className="auth-cloud" /><span className="auth-dot" /></div>
      <div className="auth-story-copy"><p className="welcome-eyebrow">A BRIGHTER WAY TO PLAN</p><h2>Make a little space for what matters.</h2><p>Tasks, time, and tiny wins—organized with less noise and more personality.</p></div>
    </section>
    <section className="auth-panel">
      <form onSubmit={submit} className="auth-form" aria-label="Authentication form">
        <div className="auth-heading"><p className="welcome-eyebrow">{isRegistering ? 'JOIN TOODLE' : 'WELCOME BACK'}</p><h2>{isRegistering ? 'Create your space' : 'Pick up where you left off'}</h2></div>
        {isRegistering && <div className="form-group"><label htmlFor="name">Name</label><input id="name" autoComplete="name" value={name} onChange={(event) => setName(event.target.value)} required /></div>}
        <div className="form-group"><label htmlFor="email">Email</label><input id="email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></div>
        <div className="form-group"><label htmlFor="password">Password</label><input id="password" type="password" autoComplete={isRegistering ? 'new-password' : 'current-password'} minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required /></div>
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="btn btn-primary auth-submit" type="submit">{isRegistering ? 'Create account' : 'Sign in'}</button>
        <p className="auth-switch-copy">{isRegistering ? 'Already have an account?' : 'New to Toodle?'} <button type="button" onClick={() => { setIsRegistering((current) => !current); setError(undefined); }}>{isRegistering ? 'Sign in' : 'Create an account'}</button></p>
      </form>
    </section>
  </main>;
}
