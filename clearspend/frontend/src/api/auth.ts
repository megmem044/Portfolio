/** Send authentication requests to FastAPI and translate errors for the UI. */

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export type User = {
  id: number
  email: string
  is_active: boolean
  created_at: string
}

type AccessToken = {
  access_token: string
  token_type: 'bearer'
  expires_in: number
}

type FastApiError = {
  detail?: string | Array<{ msg: string }>
}

function errorMessage(error: FastApiError): string {
  if (typeof error.detail === 'string') {
    return error.detail
  }

  if (Array.isArray(error.detail) && error.detail.length > 0) {
    return error.detail[0].msg
  }

  return 'The request could not be completed.'
}

export async function register(email: string, password: string): Promise<User> {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    const error = (await response.json()) as FastApiError
    throw new Error(errorMessage(error))
  }

  return (await response.json()) as User
}

export async function login(email: string, password: string): Promise<AccessToken> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    const error = (await response.json()) as FastApiError
    throw new Error(errorMessage(error))
  }

  return (await response.json()) as AccessToken
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })

  if (!response.ok) {
    const error = (await response.json()) as FastApiError
    throw new Error(errorMessage(error))
  }

  return (await response.json()) as User
}

export async function logout(token: string): Promise<void> {
  const response = await fetch(`${API_URL}/auth/logout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })

  if (!response.ok) {
    const error = (await response.json()) as FastApiError
    throw new Error(errorMessage(error))
  }
}
