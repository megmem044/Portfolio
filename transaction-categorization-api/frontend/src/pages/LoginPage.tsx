import { useState, type FormEvent } from 'react'
import { getCurrentUser, login, type User } from '../api/auth'
import './RegisterPage.css'

type LoginPageProps = {
  onAuthenticated: (token: string, user: User) => void
  onShowRegister: () => void
}

function LoginPage({ onAuthenticated, onShowRegister }: LoginPageProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsSubmitting(true)
    setMessage('')

    try {
      const tokenResponse = await login(email, password)
      const user = await getCurrentUser(tokenResponse.access_token)
      onAuthenticated(tokenResponse.access_token, user)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Login could not be completed.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-introduction">
        <p className="eyebrow">ClearSpend</p>
        <h1>Welcome back to a clearer view of your spending.</h1>
        <p>Sign in to review transactions, categories, rules, and monthly totals.</p>
      </section>

      <section className="auth-card" aria-labelledby="login-heading">
        <p className="eyebrow">Sign in</p>
        <h2 id="login-heading">Continue to your dashboard</h2>
        <p className="auth-help">Enter the email and password used for your account.</p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        {message && <p className="form-message" role="alert">{message}</p>}

        <p className="auth-switch">
          New to ClearSpend?{' '}
          <button type="button" onClick={onShowRegister}>Create an account</button>
        </p>
      </section>
    </main>
  )
}

export default LoginPage
