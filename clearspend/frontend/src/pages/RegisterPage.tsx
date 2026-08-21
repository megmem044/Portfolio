import { useState, type FormEvent } from 'react'
import { register } from '../api/auth'
import './RegisterPage.css'

type RegisterPageProps = {
  onShowLogin: () => void
}

function RegisterPage({ onShowLogin }: RegisterPageProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirmation, setPasswordConfirmation] = useState('')
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (password.length < 8) {
      setMessage('Password must contain at least 8 characters.')
      return
    }

    if (password !== passwordConfirmation) {
      setMessage('The two passwords do not match.')
      return
    }

    setIsSubmitting(true)
    setMessage('')

    try {
      const user = await register(email, password)
      setMessage(`Account created successfully for ${user.email}.`)
      setPassword('')
      setPasswordConfirmation('')
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : 'Registration could not be completed.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-introduction">
        <p className="eyebrow">ClearSpend</p>
        <h1>Make your spending easier to understand.</h1>
        <p>
          Organize transactions, correct categories, and review monthly spending
          without maintaining a spreadsheet.
        </p>
      </section>

      <section className="auth-card" aria-labelledby="register-heading">
        <p className="eyebrow">Create an account</p>
        <h2 id="register-heading">Start tracking clearly</h2>
        <p className="auth-help">Use an email and a password with at least 8 characters.</p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            required
          />

          <label htmlFor="password-confirmation">Confirm password</label>
          <input
            id="password-confirmation"
            name="password-confirmation"
            type="password"
            autoComplete="new-password"
            value={passwordConfirmation}
            onChange={(event) => setPasswordConfirmation(event.target.value)}
            minLength={8}
            required
          />

          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        {message && <p className="form-message" role="status">{message}</p>}

        <p className="auth-switch">
          Already have an account?{' '}
          <button type="button" onClick={onShowLogin}>Sign in</button>
        </p>
      </section>
    </main>
  )
}

export default RegisterPage
