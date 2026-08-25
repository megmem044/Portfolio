import { useState } from 'react'
import { logout, type User } from './api/auth'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import TransactionsPage from './pages/TransactionsPage'
import ImportPage from './pages/ImportPage'

type AuthScreen = 'login' | 'register'
type AuthenticatedScreen = 'overview' | 'transactions' | 'imports'

function App() {
  const [authScreen, setAuthScreen] = useState<AuthScreen>('login')
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [authenticatedScreen, setAuthenticatedScreen] =
    useState<AuthenticatedScreen>('overview')

  function handleAuthenticated(accessToken: string, authenticatedUser: User) {
    setToken(accessToken)
    setUser(authenticatedUser)
    setAuthenticatedScreen('overview')
  }

  async function handleLogout() {
    if (!token) return

    setIsLoggingOut(true)
    try {
      await logout(token)
    } finally {
      setToken(null)
      setUser(null)
      setIsLoggingOut(false)
      setAuthScreen('login')
      setAuthenticatedScreen('overview')
    }
  }

  if (token && user) {
    if (authenticatedScreen === 'transactions') {
      return (
        <TransactionsPage
          token={token}
          email={user.email}
          onBack={() => setAuthenticatedScreen('overview')}
        />
      )
    }
    if (authenticatedScreen === 'imports') {
      return <ImportPage token={token} email={user.email} onBack={() => setAuthenticatedScreen('overview')} />
    }

    return (
      <DashboardPage
        email={user.email}
        token={token}
        isLoggingOut={isLoggingOut}
        onLogout={handleLogout}
        onShowTransactions={() => setAuthenticatedScreen('transactions')}
        onShowImports={() => setAuthenticatedScreen('imports')}
      />
    )
  }

  if (authScreen === 'register') {
    return <RegisterPage onShowLogin={() => setAuthScreen('login')} />
  }

  return (
    <LoginPage
      onAuthenticated={handleAuthenticated}
      onShowRegister={() => setAuthScreen('register')}
    />
  )
}

export default App
