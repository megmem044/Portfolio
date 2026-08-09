import { useState } from 'react'
import { logout, type User } from './api/auth'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

type AuthScreen = 'login' | 'register'

function App() {
  const [authScreen, setAuthScreen] = useState<AuthScreen>('login')
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  function handleAuthenticated(accessToken: string, authenticatedUser: User) {
    setToken(accessToken)
    setUser(authenticatedUser)
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
    }
  }

  if (token && user) {
    return (
      <DashboardPage
        email={user.email}
        isLoggingOut={isLoggingOut}
        onLogout={handleLogout}
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
