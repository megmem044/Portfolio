import type { Analytics, BenchmarkRun, Evaluation, EvaluationInput, EvaluationStatus, EvaluationSubmission, LoginResponse, ReviewItem } from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api/v1'
let accessToken = localStorage.getItem('answertrust_token') ?? ''

export function setAccessToken(token: string) { accessToken = token }

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}), ...options?.headers } })
  } catch {
    throw new Error('The AnswerTrust API is unavailable. Start FastAPI and try again.')
  }
  const body = await response.json()
  if (!response.ok) throw new Error(body.error?.message ?? 'The request could not be completed.')
  return body as T
}

export function login(email: string, password: string) {
  return request<LoginResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
}

export function createEvaluation(input: EvaluationInput) {
  return request<EvaluationSubmission>('/evaluations', { method: 'POST', body: JSON.stringify(input) })
}

export function getEvaluation(id: string) {
  return request<(Evaluation & { state: string }) | EvaluationStatus>(`/evaluations/${encodeURIComponent(id)}`)
}

export function getPendingReviews() { return request<ReviewItem[]>('/reviews/pending') }
export function submitReview(id: string, decision: 'APPROVE' | 'REJECT', notes: string) {
  return request(`/evaluations/${encodeURIComponent(id)}/review`, { method: 'POST', body: JSON.stringify({ decision, notes }) })
}
export function runPublicationBenchmark() { return request<BenchmarkRun>('/benchmarks/publication', { method: 'POST' }) }
export function getBenchmarkRuns() { return request<BenchmarkRun[]>('/benchmarks') }
export function getBenchmarkRun(id: string) { return request<BenchmarkRun>(`/benchmarks/${encodeURIComponent(id)}`) }
export function getAnalytics() { return request<Analytics>('/analytics') }
